import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from newspaper import Article, ArticleException
import feedparser
from typing import List, Dict, Optional, Tuple
import time
import random
import json
from datetime import datetime
import re
from urllib.parse import urlparse, quote_plus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedWebResearchTool:
    """Enhanced web research tool with better quality output and error handling"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.search_cache = {}
        self.article_cache = {}
        
    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """Enhanced web search with multiple fallback strategies"""
        
        # Check cache first
        cache_key = f"{query}_{max_results}"
        if cache_key in self.search_cache:
            cached_time = self.search_cache[cache_key]['timestamp']
            if (datetime.now() - cached_time).seconds < 3600:  # 1 hour cache
                logger.info(f"Using cached search results for: {query}")
                return self.search_cache[cache_key]['results']
        
        results = []
        
        # Strategy 1: Try DuckDuckGo
        try:
            logger.info(f"Searching DuckDuckGo for: {query}")
            ddgs = DDGS()
            search_results = ddgs.text(query, max_results=max_results)
            
            for idx, result in enumerate(search_results):
                if isinstance(result, dict):
                    results.append({
                        'rank': idx + 1,
                        'title': result.get('title', 'No title'),
                        'url': result.get('href', result.get('link', '')),
                        'snippet': result.get('body', result.get('snippet', '')),
                        'source': 'duckduckgo',
                        'relevance_score': self._calculate_relevance(query, result)
                    })
                    
            logger.info(f"Found {len(results)} results from DuckDuckGo")
            
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            
        # Strategy 2: Try Google News RSS as fallback
        if len(results) < 3:
            try:
                logger.info("Falling back to Google News RSS")
                news_results = self._search_google_news(query, max_results)
                results.extend(news_results)
            except Exception as e:
                logger.warning(f"Google News search failed: {e}")
        
        # Strategy 3: Try Bing search scraping as last resort
        if len(results) < 3:
            try:
                logger.info("Falling back to Bing search scraping")
                bing_results = self._scrape_bing_search(query, max_results)
                results.extend(bing_results)
            except Exception as e:
                logger.warning(f"Bing search failed: {e}")
        
        # Remove duplicates and sort by relevance
        unique_results = self._deduplicate_results(results)
        sorted_results = sorted(unique_results, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Cache results
        self.search_cache[cache_key] = {
            'results': sorted_results[:max_results],
            'timestamp': datetime.now()
        }
        
        return sorted_results[:max_results]
    
    def _calculate_relevance(self, query: str, result: Dict) -> float:
        """Calculate relevance score for a search result"""
        score = 0.0
        query_terms = query.lower().split()
        
        title = result.get('title', '').lower()
        snippet = result.get('body', result.get('snippet', '')).lower()
        
        for term in query_terms:
            if term in title:
                score += 2.0  # Title matches are more important
            if term in snippet:
                score += 1.0
                
        # Boost recent results
        if '2024' in str(result.get('title', '')) or '2024' in str(result.get('body', '')):
            score += 1.5
        if '2025' in str(result.get('title', '')) or '2025' in str(result.get('body', '')):
            score += 2.0
            
        return score
    
    def _search_google_news(self, query: str, max_results: int) -> List[Dict]:
        """Search Google News RSS feed"""
        results = []
        encoded_query = quote_plus(query)
        feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(feed_url)
            for idx, entry in enumerate(feed.entries[:max_results]):
                results.append({
                    'rank': idx + 1,
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'snippet': BeautifulSoup(entry.get('summary', ''), 'html.parser').get_text()[:300],
                    'source': 'google_news',
                    'published': entry.get('published', ''),
                    'relevance_score': 0.8  # Default score for news
                })
        except Exception as e:
            logger.error(f"Google News RSS error: {e}")
            
        return results
    
    def _scrape_bing_search(self, query: str, max_results: int) -> List[Dict]:
        """Scrape Bing search results as fallback"""
        results = []
        encoded_query = quote_plus(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search results
            search_results = soup.find_all('li', class_='b_algo')[:max_results]
            
            for idx, result in enumerate(search_results):
                title_elem = result.find('h2')
                link_elem = result.find('a')
                snippet_elem = result.find('p')
                
                if title_elem and link_elem:
                    results.append({
                        'rank': idx + 1,
                        'title': title_elem.get_text(strip=True),
                        'url': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'source': 'bing',
                        'relevance_score': 0.7
                    })
        except Exception as e:
            logger.error(f"Bing scraping error: {e}")
            
        return results
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate URLs from results"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
                
        return unique_results
    
    def extract_article_content(self, url: str) -> Dict:
        """Enhanced article extraction with multiple strategies"""
        
        # Check cache
        if url in self.article_cache:
            logger.info(f"Using cached article: {url}")
            return self.article_cache[url]
        
        result = {
            'url': url,
            'title': '',
            'text': '',
            'authors': [],
            'publish_date': None,
            'summary': '',
            'key_points': [],
            'metadata': {},
            'status': 'failed'
        }
        
        # Strategy 1: Try newspaper3k
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()  # Natural language processing for summary
            
            result.update({
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'summary': article.summary,
                'key_points': self._extract_key_points(article.text),
                'metadata': {
                    'top_image': article.top_image,
                    'movies': article.movies,
                    'keywords': article.keywords[:10] if hasattr(article, 'keywords') else []
                },
                'status': 'success'
            })
            
            logger.info(f"Successfully extracted article using newspaper3k: {url}")
            
        except ArticleException as e:
            logger.warning(f"Newspaper extraction failed for {url}: {e}")
            
            # Strategy 2: Try BeautifulSoup scraping
            try:
                result = self._scrape_with_beautifulsoup(url)
                logger.info(f"Successfully extracted article using BeautifulSoup: {url}")
            except Exception as e2:
                logger.error(f"BeautifulSoup extraction also failed: {e2}")
                
        except Exception as e:
            logger.error(f"Article extraction error for {url}: {e}")
        
        # Cache the result
        self.article_cache[url] = result
        return result
    
    def _scrape_with_beautifulsoup(self, url: str) -> Dict:
        """Fallback scraping method using BeautifulSoup"""
        response = self.session.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "aside", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find article content
        article_content = None
        
        # Common article containers
        containers = [
            soup.find('article'),
            soup.find('main'),
            soup.find('div', class_=re.compile('content|article|post|entry')),
            soup.find('div', id=re.compile('content|article|post|entry'))
        ]
        
        for container in containers:
            if container:
                article_content = container
                break
        
        if not article_content:
            article_content = soup.find('body')
        
        # Extract text
        text = article_content.get_text(separator='\n', strip=True)
        
        # Clean text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        # Try to find title
        title = ''
        title_elem = soup.find('title') or soup.find('h1')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        return {
            'url': url,
            'title': title,
            'text': cleaned_text[:10000],  # Limit to 10000 chars
            'authors': [],
            'publish_date': None,
            'summary': self._generate_summary(cleaned_text),
            'key_points': self._extract_key_points(cleaned_text),
            'metadata': {},
            'status': 'success'
        }
    
    def _extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """Extract key points from text"""
        if not text:
            return []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Filter for important sentences
        key_sentences = []
        importance_keywords = ['important', 'key', 'critical', 'essential', 'significant', 
                              'major', 'primary', 'crucial', 'vital', 'main']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 50 and len(sentence) < 300:  # Good sentence length
                # Check for importance indicators
                lower_sentence = sentence.lower()
                if any(keyword in lower_sentence for keyword in importance_keywords):
                    key_sentences.append(sentence)
                elif sentence[0].isupper() and ':' in sentence:  # Likely a key point
                    key_sentences.append(sentence)
                elif re.match(r'^\d+\.', sentence):  # Numbered point
                    key_sentences.append(sentence)
        
        # If not enough key sentences, take first substantial sentences
        if len(key_sentences) < 3:
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 80 and sentence not in key_sentences:
                    key_sentences.append(sentence)
                if len(key_sentences) >= max_points:
                    break
        
        return key_sentences[:max_points]
    
    def _generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a simple summary of the text"""
        if not text:
            return ""
        
        # Take first few sentences
        sentences = re.split(r'[.!?]+', text)
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 30:  # Skip very short sentences
                summary_sentences.append(sentence)
                current_length += len(sentence)
                if current_length >= max_length:
                    break
        
        return '. '.join(summary_sentences[:3]) + '.'
    
    def iterative_depth_research(self, topic: str, max_iterations: int = 3) -> Dict:
        """Enhanced iterative research with better quality output"""
        logger.info(f"Starting enhanced research on: {topic}")
        
        research_data = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'iterations': [],
            'final_analysis': {},
            'quality_metrics': {}
        }
        
        all_articles = []
        all_concepts = set()
        current_queries = [topic]
        
        for iteration in range(max_iterations):
            logger.info(f"Research iteration {iteration + 1}/{max_iterations}")
            
            iteration_data = {
                'iteration': iteration + 1,
                'queries': current_queries,
                'search_results': [],
                'articles': [],
                'discovered_concepts': []
            }
            
            # Perform searches with varied queries
            for query in current_queries[:2]:  # Limit queries per iteration
                # Create query variations
                variations = [
                    query,
                    f"{query} latest news 2024",
                    f"{query} expert analysis",
                    f"{query} comprehensive guide"
                ]
                
                for variant in variations[:2]:
                    results = self.search_web(variant, max_results=5)
                    iteration_data['search_results'].extend(results)
                    time.sleep(random.uniform(0.5, 1.5))
            
            # Extract unique high-quality articles
            seen_urls = set()
            for result in sorted(iteration_data['search_results'], 
                               key=lambda x: x.get('relevance_score', 0), 
                               reverse=True)[:3]:
                
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    logger.info(f"Extracting content from: {url}")
                    
                    article = self.extract_article_content(url)
                    if article['status'] == 'success' and len(article['text']) > 500:
                        iteration_data['articles'].append({
                            'title': article['title'],
                            'url': article['url'],
                            'summary': article['summary'],
                            'key_points': article['key_points'],
                            'word_count': len(article['text'].split()),
                            'relevance_score': result.get('relevance_score', 0)
                        })
                        all_articles.append(article)
                        
                        # Extract concepts for next iteration
                        concepts = self._extract_advanced_concepts(article['text'])
                        iteration_data['discovered_concepts'].extend(concepts)
                        all_concepts.update(concepts)
                    
                    time.sleep(random.uniform(1, 2))
            
            # Prepare queries for next iteration
            if iteration < max_iterations - 1 and iteration_data['discovered_concepts']:
                # Combine topic with top concepts
                top_concepts = sorted(iteration_data['discovered_concepts'], 
                                    key=lambda x: len(x), 
                                    reverse=True)[:2]
                current_queries = [f"{topic} {concept}" for concept in top_concepts]
            
            research_data['iterations'].append(iteration_data)
        
        # Generate comprehensive final analysis
        research_data['final_analysis'] = self._generate_final_analysis(
            topic, all_articles, list(all_concepts)
        )
        
        # Calculate quality metrics
        research_data['quality_metrics'] = {
            'total_articles_analyzed': len(all_articles),
            'unique_sources': len(set(a['url'] for a in all_articles)),
            'total_concepts_discovered': len(all_concepts),
            'average_relevance_score': sum(a.get('relevance_score', 0) for iter_data in research_data['iterations'] 
                                          for a in iter_data['articles']) / max(1, len(all_articles)),
            'content_depth_score': min(100, len(all_articles) * 15),
            'research_quality': 'High' if len(all_articles) >= 5 else 'Medium' if len(all_articles) >= 3 else 'Low'
        }
        
        logger.info(f"Research completed: {len(all_articles)} articles analyzed")
        return research_data
    
    def _extract_advanced_concepts(self, text: str, limit: int = 5) -> List[str]:
        """Extract meaningful concepts using advanced techniques"""
        if not text:
            return []
        
        # Common stop words to filter out
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 
            'these', 'those', 'a', 'an', 'some', 'any', 'all', 'most', 'more', 'less',
            'very', 'much', 'many', 'few', 'also', 'just', 'only', 'still', 'even'
        }
        
        # Extract noun phrases and important terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter and count
        concept_freq = {}
        for word in words:
            if word not in stop_words and not word.isdigit():
                concept_freq[word] = concept_freq.get(word, 0) + 1
        
        # Look for multi-word concepts (bigrams)
        sentences = text.split('.')
        for sentence in sentences:
            # Find capitalized phrases (likely proper nouns or important concepts)
            capitalized = re.findall(r'[A-Z][a-z]+ [A-Z][a-z]+', sentence)
            for phrase in capitalized:
                concept_freq[phrase.lower()] = concept_freq.get(phrase.lower(), 0) + 2
        
        # Sort by frequency and importance
        sorted_concepts = sorted(concept_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top concepts
        return [concept for concept, freq in sorted_concepts[:limit] if freq > 2]
    
    def _generate_final_analysis(self, topic: str, articles: List[Dict], concepts: List[str]) -> Dict:
        """Generate comprehensive final analysis"""
        
        # Aggregate key points from all articles
        all_key_points = []
        for article in articles:
            if 'key_points' in article:
                all_key_points.extend(article['key_points'])
        
        # Deduplicate and limit key points
        unique_points = []
        seen = set()
        for point in all_key_points:
            point_lower = point.lower()
            if point_lower not in seen and len(point) > 20:
                seen.add(point_lower)
                unique_points.append(point)
        
        return {
            'topic': topic,
            'executive_summary': self._create_executive_summary(topic, articles),
            'key_insights': unique_points[:10],
            'top_concepts': concepts[:15],
            'source_diversity': {
                'total_sources': len(articles),
                'source_types': self._categorize_sources(articles),
                'date_range': self._get_date_range(articles)
            },
            'recommendations': self._generate_recommendations(topic, unique_points, concepts),
            'confidence_level': self._calculate_confidence(articles)
        }
    
    def _create_executive_summary(self, topic: str, articles: List[Dict]) -> str:
        """Create an executive summary from all articles"""
        if not articles:
            return f"Limited information available on {topic}."
        
        # Combine summaries from top articles
        summaries = [a.get('summary', '') for a in articles[:3] if a.get('summary')]
        
        if summaries:
            combined = ' '.join(summaries)
            # Limit to reasonable length
            words = combined.split()[:150]
            return ' '.join(words) + '...'
        else:
            return f"Research conducted on {topic} across {len(articles)} sources."
    
    def _categorize_sources(self, articles: List[Dict]) -> Dict[str, int]:
        """Categorize sources by type"""
        categories = {
            'news': 0,
            'academic': 0,
            'blog': 0,
            'official': 0,
            'other': 0
        }
        
        for article in articles:
            url = article.get('url', '').lower()
            if any(domain in url for domain in ['.edu', 'scholar', 'academic', 'journal']):
                categories['academic'] += 1
            elif any(domain in url for domain in ['news', 'reuters', 'bloomberg', 'cnn', 'bbc']):
                categories['news'] += 1
            elif any(domain in url for domain in ['.gov', '.org', 'official']):
                categories['official'] += 1
            elif any(domain in url for domain in ['blog', 'medium', 'wordpress']):
                categories['blog'] += 1
            else:
                categories['other'] += 1
        
        return categories
    
    def _get_date_range(self, articles: List[Dict]) -> str:
        """Get date range of articles"""
        dates = []
        for article in articles:
            if 'publish_date' in article and article['publish_date']:
                dates.append(article['publish_date'])
        
        if dates:
            return f"Sources from {min(dates)[:10]} to {max(dates)[:10]}"
        return "Date range not available"
    
    def _generate_recommendations(self, topic: str, key_points: List[str], concepts: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Basic recommendations based on research depth
        if len(key_points) >= 5:
            recommendations.append(f"Deep dive into specific aspects of {topic} for specialized insights")
        else:
            recommendations.append(f"Expand research scope on {topic} for comprehensive understanding")
        
        # Concept-based recommendations
        if concepts:
            top_concepts = concepts[:3]
            recommendations.append(f"Focus on key areas: {', '.join(top_concepts)}")
        
        # Add time-based recommendation
        recommendations.append("Monitor latest developments and emerging trends")
        
        return recommendations[:3]
    
    def _calculate_confidence(self, articles: List[Dict]) -> str:
        """Calculate confidence level based on sources"""
        if len(articles) >= 7:
            return "High"
        elif len(articles) >= 4:
            return "Medium"
        else:
            return "Low"
    
    def format_research_output(self, research_data: Dict) -> str:
        """Format research data into high-quality readable output"""
        output = []
        
        # Header
        output.append(f"# Research Report: {research_data['topic']}")
        output.append(f"Generated: {research_data['timestamp']}")
        output.append("")
        
        # Quality Metrics
        metrics = research_data.get('quality_metrics', {})
        output.append("## Research Quality Metrics")
        output.append(f"- **Articles Analyzed:** {metrics.get('total_articles_analyzed', 0)}")
        output.append(f"- **Unique Sources:** {metrics.get('unique_sources', 0)}")
        output.append(f"- **Concepts Discovered:** {metrics.get('total_concepts_discovered', 0)}")
        output.append(f"- **Research Quality:** {metrics.get('research_quality', 'Unknown')}")
        output.append(f"- **Confidence Level:** {research_data.get('final_analysis', {}).get('confidence_level', 'Unknown')}")
        output.append("")
        
        # Executive Summary
        analysis = research_data.get('final_analysis', {})
        if analysis.get('executive_summary'):
            output.append("## Executive Summary")
            output.append(analysis['executive_summary'])
            output.append("")
        
        # Key Insights
        if analysis.get('key_insights'):
            output.append("## Key Insights")
            for i, insight in enumerate(analysis['key_insights'][:7], 1):
                output.append(f"{i}. {insight}")
            output.append("")
        
        # Top Concepts
        if analysis.get('top_concepts'):
            output.append("## Important Concepts")
            output.append(", ".join(analysis['top_concepts'][:10]))
            output.append("")
        
        # Research Iterations Summary
        output.append("## Research Process")
        for iteration in research_data.get('iterations', []):
            output.append(f"\n### Iteration {iteration['iteration']}")
            output.append(f"- **Articles Processed:** {len(iteration.get('articles', []))}")
            
            # Show top articles from this iteration
            for article in iteration.get('articles', [])[:2]:
                output.append(f"  - {article['title']}")
                if article.get('summary'):
                    output.append(f"    Summary: {article['summary'][:200]}...")
        output.append("")
        
        # Recommendations
        if analysis.get('recommendations'):
            output.append("## Recommendations")
            for rec in analysis['recommendations']:
                output.append(f"- {rec}")
            output.append("")
        
        # Source Information
        if analysis.get('source_diversity'):
            output.append("## Source Analysis")
            diversity = analysis['source_diversity']
            output.append(f"- **Total Sources:** {diversity.get('total_sources', 0)}")
            output.append(f"- **Date Range:** {diversity.get('date_range', 'N/A')}")
            
            if diversity.get('source_types'):
                output.append("- **Source Types:**")
                for source_type, count in diversity['source_types'].items():
                    if count > 0:
                        output.append(f"  - {source_type.capitalize()}: {count}")
        
        return "\n".join(output)

# Create instance for backward compatibility
enhanced_web_research_tool = EnhancedWebResearchTool()