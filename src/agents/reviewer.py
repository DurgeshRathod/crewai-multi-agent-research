from crewai import Agent
from langchain_ollama import ChatOllama
from crewai.tools import BaseTool
import json
from typing import Dict, List

class QualityAssessmentTool(BaseTool):
    name: str = "quality_assessment"
    description: str = "Perform comprehensive quality assessment of content"
    
    def _run(self, content: str) -> str:
        """Perform comprehensive quality assessment of content"""
        
        # Content metrics
        word_count = len(content.split())
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Check for key elements
        has_title = content.strip().startswith('#') or any(line.isupper() for line in content.split('\n')[:3])
        has_headings = content.count('#') > 1
        has_bullet_points = '•' in content or '-' in content or any(line.strip().startswith(('*', '-', '1.')) for line in content.split('\n'))
        
        # Check content depth
        technical_terms = ['analysis', 'research', 'methodology', 'findings', 'conclusions', 
                          'implications', 'recommendations', 'strategy', 'framework']
        technical_score = sum(1 for term in technical_terms if term.lower() in content.lower())
        
        # Check for citations/sources
        citation_indicators = ['according to', 'research shows', 'study found', 'source:', 'ref:', 'http']
        has_sources = any(indicator in content.lower() for indicator in citation_indicators)
        
        # Check for actionable insights
        action_words = ['should', 'must', 'recommend', 'suggest', 'consider', 'implement']
        actionable_score = sum(1 for word in action_words if word.lower() in content.lower())
        
        # Overall quality score (0-100)
        quality_score = 0
        if word_count >= 1000: quality_score += 20
        if has_title: quality_score += 10  
        if has_headings: quality_score += 15
        if has_bullet_points: quality_score += 10
        if technical_score >= 3: quality_score += 20
        if has_sources: quality_score += 15
        if actionable_score >= 2: quality_score += 10
        
        result = f"# Quality Assessment Report\n\n"
        result += f"**Overall Quality Score:** {quality_score}/100\n\n"
        
        result += "## Content Metrics:\n"
        result += f"- **Word Count:** {word_count}\n"
        result += f"- **Paragraph Count:** {paragraph_count}\n"
        result += f"- **Technical Depth Score:** {technical_score}/10\n"
        result += f"- **Actionable Insights Score:** {actionable_score}/10\n\n"
        
        result += "## Structural Elements:\n"
        result += f"- **Has Clear Title:** {'✓' if has_title else '✗'}\n"
        result += f"- **Has Headings:** {'✓' if has_headings else '✗'}\n"
        result += f"- **Has Bullet Points:** {'✓' if has_bullet_points else '✗'}\n"
        result += f"- **Includes Sources:** {'✓' if has_sources else '✗'}\n\n"
        
        # Quality rating
        if quality_score >= 80:
            rating = "Excellent"
        elif quality_score >= 60:
            rating = "Good"
        elif quality_score >= 40:
            rating = "Fair"
        else:
            rating = "Needs Improvement"
        
        result += f"**Quality Rating:** {rating}\n"
        
        return result

class FactCheckTool(BaseTool):
    name: str = "fact_check_analysis"
    description: str = "Analyze content for potential fact-checking needs"
    
    def _run(self, content: str) -> str:
        """Analyze content for potential fact-checking needs"""
        
        # Look for claims that need verification
        claim_indicators = ['according to', 'research shows', 'studies indicate', 'data reveals',
                           'statistics show', 'experts believe', 'it is proven', 'evidence suggests']
        
        numerical_claims = []
        source_claims = []
        
        lines = content.split('\n')
        for line in lines:
            # Check for numerical claims
            if any(char.isdigit() for char in line) and any(indicator in line.lower() for indicator in claim_indicators):
                numerical_claims.append(line.strip())
            
            # Check for authority claims
            if any(indicator in line.lower() for indicator in claim_indicators):
                source_claims.append(line.strip())
        
        result = f"# Fact-Check Analysis\n\n"
        
        if numerical_claims:
            result += "## Claims Requiring Verification:\n"
            for i, claim in enumerate(numerical_claims[:5], 1):
                result += f"{i}. {claim}\n"
            result += "\n"
        
        if source_claims:
            result += "## Source-Based Claims:\n"
            for i, claim in enumerate(source_claims[:5], 1):
                result += f"{i}. {claim}\n"
            result += "\n"
        
        # Check for absolute statements
        absolute_words = ['always', 'never', 'all', 'none', 'every', 'completely', 'totally']
        absolute_statements = [line for line in lines if any(word in line.lower() for word in absolute_words)]
        
        if absolute_statements:
            result += "## Absolute Statements (May Need Qualification):\n"
            for i, statement in enumerate(absolute_statements[:3], 1):
                result += f"{i}. {statement.strip()}\n"
            result += "\n"
        
        result += "## Recommendations:\n"
        result += "- Verify all statistical claims with credible sources\n"
        result += "- Ensure expert quotes are properly attributed\n"
        result += "- Consider qualifying absolute statements\n"
        result += "- Add citations for all factual claims\n"
        
        return result

class ReviewChecklistTool(BaseTool):
    name: str = "final_review_checklist"
    description: str = "Generate a comprehensive final review checklist"
    
    def _run(self, content: str) -> str:
        """Generate a comprehensive final review checklist"""
        
        checklist_items = [
            ("Content Completeness", "Does content fully address the topic?"),
            ("Logical Flow", "Do ideas progress logically from introduction to conclusion?"),
            ("Engagement", "Will readers find the content engaging and valuable?"),
            ("Clarity", "Are complex concepts explained clearly?"),
            ("Evidence", "Are claims supported with credible evidence?"),
            ("Formatting", "Is content well-formatted with proper headings?"),
            ("Grammar", "Is content free of grammatical errors?"),
            ("Originality", "Does content offer unique insights or perspectives?"),
            ("Actionability", "Does content provide actionable takeaways?"),
            ("Professional Tone", "Is the tone appropriate for the intended audience?")
        ]
        
        result = f"# Final Review Checklist\n\n"
        result += "Please review each item and mark as complete:\n\n"
        
        for i, (category, description) in enumerate(checklist_items, 1):
            result += f"□ **{category}:** {description}\n"
        
        result += f"\n## Content Statistics:\n"
        result += f"- Word Count: {len(content.split())}\n"
        result += f"- Reading Time: ~{len(content.split()) // 200} minutes\n"
        result += f"- Paragraphs: {len([p for p in content.split('\\n\\n') if p.strip()])}\n"
        
        return result

def create_reviewer_agent():
    """Create the quality assurance reviewer agent"""
    return Agent(
        role="Quality Assurance Reviewer",
        goal="Conduct thorough quality reviews, fact-checking, and final approval of content",
        backstory="""You are a meticulous quality assurance specialist with extensive experience in 
        content review and fact-checking. You have a sharp eye for detail, strong analytical skills, 
        and deep understanding of content quality standards. You excel at identifying potential issues, 
        verifying claims, ensuring accuracy, and providing comprehensive final reviews before publication.""",
        verbose=True,
        allow_delegation=False,
        tools=[QualityAssessmentTool(), FactCheckTool(), ReviewChecklistTool()],
        llm=ChatOllama(model="ollama/openhermes:v2.5", temperature=0.1, base_url="http://localhost:11434")
    )