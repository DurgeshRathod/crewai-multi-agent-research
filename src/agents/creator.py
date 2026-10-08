from crewai import Agent
from langchain_ollama import ChatOllama
from crewai.tools import BaseTool
import json
import os

class ContentStructureTool(BaseTool):
    name: str = "create_content_structure"
    description: str = "Create a detailed content structure/outline for the given topic"
    
    def _run(self, topic: str, content_type: str = "article") -> str:
        """Create a detailed content structure/outline for the given topic"""
        structures = {
            "article": {
                "sections": [
                    "Introduction - Hook and context",
                    "Background - Historical perspective and current state",
                    "Key Concepts - Core ideas and definitions", 
                    "Current Trends - Latest developments and innovations",
                    "Challenges and Opportunities - Problems and potential solutions",
                    "Case Studies - Real-world examples and applications",
                    "Future Outlook - Predictions and implications",
                    "Conclusion - Summary and key takeaways"
                ],
                "word_count": "2000-2500 words",
                "tone": "Professional yet accessible"
            },
            "report": {
                "sections": [
                    "Executive Summary",
                    "Introduction and Scope",
                    "Methodology",
                    "Findings and Analysis", 
                    "Key Insights",
                    "Recommendations",
                    "Conclusion",
                    "References and Sources"
                ],
                "word_count": "3000-4000 words",
                "tone": "Formal and analytical"
            },
            "blog": {
                "sections": [
                    "Attention-grabbing headline",
                    "Engaging introduction with personal angle",
                    "Main content with subheadings",
                    "Practical tips or actionable insights",
                    "Conclusion with call-to-action"
                ],
                "word_count": "1200-1800 words", 
                "tone": "Conversational and engaging"
            }
        }
        
        structure = structures.get(content_type, structures["article"])
        
        result = f"# Content Structure for: {topic}\n\n"
        result += f"**Content Type:** {content_type.title()}\n"
        result += f"**Target Length:** {structure['word_count']}\n"
        result += f"**Tone:** {structure['tone']}\n\n"
        result += "## Recommended Structure:\n\n"
        
        for i, section in enumerate(structure['sections'], 1):
            result += f"{i}. {section}\n"
        
        result += f"\n**Note:** Adapt this structure based on research findings and specific requirements."
        
        return result

class HeadlineGeneratorTool(BaseTool):
    name: str = "generate_headlines"
    description: str = "Generate multiple headline options for content"
    
    def _run(self, topic: str, count: int = 10) -> str:
        """Generate multiple headline options for content"""
        headline_templates = [
            f"The Ultimate Guide to {topic}",
            f"How {topic} is Transforming [Industry/Field]", 
            f"10 Things You Need to Know About {topic}",
            f"{topic}: Everything You Need to Know in 2024",
            f"The Future of {topic}: Trends and Predictions",
            f"Understanding {topic}: A Comprehensive Analysis",
            f"Why {topic} Matters: Key Insights and Implications", 
            f"Breaking Down {topic}: Expert Analysis",
            f"{topic} Explained: From Basics to Advanced Concepts",
            f"The Complete {topic} Handbook"
        ]
        
        result = f"# Headline Options for: {topic}\n\n"
        for i, headline in enumerate(headline_templates[:count], 1):
            result += f"{i}. {headline}\n"
        
        result += "\n**Tip:** Choose headlines that match your target audience and content goals."
        
        return result

def create_creator_agent():
    """Create the content creator agent"""
    return Agent(
        role="Master Content Creator", 
        goal="Create compelling, well-structured, and engaging content based on comprehensive research",
        backstory="""You are a master content creator with expertise in crafting various types of content 
        including articles, reports, blog posts, and multimedia content. You excel at transforming complex 
        research into engaging narratives that resonate with target audiences. You understand content strategy, 
        SEO principles, and how to structure information for maximum impact and readability.""",
        verbose=True,
        allow_delegation=False,
        tools=[ContentStructureTool(), HeadlineGeneratorTool()],
        llm=ChatOllama(model="ollama/openhermes:v2.5", temperature=0.4, base_url="http://localhost:11434")
    )