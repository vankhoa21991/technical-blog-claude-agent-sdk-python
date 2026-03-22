---
title: "Building Production AI Agents with Claude Agent SDK Python: A Progressive Pattern Guide"
slug: claude-agent-sdk-python-progressive-patterns
date: 2026-03-21
author: AI Keytake
description: Learn how to build production AI agents with Claude Agent SDK Python through 5 progressive patterns: custom tools, hooks, permissions, complete agents, and sessions with skills.
tags: ["AI", "Python", "Claude", "Agent SDK", "Tutorial"]
difficulty: intermediate
estimated_time: "60 minutes"
demo_url: https://github.com/your-repo/claude-agent-sdk-python-demo
status: draft
---

# Building Production AI Agents with Claude Agent SDK Python: A Progressive Pattern Guide

**Why This Matters:** AI agents are transforming how we automate complex tasks, but building production-ready agents requires more than just API calls. You need control, security, and observability. The Claude Agent SDK Python provides exactly that through five powerful patterns that progressively add capabilities to your agents.

In this guide, you'll learn how to build production AI agents from the ground up using **Claude Agent SDK Python**. We'll progress through five patterns:

1. **Custom Tools** - Extend Claude with your own Python functions
2. **Hooks for Control** - Intercept and validate agent behavior
3. **Permission Management** - Implement tiered access control
4. **Complete Agent** - Combine all patterns into a production-ready system
5. **Sessions & Skills** - Multi-turn reasoning with project context and domain expertise

By the end, you'll have a fully functional AI agent with custom tools, security hooks, permission management, and session-based research capabilities—ready for production deployment.

## What You'll Learn

This tutorial targets **intermediate Python developers** (3-5 years experience) who want to:
- Build production AI agents with Claude Agent SDK Python
- Implement custom tools using the `@tool` decorator
- Add security and observability with hooks
- Control tool access with tiered permissions
- Follow best practices for production deployments

**Prerequisites:**
- Python 3.10+
- Basic understanding of async/await
- Familiarity with AI/LLM concepts
- 45 minutes to complete the tutorial

## Pattern 1: Custom Tools - Extending Claude's Capabilities

**The Problem:** Claude is powerful, but it can't access your business logic, databases, or APIs out of the box. You need a way to extend Claude with custom functionality.

**The Solution:** Custom tools using the `@tool` decorator. This lets you wrap any Python function as a tool that Claude can call.

### Understanding the @tool Decorator

The `@tool` decorator transforms regular Python functions into Claude-compatible tools. Here's a practical example—a calculator tool:

```python
from claude_agent_sdk import tool

@tool(
    name="calculate",
    description="Perform basic arithmetic operations",
    input_schema={
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"]
            }
        },
        "required": ["a", "b", "operation"]
    }
)
async def calculate_tool(input_data):
    """Perform arithmetic operations with error handling."""
    try:
        a = input_data["a"]
        b = input_data["b"]
        operation = input_data["operation"]

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {
                    "content": [
                        {"type": "text", "text": "Error: Division by zero"}
                    ]
                }
            result = a / b
        else:
            return {
                "content": [
                    {"type": "text", "text": f"Error: Unknown operation {operation}"}
                ]
            }

        return {"content": [{"type": "text", "text": str(result)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
```

### Key Components Explained

**1. Tool Metadata**
- `name`: How Claude refers to your tool
- `description`: Critical for Claude to understand when to use it
- `input_schema`: JSON Schema defining expected parameters

**2. Async Function**
- Tools must be async for performance
- Return format: `{"content": [{"type": "text", "text": "..."}]}`

**3. Error Handling**
- Graceful error messages prevent agent confusion
- Return errors in the same format as success responses

### When to Use Custom Tools

✅ **Use custom tools when:**
- You need to access business logic (calculations, validations)
- You want to wrap existing APIs (databases, web services)
- You need specialized processing (data transformation, parsing)
- You want to enforce specific input/output formats

❌ **Don't use custom tools when:**
- Built-in Claude capabilities suffice
- Simple prompting can achieve the same result
- The operation is too generic (better to use standard tools)

### Common Pitfalls to Avoid

**Pitfall 1: Vague Descriptions**
```python
# ❌ Bad - Claude won't know when to use it
@tool(name="process_data", description="Process some data")

# ✅ Good - Clear, actionable description
@tool(
    name="calculate_roi",
    description="Calculate return on investment given initial investment and final value"
)
```

**Pitfall 2: Missing Input Validation**
```python
# ❌ Bad - No validation, will crash on invalid input
async def bad_tool(input_data):
    return input_data["a"] / input_data["b"]  # Crashes if b=0

# ✅ Good - Validates input and handles errors
async def good_tool(input_data):
    try:
        if input_data["b"] == 0:
            return {"content": [{"type": "text", "text": "Error: Division by zero"}]}
        return {"content": [{"type": "text", "text": str(input_data["a"] / input_data["b"])}]}
    except KeyError as e:
        return {"content": [{"type": "text", "text": f"Error: Missing parameter {e}"}]}
```

**Pitfall 3: Forgetting Async**
```python
# ❌ Bad - Not async, will cause performance issues
@tool
def sync_tool(input_data):
    return {"content": [{"type": "text", "text": "result"}]}

# ✅ Good - Async for proper concurrency
@tool
async def async_tool(input_data):
    return {"content": [{"type": "text", "text": "result"}]}
```

