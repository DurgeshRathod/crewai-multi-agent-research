from crewai import Agent
from langchain_ollama import ChatOllama
from crewai.tools import BaseTool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.web_research import web_research_tool

class WebResearchTool(BaseTool):
    name: str = "web_research"
    description: str = "Perform comprehensive web research on a given topic"
    
    def _run(self, query: str) -> str:
        """Perform comprehensive web research on a given topic"""
        research_result = web_research_tool.comprehensive_research(query)
        
        # Use enhanced formatted output if available
        if 'formatted_output' in research_result:
            return research_result['formatted_output']
        
        # Fallback to legacy format
        research_data = research_result.get('legacy_format', research_result)
        
        # Format the iterative research data into a readable string
        formatted_result = f"# Enhanced Research Report: {research_data.get('topic', query)}\n\n"
        
        # Add research strategy summary
        if 'final_summary' in research_data:
            summary = research_data['final_summary']
            formatted_result += "## Research Strategy Overview\n"
            formatted_result += f"- **Iterations Completed:** {summary.get('total_iterations', 'N/A')}\n"
            formatted_result += f"- **Articles Processed:** {summary.get('total_articles_processed', 'N/A')}\n"
            formatted_result += f"- **Concepts Discovered:** {summary.get('unique_concepts_discovered', 'N/A')}\n"
            formatted_result += f"- **Research Depth Score:** {summary.get('research_depth_score', 'N/A')}/100\n"
            formatted_result += f"- **Content Optimized:** {'✅' if summary.get('content_length_optimized') else '❌'}\n\n"
        
        # Add key concepts discovered
        if 'final_summary' in research_data and research_data['final_summary'].get('key_concepts'):
            formatted_result += "## Key Concepts Discovered\n"
            concepts = research_data['final_summary']['key_concepts'][:8]  # Show top 8
            for i, concept in enumerate(concepts, 1):
                formatted_result += f"{i}. **{concept.title()}**\n"
            formatted_result += "\n"
        
        # Add iteration details (condensed)
        if 'iterations' in research_data:
            formatted_result += "## Research Iterations\n"
            for iteration in research_data['iterations']:
                iter_num = iteration['iteration']
                topics = ', '.join(iteration['topics_explored'][:2])  # Show first 2 topics
                articles = len(iteration['detailed_content'])
                concepts = len(iteration['key_concepts'])
                
                formatted_result += f"### Iteration {iter_num}\n"
                formatted_result += f"- **Topics Explored:** {topics}\n"
                formatted_result += f"- **Articles Analyzed:** {articles}\n"
                formatted_result += f"- **New Concepts Found:** {concepts}\n"
                
                # Add top article from this iteration
                if iteration['detailed_content']:
                    top_article = iteration['detailed_content'][0]
                    formatted_result += f"- **Key Article:** {top_article.get('title', 'N/A')}\n"
                    if top_article.get('text'):
                        preview = top_article['text'][:300] + "..." if len(top_article['text']) > 300 else top_article['text']
                        formatted_result += f"  *Preview:* {preview}\n"
                formatted_result += "\n"
        
        # Add comprehensive content summary
        formatted_result += "## Comprehensive Research Insights\n"
        all_articles = []
        for iteration in research_data.get('iterations', []):
            all_articles.extend(iteration.get('detailed_content', []))
        
        if all_articles:
            formatted_result += f"**Total Sources Analyzed:** {len(all_articles)}\n"
            for i, article in enumerate(all_articles[:5], 1):  # Show top 5 articles
                formatted_result += f"{i}. **{article.get('title', 'Untitled')}**\n"
                formatted_result += f"   *Source:* {article.get('url', 'N/A')[:60]}...\n"
                if article.get('authors'):
                    formatted_result += f"   *Authors:* {', '.join(article['authors'][:2])}\n"
                formatted_result += "\n"
        
        formatted_result += f"**Research Strategy:** Iterative Depth-Breadth Analysis\n"
        formatted_result += f"**Research completed at:** {research_data['research_timestamp']}\n"
        formatted_result += f"**Optimization Status:** Content length optimized for comprehensive yet concise insights\n"
        
        return formatted_result

def create_researcher_agent():
    """Create the advanced researcher agent with internet capabilities"""
    return Agent(
        role="Senior Internet Research Analyst",
        goal="Conduct deep, comprehensive internet research and gather real-time information on any given topic",
        backstory="""You are an elite research analyst with advanced internet research capabilities. 
        You can search the web, extract content from articles, analyze news feeds, and synthesize 
        information from multiple online sources. You excel at finding the most current and relevant 
        information, verifying sources, and presenting comprehensive research findings in a structured format.""",
        verbose=True,
        allow_delegation=False,
        tools=[WebResearchTool()],
        llm=ChatOllama(model="ollama/openhermes:v2.5", temperature=0.1, base_url="http://localhost:11434")
    )