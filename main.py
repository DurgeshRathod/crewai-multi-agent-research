#!/usr/bin/env python3
"""
Deep CrewAI Hierarchy Multi-Agent Project
=========================================

This script demonstrates an advanced hierarchical multi-agent system using CrewAI with:
- Manager Agent: Coordinates the entire workflow
- Internet Researcher Agent: Conducts deep web research with real-time data
- Content Creator Agent: Creates structured, engaging content
- Editor Agent: Refines and improves content quality
- Quality Reviewer Agent: Performs final quality assurance and fact-checking

Features:
- Internet research with web scraping capabilities
- Content structure analysis and optimization
- Readability assessment and improvement suggestions
- Comprehensive quality assurance and fact-checking
- Hierarchical workflow: Research → Create → Edit → Review

Usage:
    python main.py
    
Requirements:
- Ollama running with phi3 model
- Internet connection for web research
"""

import sys
import os

# Suppress warnings before importing other modules
import suppress_warnings

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.crew import run_crew

def main():
    """Main entry point"""
    print("🚀 Deep CrewAI Sequential Multi-Agent Project")
    print("=" * 55)
    print("🤖 Agents: Internet Researcher | Creator | Editor | Reviewer")
    print("🔄 Workflow: Research → Create → Edit → Review → Final Output")
    print("=" * 55)
    
    # Check if Ollama is configured
    if not os.getenv("OLLAMA_BASE_URL"):
        print("❌ Error: OLLAMA_BASE_URL not found in environment variables.")
        print("Please make sure Ollama is running and configured in the .env file.")
        return
    
    print("\n🌐 Internet Research Capabilities: ✓ Enabled")
    print("📝 Content Creation & Editing: ✓ Enabled") 
    print("🔍 Quality Assurance & Review: ✓ Enabled")
    print("\n" + "-" * 55)
    
    # Interactive topic selection
    topic = input("\n📋 Enter a topic for deep research and content creation\n(or press Enter for default): ").strip()
    if not topic:
        topic = "Artificial Intelligence in Healthcare"
    
    print(f"\n🎯 Selected Topic: {topic}")
    print("\n⚡ Starting deep agent workflow...")
    
    try:
        result = run_crew(topic)
        print("\n🎉 Deep content creation project completed successfully!")
        print("\n📄 The agents have completed:")
        print("   ✅ Comprehensive internet research")
        print("   ✅ Professional content creation") 
        print("   ✅ Editorial refinement")
        print("   ✅ Quality assurance review")
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Ensure phi3 model is available: ollama pull phi3")
        print("3. Install dependencies: poetry install")
        print("4. Check internet connection for web research")

if __name__ == "__main__":
    main()