### Testing Your Tools

Always test tools independently before integrating with Claude:

```python
import asyncio

async def test_calculator():
    # Test basic operation
    result = await calculate_tool.handler({"a": 25, "b": 4, "operation": "multiply"})
    print(f"25 * 4 = {result['content'][0]['text']}")

    # Test error handling
    error_result = await calculate_tool.handler({"a": 10, "b": 0, "operation": "divide"})
    print(f"Division by zero: {error_result['content'][0]['text']}")

asyncio.run(test_calculator())
```

**Output:**
```
25 * 4 = 100.0
Division by zero: Error: Division by zero
```

### Why This Matters

Custom tools are the foundation of production AI agents. They let you:
- **Integrate with existing systems** - Databases, APIs, business logic
- **Enforce consistency** - Validated inputs, formatted outputs
- **Improve reliability** - Error handling, edge cases covered
- **Scale efficiently** - Async operations, proper resource management

**Try It Yourself:** Run the Pattern 1 demo to see custom tools in action:
```bash
cd demo
python -m patterns.01_basic_tools
```

## Pattern 2: Hooks for Control - Intercepting Agent Behavior

**The Problem:** In production, you need more than just tool execution. You need security (block dangerous commands), compliance (audit all operations), and control (validate inputs before execution).

**The Solution:** Hooks—interceptors that run before (`PreToolUse`) or after (`PostToolUse`) tool execution.

### Understanding Hook Types

Hooks are async functions that intercept tool execution at two points:

**PreToolUse Hooks** - Run BEFORE tool execution:
- Validate inputs
- Block dangerous operations
- Modify parameters
- Log intent

**PostToolUse Hooks** - Run AFTER tool execution:
- Capture results
- Log outputs
- Modify responses
- Trigger notifications

### Implementing a Security Hook: Command Blocker

Let's build a hook that blocks dangerous bash commands:

```python
import re

async def pre_tool_use_hook(input_data, tool_use_id, context):
    """
    Block dangerous bash commands like 'rm -rf', fork bombs, etc.
    """
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    # Only check bash commands
    if tool_name == "bash":
        command = tool_input.get("command", "")

        # Define dangerous patterns
        dangerous_patterns = [
            r"rm\s+-rf\s+/",           # Recursive delete from root
            r":\(\)\{.*\|.*&.*\};:",   # Fork bomb
            r"format",                 # Disk formatting
            r"mkfs",                   # File system creation
            r"dd\s+if=",               # Direct disk write
        ]

        # Check if command matches any dangerous pattern
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Dangerous command detected: {pattern}. Command blocked for safety."
                    }
                }

    # Return empty dict for no-op (allow the command)
    return {}
```

### Implementing an Audit Hook

Now let's build a hook that logs all tool invocations:

```python
import json
from datetime import datetime
from pathlib import Path

async def pre_tool_use_hook(input_data, tool_use_id, context):
    """Log tool invocations BEFORE execution."""
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "PreToolUse",
        "tool": tool_name,
        "input": tool_input,
        "tool_use_id": tool_use_id
    }

    # Console log
    print(f"[AUDIT:PRE] {json.dumps(log_entry)}")

    # File log
    demo_dir = Path(__file__).parent.parent
    audit_log_path = demo_dir / "audit.log"
    with open(audit_log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {}  # No-op, just logging

async def post_tool_use_hook(tool_use_id, tool_output, context):
    """Log tool execution results AFTER execution."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "PostToolUse",
        "tool_use_id": tool_use_id,
        "output": tool_output
    }

    print(f"[AUDIT:POST] {json.dumps(log_entry)}")

    # File log
    demo_dir = Path(__file__).parent.parent
    audit_log_path = demo_dir / "audit.log"
    with open(audit_log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {}  # No-op, just logging
```

### How Hooks Work Together

Here's how hooks and tools work together in practice:

```python
async def execute_with_hooks(tool_name, tool_input):
    """Execute a tool with all hooks applied."""
    tool_use_id = f"tool-{uuid4()}"

    # Step 1: Apply PreToolUse hooks
    input_data = {"tool_name": tool_name, "tool_input": tool_input}

    for hook in pre_tool_use_hooks:
        result = await hook(input_data, tool_use_id, {})

        # Check if hook denied execution
        if result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny":
            reason = result["hookSpecificOutput"]["permissionDecisionReason"]
            print(f"❌ Execution denied: {reason}")
            return {"status": "blocked", "reason": reason}

    # Step 2: Execute the tool
    print(f"✓ All hooks passed, executing {tool_name}")
    result = await tool_handler(tool_input)

    # Step 3: Apply PostToolUse hooks
    for hook in post_tool_use_hooks:
        await hook(tool_use_id, result, {})

    return {"status": "completed", "result": result}
```

### Real-World Hook Use Cases

**1. Security Enforcement**
```python
async def security_hook(input_data, tool_use_id, context):
    """Block tools based on user permissions."""
    user_role = context.get("user_role", "guest")
    tool_name = input_data.get("tool_name")

    if tool_name in RESTRICTED_TOOLS and user_role != "admin":
        return {
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Tool {tool_name} requires admin role"
            }
        }
    return {}
```

