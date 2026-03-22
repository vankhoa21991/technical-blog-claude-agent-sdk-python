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
- **ClaudeSDKClient**: Session management
- **connect()**: Must connect before querying
- **query()**: Send prompts with session_id parameter
- **receive_messages()**: Async generator that streams Claude's responses
- **disconnect()**: Clean up connection

**Key Pattern:**
```python
from claude_agent_sdk import ClaudeSDKClient
import uuid

client = ClaudeSDKClient()
await client.connect()

# Create a unique session ID
session_id = f"research-{uuid.uuid4().hex[:8]}"

# Phase 1: Initial research
await client.query(
    prompt="Research topic...",
    session_id=session_id
)

async for message in client.receive_messages():
    print(message.content)

# Phase 2: Continue same session (context preserved!)
await client.query(
    prompt="Deepen analysis...",
    session_id=session_id  # Same ID = continues conversation
)

async for message in client.receive_messages():
    print(message.content)

await client.disconnect()
```

## Session Management

**Session IDs**: You manage them yourself
- Session IDs are just strings (you create them)
- Use descriptive names like `research-20250321-a3f2b1c9`
- Same session ID = continues conversation (context preserved)
- Different session ID = fresh conversation (no context)

**Continue**: Multiple `query()` calls with same `session_id`
- Context accumulates across turns
- Agent maintains conversation state

**Resume**: Store session IDs for later use
- Save session IDs in a database or file
- Reuse the same session ID to resume conversations
- Useful for long-running research tasks

**Fork**: Create a new session ID for exploration
- Use a different session ID to explore alternatives
- Original session stays untouched
- Explore tangents without losing your main thread

## Testing

Pattern 5 includes basic smoke test:
- Verifies demo script runs without errors
- Checks that skills load correctly
- Validates report generation

Run with: `pytest patterns/test_deep_research.py -v
