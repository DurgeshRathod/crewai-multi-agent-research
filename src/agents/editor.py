from crewai import Agent
from langchain_ollama import ChatOllama
from crewai.tools import BaseTool
import re
from typing import Dict, List

class ContentStructureAnalyzer(BaseTool):
    name: str = "analyze_content_structure"
    description: str = "Analyze the structure and organization of content"
    
    def _run(self, content: str) -> str:
        """Analyze the structure and organization of content"""
        lines = content.split('\n')
        
        analysis = {
            'word_count': len(content.split()),
            'paragraph_count': len([line for line in lines if line.strip() and not line.startswith('#')]),
            'heading_count': len([line for line in lines if line.startswith('#')]),
            'has_introduction': any('introduction' in line.lower() for line in lines[:10]),
            'has_conclusion': any('conclusion' in line.lower() for line in lines[-10:]),
            'average_paragraph_length': 0
        }
        
        paragraphs = [line for line in lines if line.strip() and not line.startswith('#')]
        if paragraphs:
            analysis['average_paragraph_length'] = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
        
        result = f"# Content Structure Analysis\n\n"
        result += f"**Word Count:** {analysis['word_count']}\n"
        result += f"**Paragraph Count:** {analysis['paragraph_count']}\n"
        result += f"**Heading Count:** {analysis['heading_count']}\n"
        result += f"**Has Introduction:** {'Yes' if analysis['has_introduction'] else 'No'}\n"
        result += f"**Has Conclusion:** {'Yes' if analysis['has_conclusion'] else 'No'}\n"
        result += f"**Average Paragraph Length:** {analysis['average_paragraph_length']:.1f} words\n\n"
        
        # Recommendations
        result += "## Recommendations:\n"
        if analysis['word_count'] < 1000:
            result += "- Content may be too short for comprehensive coverage\n"
        if analysis['average_paragraph_length'] > 100:
            result += "- Consider breaking up long paragraphs for better readability\n"
        if not analysis['has_introduction']:
            result += "- Add a clear introduction to engage readers\n"
        if not analysis['has_conclusion']:
            result += "- Add a conclusion to summarize key points\n"
        if analysis['heading_count'] < 3:
            result += "- Add more headings to improve content organization\n"
        
        return result

class ReadabilityChecker(BaseTool):
    name: str = "check_readability"
    description: str = "Check content readability and suggest improvements"
    
    def _run(self, content: str) -> str:
        """Check content readability and suggest improvements"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = content.split()
        
        # Basic readability metrics
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        long_sentences = len([s for s in sentences if len(s.split()) > 25])
        
        # Check for passive voice (simplified)
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are', 'am']
        passive_count = sum(1 for word in words if word.lower() in passive_indicators)
        passive_percentage = (passive_count / len(words)) * 100 if words else 0
        
        # Check for transition words
        transitions = ['however', 'therefore', 'furthermore', 'moreover', 'additionally', 
                      'consequently', 'meanwhile', 'nevertheless', 'thus']
        transition_count = sum(1 for word in words if word.lower() in transitions)
        
        result = f"# Readability Analysis\n\n"
        result += f"**Average Sentence Length:** {avg_sentence_length:.1f} words\n"
        result += f"**Long Sentences (>25 words):** {long_sentences}\n"
        result += f"**Passive Voice Indicators:** {passive_percentage:.1f}%\n"
        result += f"**Transition Words:** {transition_count}\n\n"
        
        result += "## Readability Recommendations:\n"
        if avg_sentence_length > 20:
            result += "- Consider shortening sentences for better clarity\n"
        if long_sentences > 0:
            result += f"- Break up {long_sentences} overly long sentences\n"
        if passive_percentage > 10:
            result += "- Reduce passive voice for more engaging writing\n"
        if transition_count < 5:
            result += "- Add more transition words to improve flow\n"
        
        return result

class ImprovementSuggester(BaseTool):
    name: str = "suggest_improvements"
    description: str = "Suggest specific improvements for content quality"
    
    def _run(self, content: str) -> str:
        """Suggest specific improvements for content quality"""
        improvements = []
        
        # Check for common issues
        if content.count('very') > 3:
            improvements.append("Replace 'very' with more specific adjectives")
        
        if content.count('thing') > 2:
            improvements.append("Replace vague terms like 'thing' with specific nouns")
        
        # Check for repetition
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 5:  # Only check longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        repeated_words = [word for word, freq in word_freq.items() if freq > 5]
        if repeated_words:
            improvements.append(f"Reduce repetition of words: {', '.join(repeated_words[:3])}")
        
        # Check for engagement
        question_count = content.count('?')
        if question_count == 0:
            improvements.append("Add rhetorical questions to engage readers")
        
        # Check for examples
        example_indicators = ['for example', 'such as', 'like', 'including']
        has_examples = any(indicator in content.lower() for indicator in example_indicators)
        if not has_examples:
            improvements.append("Add concrete examples to illustrate key points")
        
        result = "# Content Improvement Suggestions\n\n"
        if improvements:
            for i, improvement in enumerate(improvements, 1):
                result += f"{i}. {improvement}\n"
        else:
            result += "Content quality looks good! No major improvements needed.\n"
        
        return result

def create_editor_agent():
    """Create the content editor agent"""
    return Agent(
        role="Senior Content Editor",
        goal="Refine, improve, and perfect content for clarity, engagement, and professional quality",
        backstory="""You are a seasoned content editor with years of experience in refining written content. 
        You have a keen eye for detail, understanding of content structure, and expertise in improving 
        readability and engagement. You excel at identifying areas for improvement, suggesting specific 
        edits, and ensuring content meets professional standards while maintaining the author's voice.""",
        verbose=True,
        allow_delegation=False,
        tools=[ContentStructureAnalyzer(), ReadabilityChecker(), ImprovementSuggester()],
        llm=ChatOllama(model="ollama/openhermes:v2.5", temperature=0.2, base_url="http://localhost:11434")
    )