**2. Input Validation**
```python
async def validation_hook(input_data, tool_use_id, context):
    """Validate inputs before tool execution."""
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "send_email":
        if "@" not in tool_input.get("recipient", ""):
            return {
                "hookSpecificOutput": {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Invalid email address"
                }
            }
    return {}
```

**3. Rate Limiting**
```python
from collections import defaultdict
import time

rate_limit_tracker = defaultdict(list)

async def rate_limit_hook(input_data, tool_use_id, context):
    """Enforce rate limits per tool."""
    tool_name = input_data.get("tool_name")
    user_id = context.get("user_id", "anonymous")

    now = time.time()
    window_start = now - 60  # 60-second window

    # Clean old entries
    rate_limit_tracker[f"{user_id}:{tool_name}"] = [
        ts for ts in rate_limit_tracker[f"{user_id}:{tool_name}"]
        if ts > window_start
    ]

    # Check limit
    if len(rate_limit_tracker[f"{user_id}:{tool_name}"]) >= 10:
        return {
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "permissionDecisionReason": "Rate limit exceeded (10 requests/minute)"
            }
        }

    rate_limit_tracker[f"{user_id}:{tool_name}"].append(now)
    return {}
```

### Common Hook Pitfalls

**Pitfall 1: Forgetting Async**
```python
# ❌ Bad - Not async
def pre_tool_use_hook(input_data, tool_use_id, context):
    return {}

# ✅ Good - Async
async def pre_tool_use_hook(input_data, tool_use_id, context):
    return {}
```

**Pitfall 2: Blocking Forever**
```python
# ❌ Bad - Blocks all bash commands
if tool_name == "bash":
    return {"hookSpecificOutput": {"permissionDecision": "deny"}}

# ✅ Good - Blocks only dangerous commands
if tool_name == "bash":
    command = tool_input.get("command", "")
    if is_dangerous(command):
        return {"hookSpecificOutput": {"permissionDecision": "deny"}}
```

**Pitfall 3: Not Returning Empty Dict for No-Op**
```python
# ❌ Bad - Returns None (might cause issues)
if should_block:
    return {"hookSpecificOutput": {...}}
# Otherwise, nothing returned

# ✅ Good - Explicitly return empty dict
if should_block:
    return {"hookSpecificOutput": {...}}
return {}  # Explicit no-op
```

### Why This Matters

Hooks provide the **control layer** that makes agents production-ready:
- **Security** - Block dangerous operations before execution
- **Compliance** - Audit trail for regulatory requirements
- **Observability** - Track what your agents are doing
- **Flexibility** - Modify behavior without changing tool code

**Try It Yourself:** Run the Pattern 2 demo to see hooks in action:
```bash
cd demo
python -m patterns.02_with_hooks
```

## Pattern 3: Permission Management - Tiered Access Control

**The Problem:** Not all tools are created equal. Some are safe (calculators), some are semi-trusted (file reads), and some are risky (bash commands). You need granular control over what Claude can do.

**The Solution:** Permission management with `allowed_tools` and `permission_mode` for tiered access control.

### Understanding the Three-Tier Model

The Claude Agent SDK supports a three-tier permission model:

**Tier 1: Safe Tools** (Auto-Approved)
- Tools in `allowed_tools` list
- Execute without permission prompts
- Example: `calculator`, `text_analyzer`

**Tier 2: Semi-trusted** (Auto-Approved with Mode)
- File operations when `permission_mode='acceptEdits'`
- Auto-approved but with awareness
- Example: `write_file`, `edit_file`

**Tier 3: Risky Tools** (Require Permission)
- Tools NOT in `allowed_tools`
- Require explicit user approval
- Example: `bash`, `delete_file`, `network_request`

### Configuring Permissions

Here's how to configure permissions using `ClaudeAgentOptions`:

```python
from claude_agent_sdk.types import ClaudeAgentOptions

# Tier 1: Safe tools only (strict mode)
options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant.",
    allowed_tools=["calculate", "read_file"],  # Only these tools
    permission_mode='default'  # No auto-approval
)

# Tier 2: Include file edits (development mode)
options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant.",
    allowed_tools=["calculate", "read_file", "write_file"],
    permission_mode='acceptEdits'  # Auto-approve file edits
)

# Tier 3: Fully autonomous (use with caution!)
options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant.",
    allowed_tools=["calculate", "read_file", "write_file", "bash"],
    permission_mode='auto'  # Auto-approve everything
)
```

### Permission Filtering in Action

Here's how permission filtering works:

```python
async def check_permission(tool_name, options):
    """Check if a tool requires permission."""
    is_allowed = tool_name in options.allowed_tools

    if is_allowed:
        print(f"✓ {tool_name}: Auto-approved (in allowed_tools)")
        return True
    else:
        print(f"⚠ {tool_name}: Permission required")
        # In production, trigger permission prompt here
        return False

# Example usage
options = ClaudeAgentOptions(
    allowed_tools=["calculate", "read_file"],
    permission_mode='acceptEdits'
)

# Safe tool - auto-approved
await check_permission("calculate", options)
# Output: ✓ calculate: Auto-approved (in allowed_tools)

# Risky tool - requires permission
await check_permission("bash", options)
# Output: ⚠ bash: Permission required
```

### Practical Permission Configurations

