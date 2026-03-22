# Claude Agent SDK Python - Interactive Demo

This directory contains an interactive, progressive demo of the Claude Agent SDK Python patterns. Each pattern builds on the previous one, demonstrating how to build production-ready AI agents with custom tools, hooks, and permissions.

## Table of Contents

- [Installation](#installation)
- [Running the Demo](#running-the-demo)
- [Pattern Details](#pattern-details)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify installation**:
```bash
python -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"
```

## Running the Demo

### Interactive Menu

Run the main demo script:

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
5. Pattern 5: Deep Research Agent (Sessions & Skills)
0. Exit
============================================================

Select pattern (0-5):
```

### Running Patterns Directly

You can also run individual patterns directly:

```bash
# Pattern 1: Custom Tools
python -m patterns.01_basic_tools

# Pattern 2: With Hooks
python -m patterns.02_with_hooks

# Pattern 3: With Permissions
python -m patterns.03_with_permissions

# Pattern 4: Complete Agent
python -m patterns.04_complete_agent

# Pattern 5: Deep Research Agent
python -m patterns.05_deep_research
```

## Pattern Details

### Pattern 1: Custom Tools (`patterns/01_basic_tools.py`)

**Purpose:** Learn how to extend Claude's capabilities with custom tools.

**What You'll Learn:**
- Using the `@tool` decorator
- Defining tool parameters with type hints
- Writing tool descriptions
- Error handling in tools

**Key Files:**
- `tools/calculator.py` - Calculator tool implementation
- `tools/test_calculator.py` - Tool tests

**Demo Flow:**
1. Creates a calculator tool with arithmetic operations
2. Registers tool with agent
3. Asks Claude to perform calculations
4. Shows tool execution and results

**Example Output:**
```
=== Pattern 1: Custom Tools Demo ===

Creating calculator tool...
Tool registered: calculator(name='calculator')

User: What is 15 times 7?

[Tool Use] calculator(operation='multiply', a=15, b=7)
Tool Result: 15 * 7 = 105

Claude: The result of 15 times 7 is 105.
```

### Pattern 2: Hooks for Control (`patterns/02_with_hooks.py`)

**Purpose:** Learn how to intercept and control agent behavior.

**What You'll Learn:**
- PreToolUse hooks for validation
- PostToolUse hooks for logging
- Blocking dangerous operations
- Audit logging for compliance

**Key Files:**
- `hooks/command_blocker.py` - PreToolUse hook to block commands
- `hooks/audit_logger.py` - PreToolUse/PostToolUse hook for logging
- `hooks/test_hooks.py` - Hook tests

**Demo Flow:**
1. Sets up CommandBlockerHook to block dangerous operations
2. Sets up AuditLoggerHook to log all tool uses
3. Attempts dangerous command (blocked)
4. Performs safe operation (allowed and logged)
5. Shows audit log

**Example Output:**
```
=== Pattern 2: Hooks Demo ===

[CommandBlocker] Blocking tool: run_shell_command
[CommandBlocker] Reason: Too dangerous!

[AuditLogger] Tool use: calculator
[AuditLogger] Params: {'operation': 'add', 'a': 5, 'b': 3}
[AuditLogger] Result: Success

Audit Log:
- run_shell_command: BLOCKED (Too dangerous!)
- calculator: ALLOWED (Success)
```

### Pattern 3: Permission Management (`patterns/03_with_permissions.py`)

**Purpose:** Learn how to control tool access with tiered permissions.

**What You'll Learn:**
- Using `allowed_tools` whitelist
- Configuring `permission_mode`
- Tiered permission levels (safe/semi-trusted/risky)
- Dynamic permission assignment

**Demo Flow:**
1. Defines tool tiers (safe, semi-trusted, risky)
2. Creates agent with safe-only permissions
3. Attempts risky operation (denied)
4. Performs safe operation (allowed)
5. Upgrades permissions
6. Performs semi-trusted operation (now allowed)

**Example Output:**
```
=== Pattern 3: Permission Management Demo ===

Permission Level: SAFE
Allowed tools: calculator, text_analyzer

User: Read the file /etc/passwd

Claude: I don't have access to file reading tools at my current
permission level. I can only use calculator and text_analyzer.

Permission Level: SEMI_TRUSTED
Allowed tools: calculator, text_analyzer, read_file

User: Read the file /etc/passwd

[Tool Use] read_file(path='/etc/passwd')
Tool Result: root:x:0:0:root:/root:/bin/bash...
```

### Pattern 4: Complete Agent (`patterns/04_complete_agent.py`)

**Purpose:** See all patterns working together in a production-ready agent.

**What You'll Learn:**
- Combining custom tools, hooks, and permissions
- Production best practices
- Comprehensive error handling
- Security hardening

**Demo Flow:**
1. Creates complete agent with all patterns
2. Demonstrates safe operations
3. Demonstrates security enforcement
4. Demonstrates audit logging
5. Shows production-ready error handling

**Example Output:**
```
=== Pattern 4: Complete Agent Demo ===

Agent Configuration:
- Tools: calculator, text_analyzer
- Hooks: CommandBlockerHook, AuditLoggerHook
- Permissions: SAFE (calculator, text_analyzer)
- Mode: STRICT

User: Calculate 123 * 456

[CommandBlocker] Checking tool: calculator
[CommandBlocker] Status: ALLOWED
[AuditLogger] Tool use: calculator
[AuditLogger] Result: Success

Claude: The result of 123 * 456 is 56,088.
```

### Pattern 5: Deep Research Agent (Sessions & Skills) (`patterns/05_deep_research.py`)

**Purpose:** Learn how to build advanced agents with session persistence and skill integration.

**What You'll Learn:**
- ClaudeSDKClient for automatic session management
- Agent loop for multi-turn reasoning without custom loops
- settingSources to load CLAUDE.md and skills
- Session operations: continue, resume, fork
- Web search integration for finding documentation
- User feedback integration

**Key Code:**
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

**Demo Flow:**
1. Creates research agent with project settings and skills
2. Researches a technical topic using web search
3. Continues session to deepen analysis
4. Generates comprehensive research report
5. Demonstrates session persistence

**Example Output:**
```
=== Pattern 5: Deep Research Agent Demo ===

Loading project settings from CLAUDE.md...
Found 5 skills: research, documentation, analysis, reporting, synthesis

Session: sess_abc123
Researching: Claude Agent SDK vs LangChain

[web_search] Query: "Claude Agent SDK vs LangChain comparison"
→ Found 15 results

[Skill] Loading research methodology...
→ Applied research framework

Turn 1: Gathering information...
→ Analyzed 8 sources
→ Identified 3 key differentiators

Turn 2: Deepening analysis...
→ Comparative architecture analysis
→ Use case evaluation

Report generated: research_report.md
```

## API Reference

### Tools

#### Calculator Tool

**Location:** `tools/calculator.py`

**Operations:**
- `add` - Addition
- `subtract` - Subtraction
- `multiply` - Multiplication
- `divide` - Division

**Usage:**
```python
from tools.calculator import calculator

result = calculator.invoke(
    operation="add",
    a=5,
    b=3
)
# Returns: "5 + 3 = 8"
```

### Hooks

#### CommandBlockerHook

**Location:** `hooks/command_blocker.py`

**Purpose:** Block dangerous tools from executing

**Blocked Tools:**
- `run_shell_command` - Shell command execution
- `write_file` - File writing
- `delete_file` - File deletion
- `network_request` - Network requests

**Usage:**
```python
from hooks.command_blocker import CommandBlockerHook

hook = CommandBlockerHook()
agent = Agent(hooks=[hook])
```

#### AuditLoggerHook

**Location:** `hooks/audit_logger.py`

**Purpose:** Log all tool uses for audit trails

**Log File:** `audit.log`

**Usage:**
```python
from hooks.audit_logger import AuditLoggerHook

hook = AuditLoggerHook(log_file="audit.log")
agent = Agent(hooks=[hook])
```

### Permission Modes

**PermissionMode.STRICT**
- Only tools in `allowed_tools` can be used
- Claude will not attempt other tools

**PermissionMode.PERMISSIVE** (default)
- Claude can attempt any tool
- Useful for exploration

## Troubleshooting

### Common Issues

#### Issue: "Module not found" error

**Solution:**
```bash
# Make sure you're in the demo directory
cd /path/to/demo

# Install dependencies
pip install -r requirements.txt

# Use python -m to run modules
python -m patterns.01_basic_tools
```

#### Issue: Permission denied errors

**Solution:**
```bash
# Make sure main.py is executable
chmod +x main.py

# Or run with python explicitly
python main.py
```

#### Issue: Virtual environment not activating

**Solution:**
```bash
# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate

# Verify activation
which python  # Should show venv path
```

#### Issue: Tests failing

**Solution:**
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tools/test_calculator.py -v

# Test deep research agent
python -m pytest patterns/test_deep_research.py -v
```

### Debug Mode

Enable debug logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

For practical usage examples, see [EXAMPLES.md](EXAMPLES.md).

Quick examples:

**Example 1: Using the calculator tool**
```python
from tools.calculator import calculator

result = calculator.invoke(
    operation="multiply",
    a=12,
    b=8
)
print(result)  # "12 * 8 = 96"
```

**Example 2: Blocking dangerous commands**
```python
from hooks.command_blocker import CommandBlockerHook
from claude_agent_sdk import Agent

hook = CommandBlockerHook()
agent = Agent(hooks=[hook])

# This will be blocked
agent.chat("Run: rm -rf /")
```

**Example 3: Setting up permissions**
```python
from claude_agent_sdk import Agent, PermissionMode

agent = Agent(
    allowed_tools=["calculator", "text_analyzer"],
    permission_mode=PermissionMode.STRICT
)

# Claude can only use calculator and text_analyzer
agent.chat("Analyze this text")
```

**Example 4: Building a complete agent**
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

agent.chat("Calculate 25 * 4")
```

## Next Steps

1. **Explore the patterns** - Run each pattern and examine the code
2. **Read the tests** - Tests show how to use each component
3. **Build your own** - Create custom tools and hooks
4. **Read the blog post** - See `../blog/post.md` for full tutorial

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test files for working examples
3. Read the blog post for detailed explanations
4. Check Claude Agent SDK documentation

## License

MIT License - See LICENSE file for details.
