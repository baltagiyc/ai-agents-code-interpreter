# AI Agents Code Interpreter

A comprehensive project for building hierarchical AI agents capable of executing Python code and analyzing CSV files using LangChain and LangGraph.

## Project Overview

This repository demonstrates the evolution from classic LangChain AgentExecutor to modern LangGraph-based agents, with a focus on understanding agent architectures, state management, and advanced patterns.

## Project Structure

### `agents_basics/` - Classic LangChain Implementation

Implementation using **LangChain AgentExecutor** (classic approach) to understand:
- The **ReAct pattern** (Reasoning + Acting)
- How tools are invoked
- Limitations of this approach (limited control, difficult debugging)

**Key Features:**
- Router agent that delegates to specialized sub-agents (Python REPL and CSV analysis)
- Hierarchical agent architecture
- Tool wrapping and API adaptation

### `agents_advanced/` - Modern LangGraph Implementation

Modern refactoring with **LangGraph** for production-ready agents:

#### `langgraph_exploration/`
- **ReAct Agent**: Manual implementation of ReAct pattern with explicit state management
- **Research Agent**: Example with custom state tracking (search count, confidence scores, sources)
- Demonstrates core LangGraph concepts: State, Nodes, Edges, Conditional flows

#### `reflection_agent/`
- **Reflection Agent**: Two LLM "personalities" dialoguing to iteratively improve content
- Pattern: Generate → Critique → Improve → Critique → ...
- Uses `MessageGraph` state with conditional edges

#### `reflexion_agent/`
- **Reflexion Agent**: Learning from mistakes with persistent memory
- Pattern: Try → Evaluate → If failure: Analyze + Memorize → Retry with lessons learned
- Custom `ReflexionState` with reflection memory
- Implements self-reflection and memory storage for iterative improvement

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai-agents-code-interpreter

# Install dependencies with uv (recommended)
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Configuration

Create a `.env` file at the root:

```env
OPENAI_API_KEY=sk-your-key-here

# Optional but recommended for debugging
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2-your-key-here
LANGCHAIN_PROJECT=ai-agents-code-interpreter
```

## Key Concepts Demonstrated

### State Management
- **MessagesState**: Pre-built state for simple message-based agents
- **Custom States**: TypedDict definitions for tracking complex workflows
- **State Reducers**: Using `Annotated` with `add_messages` for message accumulation

### Agent Patterns
- **ReAct**: Reasoning and Acting loop with tool execution
- **Reflection**: Iterative content improvement through critique
- **Reflexion**: Error-based learning with persistent memory
- **Hierarchical Routing**: Supervisor agent delegating to specialized agents

### LangGraph Architecture
- **Nodes**: Functions that transform state
- **Edges**: Unconditional and conditional transitions
- **State Graph**: Explicit control flow with state machine

## Recommended Learning Path

1. **`agents_basics/main.py`** - Understand classic AgentExecutor and hierarchical routing
2. **`agents_advanced/langgraph_exploration/main.py`** - Manual ReAct implementation
3. **`agents_advanced/langgraph_exploration/research_agent_example.py`** - Custom state example
4. **`agents_advanced/reflection_agent/main.py`** - Reflection pattern
5. **`agents_advanced/reflexion_agent/`** - Reflexion pattern with memory

## Usage

```bash
# Run basic router agent
uv run python agents_basics/main.py

# Run LangGraph ReAct agent
uv run python agents_advanced/langgraph_exploration/main.py

# Run research agent example
uv run python agents_advanced/langgraph_exploration/research_agent_example.py

# Run reflection agent
uv run python agents_advanced/reflection_agent/main.py
```

## Development

```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Run Jupyter notebook
uv run jupyter notebook
```

## Dependencies

- **Python 3.12+** required
- **uv**: Fast Python package manager and resolver
- **langchain**: Core framework for LLM applications
- **langgraph**: Stateful, multi-actor applications with LLMs
- **langchain-openai**: OpenAI integration
- **langchain-experimental**: Experimental tools and agents
- **ruff**: Fast Python linter and formatter

## Notes

- Uses `uv` for dependency management (modern, fast, Rust-based)
- `ruff` configured for linting and formatting
- All agents use environment variables for API keys (no hardcoded secrets)
- Graph visualizations generated with `draw_mermaid_png()` for debugging

## Architecture Highlights

### State Customization
The project demonstrates when to use:
- **MessagesState**: Simple message-based conversations
- **Custom States**: When tracking additional metadata (counters, scores, intermediate results)

### Tool Integration
- **Python REPL**: Execute arbitrary Python code
- **CSV Analysis**: Pandas-based data analysis
- **Tavily Search**: Web search capabilities
- **Custom Tools**: Structured tool creation with Pydantic schemas

### Structured Outputs
- **Pydantic Models**: Type-safe schemas for agent responses
- **with_structured_output()**: Direct Pydantic object generation
- **bind_tools()**: Function calling with tool invocation

## License

MIT