**Configuration 1: Production Agent (Safe Only)**
```python
production_options = ClaudeAgentOptions(
    system_prompt="You are a production assistant.",
    allowed_tools=["calculate", "read_file"],
    permission_mode='default'
)

# Use case: Customer-facing assistant
# - Can calculate prices
# - Can read product info
# - Cannot write files or execute commands
```

**Configuration 2: Development Agent (File Edits OK)**
```python
development_options = ClaudeAgentOptions(
    system_prompt="You are a development assistant.",
    allowed_tools=["calculate", "read_file", "write_file", "edit_file"],
    permission_mode='acceptEdits'
)

# Use case: Developer helper
# - Can perform calculations
# - Can read and write code files
# - Cannot execute bash commands
```

**Configuration 3: Autonomous Agent (Fully Trusted)**
```python
autonomous_options = ClaudeAgentOptions(
    system_prompt="You are an autonomous agent.",
    allowed_tools=["calculate", "read_file", "write_file", "bash"],
    permission_mode='auto'
)

# Use case: Automated task runner (sandboxed environment)
# - Can do anything
# - Requires strict sandboxing
# - Use with extreme caution!
```

### Dynamic Permission Assignment

You can also implement dynamic permission logic:

```python
class PermissionManager:
    """Manage permissions based on user role."""

    def __init__(self, user_role):
        self.user_role = user_role

    def get_allowed_tools(self):
        """Return allowed tools based on role."""
        if self.user_role == "admin":
            return ["calculate", "read_file", "write_file", "bash"]
        elif self.user_role == "developer":
            return ["calculate", "read_file", "write_file"]
        elif self.user_role == "user":
            return ["calculate", "read_file"]
        else:
            return ["calculate"]

    def get_permission_mode(self):
        """Return permission mode based on role."""
        if self.user_role == "admin":
            return 'auto'
        elif self.user_role == "developer":
            return 'acceptEdits'
        else:
            return 'default'

# Usage
permission_manager = PermissionManager(user_role="developer")
options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant.",
    allowed_tools=permission_manager.get_allowed_tools(),
    permission_mode=permission_manager.get_permission_mode()
)
```

### Permission Best Practices

✅ **DO:**
- Start with restrictive permissions (Tier 1 only)
- Gradually add permissions as needed
- Document why each tool is allowed
- Use different configs for dev/prod

❌ **DON'T:**
- Use `permission_mode='auto'` in production
- Allow `bash` without sandboxing
- Grant all permissions to all users
- Forget to audit permission changes

### Common Permission Pitfalls

**Pitfall 1: Over-Permissive Configurations**
```python
# ❌ Bad - Too permissive for production
options = ClaudeAgentOptions(
    allowed_tools=["*"],  # Wildcard allows everything!
    permission_mode='auto'
)

# ✅ Good - Explicit whitelist
options = ClaudeAgentOptions(
    allowed_tools=["calculate", "read_file"],
    permission_mode='default'
)
```

**Pitfall 2: Forgetting permission_mode**
```python
# ❌ Bad - Missing permission_mode
options = ClaudeAgentOptions(
    allowed_tools=["calculate", "write_file"]
    # permission_mode defaults to 'default', file edits will prompt
)

# ✅ Good - Explicit permission_mode
options = ClaudeAgentOptions(
    allowed_tools=["calculate", "write_file"],
    permission_mode='acceptEdits'  # Auto-approve file edits
)
```

**Pitfall 3: Not Logging Permission Changes**
```python
# ❌ Bad - Silent permission changes
options.allowed_tools.append("bash")  # No audit trail

# ✅ Good - Logged permission changes
import logging
logging.info(f"Adding 'bash' to allowed_tools for user {user_id}")
options.allowed_tools.append("bash")
```

### Why This Matters

Permission management is your **safety net**:
- **Prevents accidents** - Claude can't accidentally delete files
- **Enforces least privilege** - Users only get necessary permissions
- **Enables progressive trust** - Start safe, add permissions as needed
- **Supports compliance** - Audit trail of who can do what

**Try It Yourself:** Run the Pattern 3 demo to see permissions in action:
```bash
cd demo
python -m patterns.03_with_permissions
```

## Pattern 4: Complete Agent - All Patterns Combined

**The Problem:** Real-world agents need all three patterns working together: custom tools for functionality, hooks for security, and permissions for control.

**The Solution:** A complete agent that combines all patterns into a production-ready system.

### Complete Agent Architecture

Let's build a complete agent that integrates all patterns:

