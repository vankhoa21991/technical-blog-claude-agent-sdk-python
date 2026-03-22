# Claude Agent SDK Python - Progressive Patterns Demo

This demo showcases progressive patterns for building production-ready AI agents with Claude Agent SDK Python.

## Project Overview

This interactive demo teaches four core patterns:
1. **Custom Tools** - Extend Claude with @tool decorator
2. **Hooks for Control** - Intercept agent behavior with PreToolUse/PostToolUse
3. **Permission Management** - Control tool access with tiers
4. **Advanced Sessions** - This demo: Multi-turn reasoning with skills and session persistence

## Quick Commands

```bash
# Run all patterns via interactive menu
python main.py

# Run Pattern 5 directly (this demo)
python patterns/05_deep_research.py

# Run tests
pytest patterns/test_deep_research.py -v
```

## Architecture

**Pattern 5 (Deep Research Agent):**
- **ClaudeSDKClient**: Automatic session management (continue/resume/fork)
- **Agent Loop**: Multi-turn reasoning without custom loops
- **settingSources**: Loads CLAUDE.md and skills from `.claude/skills/`
- **Web Search**: Built-in `web_search` tool for finding documentation
- **Effort Levels**: Controls reasoning depth (low/medium/high/max)

**Key Pattern:**
```python
from claude_agent_sdk import ClaudeSDKClient, query, ClaudeAgentOptions

client = ClaudeSDKClient()

# Agent creates session automatically
async for message in query(
    prompt="Research topic...",
    options=ClaudeAgentOptions(
        setting_sources=["project"],  # Loads CLAUDE.md + skills
        allowed_tools=["Skill", "Read", "Bash", "web_search"],
        effort="high"  # Deeper reasoning per turn
    )
):
    print(message)

# Continue same session
session_id = client.get_most_recent_session_id()
async for message in query(
    prompt="Deepen analysis...",
    options=ClaudeAgentOptions(session_id=session_id)
):
    print(message)
```

## Skills System

Skills are markdown files at `.claude/skills/<name>/SKILL.md` that provide domain expertise to the agent.

**Example Skill Structure:**
```markdown
---
name: research
description: Research methodology for deep analysis
---

# Research Methodology

## Phase 1: Information Gathering
- Search official documentation
- Find comparison guides
- Identify key differentiators

## Phase 2: Analysis
- Compare architecture patterns
- Evaluate use cases
- Assess trade-offs
```

The agent loads skills on-demand via the `Skill` tool when `setting_sources=["project"]` is enabled.

## Session Operations

**Continue**: Multiple `query()` calls with same `session_id`
- Context accumulates across turns
- Agent maintains conversation state

**Resume**: Load specific session by ID
- `client.get_session(session_id)`
- Useful for long-running research tasks

**Fork**: Create new session from existing
- `fork_from=session_id` in options
- Explore alternative directions without changing original

## Testing

Pattern 5 includes basic smoke test:
- Verifies demo script runs without errors
- Checks that skills load correctly
- Validates report generation

Run with: `pytest patterns/test_deep_research.py -v
