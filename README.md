# Deep CrewAI Hierarchical Multi-Agent Project

An advanced CrewAI hierarchy multi-agent project featuring deep agents with internet research, content creation, editing, and quality review capabilities.

## Project Structure

```
crew-ai-conversational-bot/
├── src/
│   ├── agents/
│   │   ├── manager.py      # Project Manager agent (coordinates workflow)
│   │   ├── researcher.py   # Internet Research agent (web scraping, real-time data)
│   │   ├── creator.py      # Content Creator agent (structured content creation)
│   │   ├── editor.py       # Content Editor agent (refinement, readability)
│   │   └── reviewer.py     # Quality Reviewer agent (QA, fact-checking)
│   ├── tasks/
│   │   └── research_task.py    # All task definitions (research, create, edit, review)
│   ├── tools/
│   │   └── web_research.py     # Advanced web research capabilities
│   └── crew.py             # Deep hierarchical crew orchestration
├── main.py                 # Enhanced main execution script
├── pyproject.toml         # Poetry configuration with web research tools
├── .env                   # Environment variables
└── README.md
```

## Deep Agents

### 🎯 Manager Agent (Hierarchical Leader)
- **Role**: Project Manager & Workflow Coordinator
- **Responsibility**: Orchestrates the entire workflow from research to final review
- **Capabilities**: Delegates tasks, monitors progress, ensures quality standards
- **Model**: Ollama phi3 (low temperature for consistency)

### 🌐 Internet Researcher Agent
- **Role**: Senior Internet Research Analyst
- **Responsibility**: Conducts deep web research with real-time data gathering
- **Capabilities**: 
  - Web search using DuckDuckGo
  - Article content extraction and analysis
  - News feed monitoring
  - Source verification and citation
- **Tools**: Web research, content extraction, news analysis
- **Output**: Comprehensive research reports with current data and sources

### 🎨 Content Creator Agent
- **Role**: Master Content Creator
- **Responsibility**: Creates structured, engaging, and professional content
- **Capabilities**:
  - Content structure planning and optimization
  - Multiple headline generation
  - SEO-aware content creation
  - Various content format support (articles, reports, blogs)
- **Tools**: Content structuring, headline generation
- **Output**: High-quality content (2000-2500 words) with proper structure

### ✍️ Content Editor Agent
- **Role**: Senior Content Editor
- **Responsibility**: Refines content for maximum clarity and engagement
- **Capabilities**:
  - Content structure analysis
  - Readability assessment and improvement
  - Style and flow optimization
  - Grammar and clarity enhancement
- **Tools**: Structure analysis, readability checking, improvement suggestions
- **Output**: Refined, polished content with analysis reports

### 🔍 Quality Reviewer Agent
- **Role**: Quality Assurance Specialist
- **Responsibility**: Final quality control and fact-checking
- **Capabilities**:
  - Comprehensive quality assessment (scoring system)
  - Fact-checking and claim verification
  - Final review checklist validation
  - Publication readiness evaluation
- **Tools**: Quality assessment, fact-checking, review checklists
- **Output**: Complete QA reports with approval status

## Setup

1. **Install Ollama and pull phi3 model**:
   ```bash
   # Install Ollama (follow instructions at https://ollama.ai)
   ollama pull phi3
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Make sure Ollama is running**:
   ```bash
   ollama serve
   ```

4. **Run the project**:
   ```bash
   poetry run python main.py
   ```

## Deep Workflow

When you run the script, you'll enter a topic and the deep hierarchical crew will execute:

### 🔄 Complete Workflow: Research → Create → Edit → Review

1. **🎯 Manager** coordinates the entire project and assigns initial research task
2. **🌐 Internet Researcher** conducts deep web research:
   - Searches current information using DuckDuckGo
   - Extracts content from authoritative sources
   - Analyzes recent developments and trends
   - Compiles comprehensive research report with sources
3. **🎨 Content Creator** develops structured content:
   - Plans content structure and outline
   - Generates compelling headlines
   - Creates 2000-2500 word comprehensive content
   - Incorporates research findings and real-world examples
4. **✍️ Content Editor** refines the content:
   - Analyzes structure and organization
   - Assesses readability and clarity
   - Suggests specific improvements
   - Polishes content for maximum impact
5. **🔍 Quality Reviewer** performs final quality assurance:
   - Conducts comprehensive quality assessment with scoring
   - Performs fact-checking and claim verification
   - Validates content against publication standards
   - Provides final approval or improvement recommendations
6. **🎯 Manager** oversees each step and ensures quality delivery

### 📊 Output Features
- Real-time internet research with current data
- Professional content with proper structure
- Readability optimization and engagement metrics
- Comprehensive quality scoring (0-100 scale)
- Fact-checking analysis and source verification
- Final review checklist with publication readiness

## Configuration

- Modify agent roles and capabilities in `src/agents/`
- Customize task descriptions in `src/tasks/`
- Adjust crew configuration in `src/crew.py`
- Change default topics or make it fully interactive in `main.py`

## Requirements

- Python 3.9+
- Ollama with phi3 model
- Poetry for dependency management

## Notes

- Make sure Ollama is running before executing the crew
- The phi3 model will be used for all agents (manager, researcher, writer)
- Adjust model parameters in the agent files if needed