```python
from claude_agent_sdk.types import ClaudeAgentOptions
from tools.calculator import calculate_tool
from hooks.command_blocker import pre_tool_use_hook as block_dangerous_commands
from hooks.audit_logger import pre_tool_use_hook as log_tool_use_pre
from hooks.audit_logger import post_tool_use_hook as log_tool_use_post

class CompleteAgent:
    """Production-ready agent with all patterns."""

    def __init__(self):
        # Pattern 3: Permissions
        self.options = ClaudeAgentOptions(
            system_prompt="You are a helpful task automation assistant.",
            allowed_tools=["calculate", "read_file"],  # Safe tools only
            permission_mode='acceptEdits'  # Auto-approve file edits
        )

        # Pattern 2: Hooks
        self.hooks = {
            "PreToolUse": [block_dangerous_commands, log_tool_use_pre],
            "PostToolUse": [log_tool_use_post]
        }

        # Pattern 1: Tools (loaded dynamically)
        self.tools = {
            "calculate": calculate_tool
        }

        # Audit trail
        self.audit_log = []

    async def execute_tool(self, tool_name, tool_input):
        """Execute a tool with all patterns applied."""
        tool_use_id = f"tool-{len(self.audit_log)}"

        print(f"\n{'='*70}")
        print(f"Executing: {tool_name}")
        print(f"Input: {tool_input}")
        print(f"{'='*70}")

        # Step 1: Check permissions (Pattern 3)
        print("\n[Pattern 3: Permissions]")
        is_allowed = tool_name in self.options.allowed_tools
        print(f"  Tool in allowed_tools: {is_allowed}")

        if not is_allowed:
            print(f"  ⚠ Permission required for: {tool_name}")
            return {
                "status": "denied",
                "reason": f"Tool '{tool_name}' not in allowed_tools"
            }

        # Step 2: Apply PreToolUse hooks (Pattern 2)
        print("\n[Pattern 2: PreToolUse Hooks]")
        input_data = {"tool_name": tool_name, "tool_input": tool_input}

        for hook in self.hooks["PreToolUse"]:
            print(f"  → Applying {hook.__name__}...")
            hook_result = await hook(input_data, tool_use_id, {})

            if hook_result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny":
                reason = hook_result["hookSpecificOutput"]["permissionDecisionReason"]
                print(f"  ✗ Execution denied by {hook.__name__}")
                print(f"  Reason: {reason}")
                return {
                    "status": "blocked",
                    "reason": reason,
                    "hook": hook.__name__
                }

            print(f"  ✓ {hook.__name__} passed")

        # Step 3: Execute tool (Pattern 1)
        print("\n[Pattern 1: Tool Execution]")
        print(f"  → Executing {tool_name}...")

        if tool_name == "calculate":
            result = await calculate_tool.handler(tool_input)
            output_text = result["content"][0]["text"]
            print(f"  ✓ Result: {output_text}")
        else:
            output_text = f"Simulated output for {tool_name}"
            print(f"  ✓ {output_text}")
            result = {"content": [{"type": "text", "text": output_text}]}

        # Step 4: Apply PostToolUse hooks (Pattern 2)
        print("\n[Pattern 2: PostToolUse Hooks]")
        for hook in self.hooks["PostToolUse"]:
            print(f"  → Applying {hook.__name__}...")
            await hook(tool_use_id, result, {})
            print(f"  ✓ {hook.__name__} logged")

        # Log to audit trail
        self.audit_log.append({
            "tool_use_id": tool_use_id,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "result": result,
            "status": "completed"
        })

        print(f"\n{'='*70}")
        print(f"✓ Tool execution completed successfully")
        print(f"{'='*70}")

        return {
            "status": "completed",
            "result": result
        }

    def show_audit_trail(self):
        """Display complete audit trail."""
        print("\n" + "="*70)
        print("Complete Audit Trail")
        print("="*70)

        for i, entry in enumerate(self.audit_log, 1):
            print(f"\n{i}. Tool Use ID: {entry['tool_use_id']}")
            print(f"   Tool: {entry['tool_name']}")
            print(f"   Input: {entry['tool_input']}")
            print(f"   Status: {entry['status']}")
            if entry['status'] == 'completed':
                result = entry['result']['content'][0]['text']
                print(f"   Result: {result}")

        print("\n" + "="*70)
```

### Real-World Scenarios

Let's see the complete agent in action with realistic scenarios:

**Scenario 1: Safe Calculation**
```python
agent = CompleteAgent()
result = await agent.execute_tool(
    "calculate",
    {"a": 25, "b": 4, "operation": "multiply"}
)
# Output: 100.0
# Status: completed
# Audit trail: Logged
```

**Scenario 2: Dangerous Command Blocked**
```python
result = await agent.execute_tool(
    "bash",
    {"command": "rm -rf /important/data"}
)
# Output: Command blocked by command_blocker hook
# Status: blocked
# Reason: Dangerous command detected
# Audit trail: Logged (even blocked attempts!)
```

**Scenario 3: Permission Denied**
```python
result = await agent.execute_tool(
    "bash",
    {"command": "ls -la"}
)
# Output: Permission required
# Status: denied
# Reason: Tool 'bash' not in allowed_tools
# Audit trail: Logged
```

**Scenario 4: Complex Multi-Step Task**
```python
# Calculate project budget
team_cost = await agent.execute_tool(
    "calculate",
    {"a": 10, "b": 100, "operation": "multiply"}  # 10 people * $100/hr
)

duration_cost = await agent.execute_tool(
    "calculate",
    {"a": 1000, "b": 40, "operation": "multiply"}  # $1000/hr * 40 hours
)

total_with_overhead = await agent.execute_tool(
    "calculate",
    {"a": 40000, "b": 1.2, "operation": "multiply"}  # +20% overhead
)
# All operations logged and audited
```

### Production Best Practices

When deploying a complete agent to production, follow these guidelines:

**1. Security First**
```python
# Start with minimal permissions
options = ClaudeAgentOptions(
    allowed_tools=["calculate"],  # Only calculator
    permission_mode='default'  # No auto-approval
)

# Add security hooks
hooks = {
    "PreToolUse": [block_dangerous_commands, rate_limit_hook, security_hook],
    "PostToolUse": [audit_logger_hook]
}
```

