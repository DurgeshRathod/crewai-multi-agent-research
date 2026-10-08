from crewai import Agent
from langchain_ollama import ChatOllama

def create_writer_agent():
    """Create the content writer agent"""
    return Agent(
        role="Content Writer",
        goal="Create engaging and well-structured content based on research findings",
        backstory="""You are a skilled content writer with expertise in transforming research 
        data into compelling narratives. You have a talent for making complex information 
        accessible and engaging for various audiences.""",
        verbose=True,
        allow_delegation=False,
        llm=ChatOllama(model="ollama/openhermes:v2.5", temperature=0.1, base_url="http://localhost:11434")
    )