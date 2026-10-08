from crewai import Task

def create_writing_task(topic: str):
    """Create a writing task based on research findings"""
    return Task(
        description=f"""Using the research findings, write a comprehensive article about: {topic}
        
        Your article should:
        1. Have an engaging introduction that hooks the reader
        2. Be well-structured with clear sections and headings
        3. Present information in a logical flow
        4. Include relevant examples and case studies
        5. Have a compelling conclusion with key takeaways
        6. Be approximately 1000-1500 words
        
        The tone should be professional yet accessible to a general audience.""",
        expected_output="A well-written, engaging article of 1000-1500 words with proper structure and flow",
        agent=None  # Will be assigned when creating the crew
    )