**2. Comprehensive Logging**
```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

# Log all tool uses
logger = logging.getLogger('agent')
logger.info(f"Tool execution: {tool_name} with input: {tool_input}")
```

**3. Error Handling**
```python
async def execute_tool_safe(self, tool_name, tool_input):
    """Execute tool with comprehensive error handling."""
    try:
        result = await self.execute_tool(tool_name, tool_input)
        return result
    except Exception as e:
        logger.error(f"Error executing {tool_name}: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "tool_name": tool_name
        }
```

**4. Monitoring & Alerting**
```python
from prometheus_client import Counter, Histogram

# Metrics
tool_counter = Counter('tool_executions_total', 'Total tool executions', ['tool_name', 'status'])
tool_duration = Histogram('tool_execution_duration_seconds', 'Tool execution duration', ['tool_name'])

async def execute_tool_with_metrics(self, tool_name, tool_input):
    """Execute tool with Prometheus metrics."""
    start_time = time.time()

    try:
        result = await self.execute_tool(tool_name, tool_input)
        tool_counter.labels(tool_name=tool_name, status='success').inc()
        return result
    except Exception as e:
        tool_counter.labels(tool_name=tool_name, status='error').inc()
        raise
    finally:
        duration = time.time() - start_time
        tool_duration.labels(tool_name=tool_name).observe(duration)
```

### Why This Matters

The complete agent pattern brings everything together:
- **Functionality** - Custom tools do the work
- **Security** - Hooks enforce rules
- **Control** - Permissions limit access
- **Observability** - Audit trail tracks everything

This is the **production-ready foundation** for building AI agents that are:
- **Safe** - Dangerous operations blocked
- **Compliant** - Everything logged
- **Controllable** - Granular permissions
- **Observable** - Complete audit trail

**Try It Yourself:** Run the Pattern 4 demo to see the complete agent:
```bash
cd demo
python -m patterns.04_complete_agent
```

## Pattern 5: Deep Research Agent with Sessions and Skills

So far, we've built agents that respond to single prompts. But what if you need an agent that can:

- Maintain conversation state across multiple interactions?
- Access project-specific context and instructions?
- Use specialized domain knowledge?
- Allow users to provide feedback and refine the analysis?

Enter **ClaudeSDKClient** and the **Agent Loop** - the most powerful pattern in the SDK.

### The Scenario: Literature Review Agent

Let's build an agent that conducts a literature review comparing three AI agent frameworks:
- **LangGraph** (from LangChain)
- **AutoGen** (from Microsoft)
- **Claude Agent SDK** (from Anthropic)

The agent will:
1. Search the web for official documentation and comparisons
2. Analyze architecture, features, and use cases
3. Accept user feedback on what to focus on
4. Provide refined analysis based on feedback
5. Optionally explore alternative directions via session forking

### Key Concepts

**ClaudeSDKClient**: Automatic session management
- Creates sessions automatically on first `query()`
- Manages session lifecycle (create, continue, resume, fork)
- No manual session handling required

**Agent Loop**: Multi-turn reasoning without custom code
- Agent automatically does multi-step analysis
- Each turn can use tools, search web, read files
- No need to write custom "thinking" loops
- Control depth with `effort` parameter (low/medium/high/max)

**settingSources**: Load CLAUDE.md and skills
- `setting_sources=["project"]` loads:
  - `CLAUDE.md` - Project instructions and context
  - `.claude/skills/*/SKILL.md` - Domain expertise
- Agent loads skills on-demand via `Skill` tool
- Skills provide methodology without biasing analysis

**Session Operations**:
- **Continue**: Multiple `query()` calls with same `session_id`
- **Resume**: Load specific session by ID for long-running tasks
- **Fork**: Create new session from existing (explore alternatives)

### Implementation

**Setup**:
```python
from claude_agent_sdk import ClaudeSDKClient, query, ClaudeAgentOptions

client = ClaudeSDKClient()
```

**Phase 1: Initial Research**
```python
async for message in query(
    prompt="Conduct literature review comparing LangGraph, AutoGen, and Claude Agent SDK...",
    options=ClaudeAgentOptions(
        setting_sources=["project"],  # Load CLAUDE.md and skills
        allowed_tools=["Skill", "Read", "Bash", "web_search"],
        effort="high"  # Deeper reasoning per turn
    )
):
    print(message.content)

session_id = client.get_most_recent_session_id()
```

**Phase 2: User Feedback** (Manual CLI pause)
```python
direction = input("Focus on architecture or use cases? ")
```

**Phase 3: Refined Analysis** (Continue same session)
```python
async for message in query(
    prompt=f"Great, focusing on {direction}. Provide detailed comparison...",
    options=ClaudeAgentOptions(
        setting_sources=["project"],
        session_id=session_id  # Continue same session
    )
):
    print(message.content)
```

**Phase 4: Fork Session** (Optional)
```python
async for message in query(
    prompt="Now compare learning curves instead",
    options=ClaudeAgentOptions(
        setting_sources=["project"],
        fork_from=session_id  # Fork: new session with copied history
    )
):
    print(message.content)
```

### Skills System

Skills are markdown files that provide domain expertise to the agent.

**Structure**:
```
demo/.claude/skills/
└── research/
    └── SKILL.md
```

