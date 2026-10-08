from crewai import Agent
from langchain_ollama import ChatOllama

def create_manager_agent():
    """Create the manager agent for hierarchical crew"""
    return Agent(
        role="Project Manager",
        goal="Coordinate research and writing tasks, ensure quality deliverables",
        backstory="""You are an experienced project manager who oversees content creation projects. 
        You assign tasks to team members, review their work, and ensure deadlines are met with high-quality results.""",
        verbose=True,
        allow_delegation=True,
        llm=ChatOllama(model="ollama/openhermes:v2.5", temperature=0.1, base_url="http://localhost:11434")
    )