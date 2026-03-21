# Claude Agent SDK Python - Technical Blog Demo

Progressive demo showcasing Claude Agent SDK Python patterns:
- **Pattern 1: Custom Tools** (in-process MCP servers)
- **Pattern 2: Hooks for Control** (PreToolUse, PostToolUse)
- **Pattern 3: Permission Management** (allowed_tools, permission_mode)
- **Pattern 4: Complete Agent** (all patterns combined)

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
│   │   ├── test_permissions.py    # Permission tests
│   │   └── test_complete_agent.py # Integration tests
│   ├── tests/                     # Additional test utilities
│   ├── requirements.txt           # Python dependencies
│   ├── README.md                  # Demo-specific documentation
│   └── EXAMPLES.md                # Usage examples
├── blog/
│   ├── post.md                    # Full technical blog post
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
0. Exit
============================================================

Select pattern (0-4):
```

Select a pattern (1-4) to see it in action. Each pattern builds on the previous one.

## Pattern Overview

### Pattern 1: Custom Tools
Learn how to extend Claude's capabilities with custom tools using the `@tool` decorator. This pattern demonstrates:
- Creating custom tools with type hints
- Tool input validation
- Error handling
- Tool registration with the agent

**Key Code:**
```python
from claude_agent_sdk import tool

@tool
def calculator(operation: str, a: float, b: float) -> str:
    """Perform basic arithmetic operations."""
    # Implementation
```

### Pattern 2: Hooks for Control
Intercept agent behavior for security, validation, and audit logging. This pattern demonstrates:
- PreToolUse hooks: Validate/modify tool use before execution
- PostToolUse hooks: Capture results after execution
- Blocking dangerous operations
- Audit logging for compliance

**Key Code:**
```python
from claude_agent_sdk import PreToolUseHook

class CommandBlockerHook(PreToolUseHook):
    async def on_pre_tool_use(self, tool_use):
        if tool_use.name in BLOCKED_TOOLS:
            raise ToolUseBlockedException(f"Tool {tool_use.name} is blocked")
```

### Pattern 3: Permission Management
Control tool access with tiered permissions (safe/semi-trusted/risky). This pattern demonstrates:
- `allowed_tools` whitelist
- `permission_mode` configuration
- Tiered permission levels
- Dynamic permission assignment

**Key Code:**
```python
from claude_agent_sdk import Agent, PermissionMode

agent = Agent(
    allowed_tools=["calculator", "text_analyzer"],
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

**Key Code:**
```python
agent = Agent(
    tools=[calculator, text_analyzer],
    hooks=[command_blocker, audit_logger],
    allowed_tools=SAFE_TOOLS,
    permission_mode=PermissionMode.STRICT
)
```

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

# Run all tests
python -m pytest -v
```

## Learning Path

1. **Start with Pattern 1** to understand custom tools
2. **Add Pattern 2** to learn hooks for control
3. **Add Pattern 3** to understand permission management
4. **Review Pattern 4** to see all patterns working together

Each pattern is self-contained and can be run independently via the menu system.

## Blog Post

See `blog/post.md` for the full technical tutorial with detailed explanations, code walkthroughs, and production best practices.

## Demo-Specific Documentation

For detailed setup instructions, API reference, and troubleshooting, see:
- **[demo/README.md](demo/README.md)** - Detailed demo documentation
- **[demo/EXAMPLES.md](demo/EXAMPLES.md)** - Practical usage examples

## License

MIT License - See LICENSE file for details.