**Example Skill** (`research/SKILL.md`):
```markdown
---
name: research
description: Research methodology for deep analysis
---

# Research Methodology

## Phase 1: Information Gathering
- Search official documentation first
- Find comparison guides and benchmarks
- Identify key differentiators

## Phase 2: Analysis
- Compare architecture patterns
- Evaluate use cases and trade-offs
- Assess strengths and weaknesses

## Phase 3: Synthesis
- Identify patterns and trends
- Highlight key differences
- Provide concrete recommendations
```

When the agent needs research expertise, it automatically loads the skill via the `Skill` tool.

### CLAUDE.md Integration

`CLAUDE.md` provides project context automatically:

```markdown
# Claude Agent SDK Python - Progressive Patterns Demo

## Project Overview
This demo teaches four core patterns...

## Quick Commands
```bash
python main.py  # Run interactive menu
```

## Architecture
**Pattern 5 Features:**
- ClaudeSDKClient: Automatic session management
- Agent Loop: Multi-turn reasoning
- settingSources: Loads CLAUDE.md and skills
...
```

The agent uses this context to understand the project structure and available patterns.

### Live Demo

Run the demo:
```bash
cd demo
python patterns/05_deep_research.py
```

**What you'll see:**

1. **Phase 1: Initial Research**
   - Agent searches web for documentation
   - Analyzes all three frameworks
   - Produces 1-2 page summary report
   - Displays session ID

2. **Phase 2: User Feedback**
   - Demo pauses for your input
   - Choose focus area: architecture, use cases, learning curve, performance, or custom

3. **Phase 3: Refined Analysis**
   - Agent continues same session (context preserved)
   - Deepens analysis on chosen topic
   - Builds on previous research

4. **Phase 4: Optional Fork**
   - Choose to explore alternative direction
   - Fork creates new session with copied history
   - Original session unchanged

**Expected Output** (excerpt):
```markdown
# Literature Review: LangGraph vs AutoGen vs Claude Agent SDK

## Overview
This report compares three leading frameworks for building AI agents...

## LangGraph
**Architecture:** Graph-based agent orchestration...
**Strengths:** Visual debugging, complex multi-agent workflows...
**Weaknesses:** Steep learning curve, heavy abstraction...

## AutoGen
**Architecture:** Multi-agent conversation framework...
**Strengths:** Natural multi-agent patterns, Microsoft backing...
**Weaknesses:** Less mature ecosystem, Python-only...

## Claude Agent SDK
**Architecture:** Tool-calling with agent loop...
**Strengths:** Simple API, built-in session management...
**Weaknesses:** Newer framework, fewer examples...

## Recommendation
Choose based on your use case...
```

### Key Takeaways

**ClaudeSDKClient** vs Manual Session Management:
- ✅ Automatic session creation
- ✅ Built-in continue/resume/fork
- ✅ No manual state handling
- ❌ Less control over session lifecycle

**Agent Loop** vs Custom Thinking:
- ✅ Multi-turn reasoning automatic
- ✅ No custom "thinking" prompts
- ✅ Handles tool use naturally
- ❌ Less transparent reasoning process

**settingSources** vs Manual Context:
- ✅ Automatic CLAUDE.md loading
- ✅ On-demand skill loading
- ✅ Project context always available
- ❌ Requires filesystem structure

### When to Use Pattern 5

**Use Pattern 5 when:**
- Building research or analysis agents
- Need multi-turn reasoning with user feedback
- Want session persistence across interactions
- Have domain expertise in skills format
- Exploring alternative directions (fork)

**Consider alternatives when:**
- Simple single-turn tasks (use Pattern 1)
- No need for user feedback (use Pattern 4)
- Custom session handling required
- Don't have skills or CLAUDE.md

### Production Tips

1. **Effort Levels**: Use `effort="high"` for complex research, `effort="low"` for quick tasks
2. **Session Management**: Save session IDs for long-running tasks (resumable research)
3. **Skills**: Keep skills focused on methodology, not specific frameworks (avoids bias)
4. **Error Handling**: Wrap `query()` calls in try/except for production robustness
5. **Web Search**: Always include `web_search` in `allowed_tools` for research tasks

### Next Steps

Try the demo:
```bash
cd demo
python patterns/05_deep_research.py
```

Explore the code:
```bash
cat demo/patterns/05_deep_research.py
cat demo/CLAUDE.md
cat demo/.claude/skills/research/SKILL.md
```

