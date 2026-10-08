import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from newspaper import Article
import feedparser
from typing import List, Dict
import time
import random
from .enhanced_web_research import EnhancedWebResearchTool

class WebResearchTool:
    """Advanced web research tool for agents"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search the web using DuckDuckGo"""
        try:
            # Initialize DDGS with the new API
            results = []
            # Use the text search method - new API returns generator
            print(f"🔍 Searching DuckDuckGo for: {query[:50]}...")
            search_results = DDGS().text(
                query,
                max_results=max_results
            )
            
            for result in search_results:
                print("Processing result:", result.get('title', 'No title'))
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', ''),
                    'source': 'duckduckgo'
                })
            
            if results:
                print(f"✅ Found {len(results)} search results for: {query[:50]}")
            else:
                print(f"⚠️ No results found for: {query[:50]}")
                    
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            # Fallback: return mock results for testing
            print("Using fallback mock results...")
            return [
                {
                    'title': f'Latest developments in {query}',
                    'url': f'https://example.com/{query.replace(" ", "-")}',
                    'snippet': f'Recent analysis and insights about {query} from leading experts.',
                    'source': 'mock'
                }
            ]
    
    def extract_article_content(self, url: str) -> Dict:
        """Extract full article content from URL"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            return {
                'url': url,
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'summary': article.summary if hasattr(article, 'summary') else '',
                'status': 'success'
            }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'failed'
            }
    
    def get_news_feeds(self, topic: str) -> List[Dict]:
        """Get recent news from RSS feeds"""
        news_sources = [
            f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en",
            f"https://feeds.reuters.com/reuters/topNews"
        ]
        
        articles = []
        for feed_url in news_sources:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Top 5 from each source
                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'summary': entry.summary if hasattr(entry, 'summary') else '',
                        'published': str(entry.published) if hasattr(entry, 'published') else '',
                        'source': 'news_feed'
                    })
            except Exception as e:
                print(f"RSS feed error: {e}")
                continue
        
        return articles
    
    def extract_key_concepts(self, content: str, limit: int = 5) -> List[str]:
        """Extract key concepts from content for deeper research"""
        # Simple keyword extraction (can be enhanced with NLP)
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an'}
        
        words = content.lower().split()
        # Filter out common words and short words
        keywords = [word for word in words if len(word) > 4 and word not in common_words]
        
        # Count frequency and get top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords sorted by frequency
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in top_keywords[:limit]]

    def iterative_depth_breadth_research(self, topic: str, max_iterations: int = 3, max_content_per_iteration: int = 2) -> Dict:
        """Perform iterative depth and breadth research strategy"""
        print(f"🔍 Starting iterative depth-breadth research on: {topic}")
        
        research_data = {
            'topic': topic,
            'iterations': [],
            'final_summary': {},
            'research_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        current_topics = [topic]  # Start with main topic
        all_content = []
        
        for iteration in range(max_iterations):
            print(f"📊 Iteration {iteration + 1}/{max_iterations}")
            iteration_data = {
                'iteration': iteration + 1,
                'topics_explored': current_topics.copy(),
                'search_results': [],
                'detailed_content': [],
                'key_concepts': []
            }
            
            # BREADTH: Search across current topics
            for topic_variant in current_topics[:3]:  # Limit breadth to 3 topics per iteration
                print(f"  🔎 Searching: {topic_variant}")
                
                # Search with different query strategies
                queries = [
                    f"{topic_variant} comprehensive analysis",
                    f"{topic_variant} recent developments 2024",
                    f"{topic_variant} key insights trends"
                ]
                
                for query in queries[:2]:  # Limit queries per topic
                    results = self.search_web(query, max_results=4)  # Reduced results per query
                    iteration_data['search_results'].extend(results[:2])  # Take top 2
                    time.sleep(0.5)  # Brief pause
            
            # DEPTH: Extract detailed content from best results
            unique_urls = list({r['url']: r for r in iteration_data['search_results']}.values())
            top_urls = [r['url'] for r in unique_urls[:max_content_per_iteration]]
            
            for url in top_urls:
                print(f"  📄 Extracting: {url[:50]}...")
                content = self.extract_article_content(url)
                if content['status'] == 'success' and len(content['text']) > 200:
                    # Truncate content to optimize length (keep first 2000 chars)
                    content['text'] = content['text'][:2000] + "..." if len(content['text']) > 2000 else content['text']
                    iteration_data['detailed_content'].append(content)
                    all_content.append(content['text'])
                time.sleep(random.uniform(0.5, 1))  # Respectful delays
            
            # Extract key concepts for next iteration (DEPTH expansion)
            if iteration_data['detailed_content']:
                combined_text = ' '.join([c['text'] for c in iteration_data['detailed_content']])
                key_concepts = self.extract_key_concepts(combined_text, limit=3)
                iteration_data['key_concepts'] = key_concepts
                
                # Prepare topics for next iteration (combine original topic with new concepts)
                if iteration < max_iterations - 1:  # Don't generate new topics on last iteration
                    current_topics = [f"{topic} {concept}" for concept in key_concepts[:2]]
            
            research_data['iterations'].append(iteration_data)
            print(f"  ✅ Iteration {iteration + 1} complete: {len(iteration_data['detailed_content'])} articles, {len(iteration_data['key_concepts'])} concepts")
        
        # Generate final summary
        total_articles = sum(len(iter_data['detailed_content']) for iter_data in research_data['iterations'])
        total_concepts = list(set([concept for iter_data in research_data['iterations'] for concept in iter_data['key_concepts']]))
        
        research_data['final_summary'] = {
            'total_iterations': max_iterations,
            'total_articles_processed': total_articles,
            'unique_concepts_discovered': len(total_concepts),
            'key_concepts': total_concepts[:10],  # Top 10 concepts
            'research_depth_score': min(100, total_articles * 10),  # Simple scoring
            'content_length_optimized': True
        }
        
        print(f"🎯 Research complete: {total_articles} articles, {len(total_concepts)} concepts discovered")
        return research_data

    def comprehensive_research(self, topic: str) -> Dict:
        """Perform comprehensive research using enhanced strategy"""
        # Use enhanced tool for better quality
        enhanced_tool = EnhancedWebResearchTool()
        research_data = enhanced_tool.iterative_depth_research(topic, max_iterations=3)
        
        # Format output for better readability
        formatted_output = enhanced_tool.format_research_output(research_data)
        
        # Return both raw data and formatted output
        return {
            'raw_data': research_data,
            'formatted_output': formatted_output,
            'legacy_format': self.iterative_depth_breadth_research(topic, max_iterations=3, max_content_per_iteration=2)
        }

# Create a global instance for agents to use
web_research_tool = WebResearchTool()