from crewai import Task

def create_research_task(topic: str):
    """Create an internet research task for comprehensive topic analysis"""
    return Task(
        description=f"""Conduct deep internet research on the topic: {topic}
        
        Use your web research capabilities to:
        1. Search for the latest information and developments
        2. Extract content from authoritative articles and sources
        3. Analyze current trends and statistics
        4. Identify key challenges and opportunities
        5. Gather expert opinions and notable quotes
        6. Find real-world examples and case studies
        
        Use the web_research tool to gather comprehensive, up-to-date information.
        Provide a well-structured research report with credible online sources.""",
        expected_output="A comprehensive internet research report with current data, trends, expert insights, and credible online sources",
        agent=None  # Will be assigned when creating the crew
    )

def create_creation_task(topic: str):
    """Create a content creation task based on research findings"""
    return Task(
        description=f"""Create high-quality content about: {topic}
        
        Based on the research findings, create comprehensive content that:
        1. Uses the create_content_structure tool to plan the content outline
        2. Generates compelling headlines using the generate_headlines tool
        3. Develops engaging, well-structured content
        4. Incorporates research findings and current data
        5. Includes real-world examples and case studies
        6. Maintains professional yet accessible tone
        7. Ensures content is 2000-2500 words for comprehensive coverage
        
        Focus on creating valuable, informative, and engaging content.""",
        expected_output="High-quality, comprehensive content (2000-2500 words) with proper structure, engaging headlines, and research-backed information",
        agent=None
    )

def create_editing_task():
    """Create a content editing and refinement task"""
    return Task(
        description="""Edit and refine the created content for maximum quality and impact.
        
        Use your editing tools to:
        1. Analyze content structure using analyze_content_structure tool
        2. Check readability and clarity with check_readability tool
        3. Identify specific improvements using suggest_improvements tool
        4. Refine content based on analysis results
        5. Ensure proper flow, transitions, and engagement
        6. Optimize for readability and professional quality
        7. Maintain the original message while improving presentation
        
        Provide both the analysis results and the final edited version.""",
        expected_output="Comprehensive editing analysis report plus the refined, improved version of the content",
        agent=None
    )

def create_review_task():
    """Create a quality assurance review task"""
    return Task(
        description="""Conduct final quality assurance review of the content.
        
        Perform comprehensive review using:
        1. Quality assessment using quality_assessment tool
        2. Fact-checking analysis with fact_check_analysis tool
        3. Final review checklist using final_review_checklist tool
        4. Verify all claims and ensure accuracy
        5. Check for completeness and professional standards
        6. Ensure content meets publication quality
        7. Provide final approval or recommendations for improvements
        
        Deliver a complete quality assurance report with final verdict.""",
        expected_output="Complete quality assurance report with assessment scores, fact-check analysis, review checklist, and final approval status",
        agent=None
    )