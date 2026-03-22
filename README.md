# Claude Agent SDK Python - Technical Blog Demo

Progressive demo showcasing Claude Agent SDK Python patterns:
- **Pattern 1: Custom Tools** - Extend Claude with Python functions
- **Pattern 2: Hooks for Control** - Intercept agent behavior
- **Pattern 3: Permission Management** - Control tool access
- **Pattern 4: Complete Agent** - All patterns combined
- **Pattern 5: Sessions** - Multi-turn reasoning with context

## Prerequisites

- Python 3.10+
- Claude Code CLI installed
- claude-agent-sdk: `pip install claude-agent-sdk`

## Project Structure

```
projects/technical-blog-claude-agent-sdk-python/
├── demo/
│   ├── main.py                    # Interactive menu system
│   ├── tools/                     # Custom tools
│   │   ├── calculator.py          # Calculator tool with @tool decorator
│   │   └── test_calculator.py     # Tool tests
│   ├── hooks/                     # Hook implementations
│   │   ├── command_blocker.py     # PreToolUse hook for security
│   │   ├── audit_logger.py        # PreToolUse/PostToolUse hook for logging
│   │   └── test_hooks.py          # Hook tests
│   ├── patterns/                  # Progressive demos
│   │   ├── 01_basic_tools.py      # Pattern 1: Custom tools
│   │   ├── 02_with_hooks.py       # Pattern 2: Add hooks
│   │   ├── 03_with_permissions.py # Pattern 3: Add permissions
│   │   ├── 04_complete_agent.py   # Pattern 4: All patterns
│   │   ├── 05_deep_research.py    # Pattern 5: Sessions & Skills
│   │   ├── test_permissions.py    # Permission tests
│   │   ├── test_complete_agent.py # Integration tests
│   │   └── test_deep_research.py  # Session tests
│   ├── tests/                     # Additional test utilities
│   ├── requirements.txt           # Python dependencies
│   ├── README.md                  # Demo-specific documentation
│   └── EXAMPLES.md                # Usage examples
├── blog/
│   ├── claude-code-building-blocks.md  # Full technical blog post
│   └── images/                    # Blog images and diagrams
└── README.md                      # This file
```

## Quick Start

### Installation

```bash
cd demo
pip install -r requirements.txt
```

### Running the Demo

```bash
python main.py
```

You'll see an interactive menu:

```
============================================================
Claude Agent SDK Python - Progressive Patterns
============================================================
1. Pattern 1: Custom Tools (Calculator)
2. Pattern 2: Add Hooks (Command Blocker)
3. Pattern 3: Add Permissions (Tiered Access)
4. Pattern 4: Complete Agent (All Patterns)
5. Pattern 5: Sessions (Multi-turn Research)
0. Exit
============================================================

Select pattern (0-5):
```

Select a pattern (1-5) to see it in action. Each pattern builds on the previous one.

## Pattern Overview

### Pattern 1: Custom Tools
Learn how to extend Claude's capabilities with custom tools using the `@tool` decorator. This pattern demonstrates:
- Creating custom tools with type hints
- Tool input validation
- Error handling
- Tool registration with the agent

**What You'll Learn:**
- Tools are just Python functions that Claude can call
- The `@tool` decorator handles registration automatically
- Claude figures out when to use tools
- You write normal Python, Claude handles the integration

**Key Code:**
```python
from claude_agent_sdk import tool

@tool
def calculator(operation: str, a: float, b: float) -> str:
    """Perform arithmetic operations."""
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }
    # Implementation...
```

### Pattern 2: Hooks for Control
Intercept agent behavior for security, validation, and audit logging. This pattern demonstrates:
- PreToolUse hooks: Validate/modify tool use before execution
- PostToolUse hooks: Capture results after execution
- Blocking dangerous operations
- Audit logging for compliance

**What You'll Learn:**
- Hooks are like middleware for tool calls
- They run before (PreToolUseHook) or after (PostToolUseHook) execution
- You can block, modify, or log tool calls
- Multiple hooks can run in sequence

**Key Code:**
```python
from claude_agent_sdk import PreToolUseHook, HookResult

class CommandBlockerHook(PreToolUseHook):
    """Block dangerous tools from executing."""

    BLOCKED_TOOLS = {"run_shell_command", "write_file", "delete_file"}

    async def before_tool_use(self, tool_name: str, input_data: dict) -> HookResult:
        if tool_name in self.BLOCKED_TOOLS:
            return HookResult(
                action="block",
                reason=f"Tool {tool_name} is blocked for security reasons"
            )
        return HookResult(action="allow")
```

### Pattern 3: Permission Management
Control tool access with tiered permissions (safe/semi-trusted/risky). This pattern demonstrates:
- `allowed_tools` whitelist
- `permission_mode` configuration
- Tiered permission levels
- Dynamic permission assignment

**What You'll Learn:**
- `allowed_tools` creates a whitelist of available tools
- `PermissionMode.STRICT` enforces boundaries
- `PermissionMode.PERMISSIVE` allows exploration
- Claude respects permissions automatically

