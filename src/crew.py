import os
from dotenv import load_dotenv
from crewai import Crew, Process
from agents.manager import create_manager_agent
from agents.researcher import create_researcher_agent
from agents.creator import create_creator_agent
from agents.editor import create_editor_agent
from agents.reviewer import create_reviewer_agent
from tasks.research_task import create_research_task, create_creation_task, create_editing_task, create_review_task

# Load environment variables
load_dotenv()

def create_deep_hierarchical_crew(topic: str):
    """Create a deep hierarchical crew with research, creation, editing, and review capabilities"""
    
    print("🚀 Initializing Deep Agent Hierarchy...")
    
    # Create agents
    manager = create_manager_agent()
    researcher = create_researcher_agent()
    creator = create_creator_agent()
    editor = create_editor_agent()
    reviewer = create_reviewer_agent()
    
    print("✅ Agents created: Researcher, Creator, Editor, Reviewer")
    
    # Create tasks for the complete workflow
    research_task = create_research_task(topic)
    creation_task = create_creation_task(topic)
    editing_task = create_editing_task()
    review_task = create_review_task()
    
    print("✅ Tasks defined: Research → Create → Edit → Review")
    
    # Assign agents to tasks
    research_task.agent = researcher
    creation_task.agent = creator
    editing_task.agent = editor
    review_task.agent = reviewer
    
    # Create crew with sequential process for proper execution
    crew = Crew(
        agents=[researcher, creator, editor, reviewer],  # Remove manager from agents list
        tasks=[research_task, creation_task, editing_task, review_task],
        process=Process.sequential,  # Sequential execution ensures each agent runs properly
        verbose=True
    )
    
    print("✅ Deep sequential crew assembled!")
    return crew

def run_deep_crew(topic: str = "Artificial Intelligence in Healthcare"):
    """Run the deep hierarchical crew with comprehensive workflow"""
    print(f"🎯 Starting deep content creation project on: {topic}")
    print("="*60)
    print("WORKFLOW: Research → Create → Edit → Review → Final Output")
    print("="*60)
    
    crew = create_deep_hierarchical_crew(topic)
    result = crew.kickoff()
    
    print("\n" + "="*60)
    print("🏆 FINAL PROJECT RESULT:")
    print("="*60)
    
    # Format the result properly
    if isinstance(result, str):
        # Replace literal \n with actual newlines
        formatted_result = result.replace('\\n', '\n')
        print(formatted_result)
    else:
        # If result is an object, try to get its string representation
        formatted_result = str(result).replace('\\n', '\n')
        print(formatted_result)
    
    return result

# Backward compatibility
def create_hierarchical_crew(topic: str):
    """Backward compatible function"""
    return create_deep_hierarchical_crew(topic)

def run_crew(topic: str = "Artificial Intelligence in Healthcare"):
    """Backward compatible function"""
    return run_deep_crew(topic)