Read the SDK documentation:
- [Sessions](https://platform.claude.com/docs/en/agent-sdk/sessions)
- [Agent Loop](https://platform.claude.com/docs/en/agent-sdk/agent-loop)
- [Claude Code Features](https://platform.claude.com/docs/en/agent-sdk/claude-code-features)

## Summary

In this blog series, we've progressed from basic tools to advanced agents:

| Pattern | Capability | Use Case |
|---------|-----------|----------|
| 1. Custom Tools | Extend Claude with Python functions | Calculators, APIs, utilities |
| 2. Hooks | Intercept agent behavior | Security, validation, audit |
| 3. Permissions | Control tool access | Tiered access, safety |
| 4. Complete Agent | All patterns combined | Production agents |
| 5. Sessions & Skills | Multi-turn reasoning with context | Research, analysis, feedback |

**Pattern 5 is the most powerful** - it enables agents that:
- Maintain state across interactions
- Learn from project context (CLAUDE.md)
- Use domain expertise (skills)
- Iterate with human feedback
- Explore alternatives (fork)

This is how you build production AI agents that can tackle complex, multi-step research tasks while maintaining context and adapting to user feedback.

**Ready to build your own agent?** Start with Pattern 1, progress through the patterns, and you'll have production-ready agents in no time.

## Best Practices for Production AI Agents

After implementing all five patterns, here are the key best practices for production deployments:

### 1. Start Simple, Add Complexity Gradually

Begin with Pattern 1 (custom tools) and add patterns as needed:
- **MVP**: Custom tools only
- **V1**: Add permissions (Pattern 3)
- **V2**: Add security hooks (Pattern 2)
- **Production**: Complete agent (Pattern 4)
- **Advanced**: Research agent with sessions (Pattern 5)

### 2. Security by Default

- **Default deny**: Use restrictive `allowed_tools`
- **Layered security**: Combine hooks + permissions
- **Audit everything**: Log all tool uses
- **Sandbox execution**: Run in isolated environments

### 3. Test Thoroughly

```python
# Test each pattern independently
async def test_all_patterns():
    # Test Pattern 1: Tools
    assert await test_calculator_tool()

    # Test Pattern 2: Hooks
    assert await test_command_blocker()
    assert await test_audit_logger()

    # Test Pattern 3: Permissions
    assert await test_permission_filtering()

    # Test Pattern 4: Complete agent
    assert await test_complete_agent()

    # Test Pattern 5: Sessions & Skills
    assert await test_deep_research_agent()

    print("✓ All patterns tested successfully")
```

### 4. Monitor Performance

Track metrics for:
- Tool execution time
- Hook latency
- Permission deny rates
- Error rates by tool

### 5. Document Everything

- **Tool descriptions** - Clear, actionable
- **Hook logic** - Why each hook exists
- **Permission rationale** - Why tools are allowed/denied
- **Audit schema** - What's logged and why

### 6. Handle Errors Gracefully

```python
async def safe_execute(tool_name, tool_input):
    """Execute tool with comprehensive error handling."""
    try:
        # Check permissions
        if not check_permission(tool_name):
            return {"status": "denied", "reason": "Permission denied"}

        # Apply hooks
        hook_result = await apply_pre_hooks(tool_name, tool_input)
        if hook_result.get("blocked"):
            return {"status": "blocked", "reason": hook_result["reason"]}

        # Execute tool
        result = await execute_tool(tool_name, tool_input)

        # Apply post-hooks
        await apply_post_hooks(tool_name, result)

        return {"status": "success", "result": result}

    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": "Internal error"}
```

### 7. Version Your Tools

```python
@tool(
    name="calculate_v2",
    description="Calculator with improved error handling (v2)",
    version="2.0.0"
)
async def calculate_tool_v2(input_data):
    """Improved calculator with better error handling."""
    # Implementation
```

## Conclusion: Building Production AI Agents

You've now learned how to build production AI agents with Claude Agent SDK Python through five progressive patterns:

**Pattern 1: Custom Tools** - Extend Claude with your own Python functions
**Pattern 2: Hooks for Control** - Intercept and validate agent behavior
**Pattern 3: Permission Management** - Implement tiered access control
**Pattern 4: Complete Agent** - Combine all patterns into production-ready systems
**Pattern 5: Sessions & Skills** - Multi-turn reasoning with project context and domain expertise

### Key Takeaways

1. **Start with tools** - Build custom tools for your specific use case
2. **Add hooks for security** - Implement PreToolUse and PostToolUse hooks
3. **Control access with permissions** - Use `allowed_tools` and `permission_mode`
4. **Combine all patterns** - Build complete agents for production
5. **Add sessions for research** - Use ClaudeSDKClient for multi-turn reasoning with context

### Next Steps

1. **Try the demo**: Run all five patterns locally
   ```bash
   cd demo
   python main.py
   ```

2. **Build your own tools**: Create custom tools for your use case
3. **Add security**: Implement hooks for your threat model
4. **Configure permissions**: Set up tiered access for your users
5. **Add sessions for research**: Use ClaudeSDKClient for multi-turn agents
6. **Deploy to production**: Follow best practices for monitoring and logging

### Resources

- **Demo Code**: [GitHub Repository](https://github.com/your-repo/claude-agent-sdk-python-demo)
- **Official Docs**: [Claude Agent SDK Python Documentation](https://docs.anthropic.com/claude-agent-sdk)
- **Community**: Join the Claude Agent SDK community for support

### Call to Action

Ready to build your own production AI agent? Start with the demo code and extend it for your use case. The patterns you've learned are the foundation for building safe, secure, and observable AI agents.

**Try it now:**
```bash
git clone https://github.com/your-repo/claude-agent-sdk-python-demo
cd claude-agent-sdk-python-demo/demo
python main.py
```

Happy building! 🚀

---

**Author's Note:** This tutorial reflects the latest Claude Agent SDK Python patterns as of March 2026. APIs and best practices evolve, so always check the official documentation for the most current information.

**About the Author:** This guide was created by AI Keytake, an AI consulting company specializing in production AI agent development. We help businesses build and deploy AI agents that are safe, secure, and scalable.

**Got Questions?** Join the discussion in our community forum or open an issue on GitHub.