**Key Code:**
```python
from claude_agent_sdk import Agent, PermissionMode

# Define tiers
SAFE_TOOLS = ["calculator", "text_analyzer"]
SEMI_TRUSTED_TOOLS = SAFE_TOOLS + ["read_file"]
RISKY_TOOLS = SEMI_TRUSTED_TOOLS + ["write_file", "run_shell_command"]

agent = Agent(
    allowed_tools=SAFE_TOOLS,
    permission_mode=PermissionMode.STRICT
)
```

### Pattern 4: Complete Agent
All patterns combined in a production-ready agent. This pattern demonstrates:
- Custom tools with validation
- Security hooks (command blocker, audit logger)
- Tiered permission management
- Comprehensive error handling
- Production best practices

**What You'll Learn:**
- Tools, hooks, and permissions layer without conflicts
- Security and observability are built-in
- This is how you build production agents
- All patterns work together seamlessly

**Key Code:**
```python
from claude_agent_sdk import Agent, PermissionMode
from tools.calculator import calculator
from hooks.command_blocker import CommandBlockerHook
from hooks.audit_logger import AuditLoggerHook

agent = Agent(
    tools=[calculator],
    hooks=[CommandBlockerHook(), AuditLoggerHook()],
    allowed_tools=["calculator"],
    permission_mode=PermissionMode.STRICT
)
```

### Pattern 5: Sessions
Multi-turn reasoning with context persistence. This pattern demonstrates:
- **ClaudeSDKClient** - Session management
- **connect()** - Must connect before querying
- **query()** - Send prompts with session_id
- **receive_messages()** - Stream Claude's responses
- **disconnect()** - Clean up connection

**What You'll Learn:**
- Sessions maintain conversation state across multiple turns
- `session_id` is just a string - you manage it yourself
- Same session ID = continues conversation (context preserved)
- Different session ID = fresh conversation
- Always call `await client.connect()` before querying

**Key Code:**
```python
from claude_agent_sdk import ClaudeSDKClient
import uuid

client = ClaudeSDKClient()
await client.connect()

# Create a unique session ID
session_id = f"research-{uuid.uuid4().hex[:8]}"

# Phase 1: Initial research
await client.query(
    prompt="Compare LangGraph, AutoGen, and Claude Agent SDK",
    session_id=session_id
)

async for message in client.receive_messages():
    print(message.content)

# Phase 2: Continue same session (context preserved!)
await client.query(
    prompt="Deepen analysis on architecture",
    session_id=session_id  # Same ID = continues conversation
)

async for message in client.receive_messages():
    print(message.content)

await client.disconnect()
```

**Session Management:**
- Session IDs are just strings—you manage them yourself
- Use descriptive names like `research-20250321-a3f2b1c9`
- Store session IDs in a database if you need to resume later
- Always call `await client.disconnect()` when done to free resources

## Testing

Each pattern includes comprehensive tests. Run tests from the demo directory:

```bash
# Test custom tools
python -m pytest tools/test_calculator.py -v

# Test hooks
python -m pytest hooks/test_hooks.py -v

# Test permissions
python -m pytest patterns/test_permissions.py -v

# Test complete agent
python -m pytest patterns/test_complete_agent.py -v

# Test sessions
python -m pytest patterns/test_deep_research.py -v

# Run all tests
python -m pytest -v
```

## Learning Path

**Progressive Learning:**
1. **Start with Pattern 1** to understand custom tools
2. **Add Pattern 2** to learn hooks for control
3. **Add Pattern 3** to understand permission management
4. **Review Pattern 4** to see all patterns working together
5. **Explore Pattern 5** for advanced multi-turn reasoning

Each pattern is self-contained and can be run independently via the menu system.

**What You'll Build:**
- Pattern 1: Extend Claude with your own Python functions
- Pattern 2: Add safety and logging with hooks
- Pattern 3: Control what Claude can access
- Pattern 4: Build a production-ready agent
- Pattern 5: Create agents that remember and learn

## Blog Post

See **[blog/claude-code-building-blocks.md](blog/claude-code-building-blocks.md)** for the full technical tutorial with detailed explanations, code walkthroughs, and production best practices.

The blog post covers:
- Why I built this demo (the learning problem)
- How each pattern works with live examples
- What I learned building it
- Common mistakes and how to avoid them
- Production-ready patterns

## Demo-Specific Documentation

For detailed setup instructions, API reference, and troubleshooting, see:
- **[demo/README.md](demo/README.md)** - Detailed demo documentation
- **[demo/EXAMPLES.md](demo/EXAMPLES.md)** - Practical usage examples

## Key Takeaways

**The Five Patterns:**

| Pattern | Capability | When to Use It |
|---------|-----------|---------------|
| **Custom Tools** | Extend Claude with Python functions | Need new capabilities |
| **Hooks** | Intercept and control behavior | Need safety, logging, validation |
| **Permissions** | Control what tools Claude can use | Need tiered access control |
| **Complete Agent** | All patterns combined | Building production agents |
| **Sessions & Skills** | Multi-turn reasoning with context | Complex, multi-step tasks |

**Production Mindset:**
- Always use `setting_sources=["project"]` for context
- Wrap tools in error handling
- Use hooks for security and observability
- Set appropriate permissions for your use case
- Monitor costs with effort levels

## License

MIT License - See LICENSE file for details.
