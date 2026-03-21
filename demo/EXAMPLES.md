# Claude Agent SDK Python - Usage Examples

This document provides practical, copy-pasteable examples for using the Claude Agent SDK Python patterns. Each example is self-contained and can be run independently.

## Table of Contents

- [Example 1: Using the Calculator Tool](#example-1-using-the-calculator-tool)
- [Example 2: Blocking Dangerous Commands](#example-2-blocking-dangerous-commands)
- [Example 3: Setting Up Permissions](#example-3-setting-up-permissions)
- [Example 4: Building a Complete Agent](#example-4-building-a-complete-agent)
- [Example 5: Creating Custom Tools](#example-5-creating-custom-tools)
- [Example 6: Writing Custom Hooks](#example-6-writing-custom-hooks)
- [Example 7: Audit Logging](#example-7-audit-logging)
- [Example 8: Error Handling](#example-8-error-handling)

## Example 1: Using the Calculator Tool

### Basic Usage

```python
from tools.calculator import calculator

# Perform addition
result = calculator.invoke(
    operation="add",
    a=10,
    b=5
)
print(result)
# Output: "10 + 5 = 15"

# Perform multiplication
result = calculator.invoke(
    operation="multiply",
    a=7,
    b=6
)
print(result)
# Output: "7 * 6 = 42"
```

### Using with an Agent

```python
from claude_agent_sdk import Agent
from tools.calculator import calculator

# Create agent with calculator tool
agent = Agent(tools=[calculator])

# Ask Claude to perform calculations
response = agent.chat("What is 25 times 4?")
print(response)
# Output: "The result of 25 times 4 is 100."

response = agent.chat("Calculate 123 divided by 3")
print(response)
# Output: "The result of 123 divided by 3 is 41."
```

### Error Handling

```python
from tools.calculator import calculator

try:
    # Division by zero
    result = calculator.invoke(
        operation="divide",
        a=10,
        b=0
    )
except ValueError as e:
    print(f"Error: {e}")
    # Output: "Error: Cannot divide by zero"

try:
    # Invalid operation
    result = calculator.invoke(
        operation="modulo",
        a=10,
        b=3
    )
except ValueError as e:
    print(f"Error: {e}")
    # Output: "Error: Unknown operation: modulo"
```

## Example 2: Blocking Dangerous Commands

### Basic Command Blocking

```python
from hooks.command_blocker import CommandBlockerHook
from claude_agent_sdk import Agent

# Create hook
hook = CommandBlockerHook()

# Create agent with hook
agent = Agent(hooks=[hook])

# Try to run a dangerous command
response = agent.chat("Execute: rm -rf /")
print(response)
# Output: "I'm sorry, but I cannot execute shell commands as they are blocked for security reasons."
```

### Custom Blocked Tools

```python
from hooks.command_blocker import CommandBlockerHook

# Create hook with custom blocked tools
hook = CommandBlockerHook(
    blocked_tools={
        "run_shell_command": "Too dangerous!",
        "write_file": "File writing is not allowed",
        "delete_file": "File deletion is not allowed"
    }
)

agent = Agent(hooks=[hook])

# All these will be blocked
agent.chat("Run: ls -la")
agent.chat("Write to config.txt")
agent.chat("Delete temp.txt")
```

### Combining with Audit Logging

```python
from hooks.command_blocker import CommandBlockerHook
from hooks.audit_logger import AuditLoggerHook
from claude_agent_sdk import Agent

# Create both hooks
blocker = CommandBlockerHook()
logger = AuditLoggerHook(log_file="audit.log")

# Create agent with both hooks
agent = Agent(hooks=[blocker, logger])

# Blocked attempt is logged
agent.chat("Execute: rm -rf /")

# Safe operation is logged
agent.chat("Calculate 10 + 5")

# Check the log
with open("audit.log", "r") as f:
    print(f.read())
```

## Example 3: Setting Up Permissions

### Strict Mode (Whitelist)

```python
from claude_agent_sdk import Agent, PermissionMode

# Create agent with strict permissions
agent = Agent(
    allowed_tools=["calculator", "text_analyzer"],
    permission_mode=PermissionMode.STRICT
)

# This works - calculator is allowed
response = agent.chat("Calculate 15 * 7")
print(response)

# This fails - file_reader is not in allowed list
response = agent.chat("Read the file config.txt")
print(response)
# Output: "I don't have access to file reading tools..."
```

### Permissive Mode (Default)

```python
from claude_agent_sdk import Agent, PermissionMode

# Create agent with permissive permissions
agent = Agent(
    allowed_tools=["calculator"],
    permission_mode=PermissionMode.PERMISSIVE
)

# Claude can attempt any tool
# But calculator is the only one available
response = agent.chat("Read the file config.txt")
print(response)
# Output: "I don't have a file reading tool available..."
```

### Dynamic Permission Changes

```python
from claude_agent_sdk import Agent, PermissionMode

# Start with safe permissions
agent = Agent(
    allowed_tools=["calculator"],
    permission_mode=PermissionMode.STRICT
)

# Only calculator available
agent.chat("Calculate 10 + 5")  # Works

# Upgrade permissions
agent.allowed_tools = ["calculator", "read_file", "write_file"]

# Now file operations are available
agent.chat("Read the file config.txt")  # Works
```

### Tiered Permission Levels

```python
from claude_agent_sdk import Agent, PermissionMode

# Define permission tiers
SAFE_TOOLS = ["calculator", "text_analyzer"]
SEMI_TRUSTED_TOOLS = SAFE_TOOLS + ["read_file", "write_file"]
RISKY_TOOLS = SEMI_TRUSTED_TOOLS + ["run_shell_command", "delete_file"]

# Start at safe level
agent = Agent(
    allowed_tools=SAFE_TOOLS,
    permission_mode=PermissionMode.STRICT
)

# Upgrade based on user trust level
def upgrade_permissions(agent, level):
    if level == "safe":
        agent.allowed_tools = SAFE_TOOLS
    elif level == "semi_trusted":
        agent.allowed_tools = SEMI_TRUSTED_TOOLS
    elif level == "risky":
        agent.allowed_tools = RISKY_TOOLS

# Upgrade to semi-trusted
upgrade_permissions(agent, "semi_trusted")
agent.chat("Read the file config.txt")  # Now works
```

## Example 4: Building a Complete Agent

### Production-Ready Agent

```python
from claude_agent_sdk import Agent, PermissionMode
from tools.calculator import calculator
from hooks.command_blocker import CommandBlockerHook
from hooks.audit_logger import AuditLoggerHook

# Create complete agent
agent = Agent(
    tools=[calculator],
    hooks=[
        CommandBlockerHook(),
        AuditLoggerHook(log_file="audit.log")
    ],
    allowed_tools=["calculator"],
    permission_mode=PermissionMode.STRICT
)

# Use the agent
response = agent.chat("Calculate 25 * 4")
print(response)
# Output: "The result of 25 times 4 is 100."

# Check audit log
with open("audit.log", "r") as f:
    print(f.read())
```

### Multi-Tool Agent

```python
from claude_agent_sdk import Agent, PermissionMode
from tools.calculator import calculator
from tools.text_analyzer import text_analyzer  # Hypothetical

# Create agent with multiple tools
agent = Agent(
    tools=[calculator, text_analyzer],
    hooks=[CommandBlockerHook(), AuditLoggerHook()],
    allowed_tools=["calculator", "text_analyzer"],
    permission_mode=PermissionMode.STRICT
)

# Claude can use both tools
response1 = agent.chat("Calculate 100 / 4")
response2 = agent.chat("Analyze the sentiment of this text: 'I love this!'")

print(response1)
print(response2)
```

### Error Handling in Complete Agent

```python
from claude_agent_sdk import Agent, PermissionMode

agent = Agent(
    tools=[calculator],
    hooks=[CommandBlockerHook(), AuditLoggerHook()],
    allowed_tools=["calculator"],
    permission_mode=PermissionMode.STRICT
)

# Safe operation
try:
    response = agent.chat("Calculate 10 / 2")
    print(response)
except Exception as e:
    print(f"Error: {e}")

# Handle errors gracefully
response = agent.chat("Calculate 10 / 0")
# Calculator handles division by zero
print(response)
```

## Example 5: Creating Custom Tools

### Simple Tool

```python
from claude_agent_sdk import tool

@tool
def greet(name: str) -> str:
    """Greet a person by name.

    Args:
        name: The name of the person to greet

    Returns:
        A greeting message
    """
    return f"Hello, {name}!"

# Use the tool
agent = Agent(tools=[greet])
response = agent.chat("Greet Alice")
print(response)
# Output: "Hello, Alice!"
```

### Tool with Validation

```python
from claude_agent_sdk import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient.

    Args:
        to: Email address of recipient
        subject: Email subject line
        body: Email body content

    Returns:
        Confirmation message
    """
    # Validate email format
    if "@" not in to:
        raise ValueError(f"Invalid email address: {to}")

    # Validate subject length
    if len(subject) > 100:
        raise ValueError("Subject too long (max 100 characters)")

    # Send email (simulated)
    return f"Email sent to {to} with subject '{subject}'"

# Use the tool
agent = Agent(tools=[send_email])
response = agent.chat("Send an email to bob@example.com with subject 'Hello' and body 'How are you?'")
print(response)
```

### Tool with Complex Logic

```python
from claude_agent_sdk import tool
from typing import List

@tool
def analyze_sentiment(text: str) -> str:
    """Analyze the sentiment of a piece of text.

    Args:
        text: The text to analyze

    Returns:
        Sentiment analysis result (positive/negative/neutral)
    """
    # Simple keyword-based sentiment analysis
    positive_words = ["good", "great", "awesome", "love", "happy"]
    negative_words = ["bad", "terrible", "hate", "sad", "angry"]

    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

# Use the tool
agent = Agent(tools=[analyze_sentiment])
response = agent.chat("Analyze the sentiment of: 'I love this product, it's great!'")
print(response)
# Output: "positive"
```

## Example 6: Writing Custom Hooks

### PreToolUse Hook

```python
from claude_agent_sdk import PreToolUseHook

class ValidationHook(PreToolUseHook):
    """Validate tool inputs before execution."""

    async def on_pre_tool_use(self, tool_use):
        # Validate calculator inputs
        if tool_use.name == "calculator":
            a = tool_use.input.get("a")
            b = tool_use.input.get("b")

            # Check for negative numbers
            if a < 0 or b < 0:
                raise ValueError("Negative numbers not allowed")

        # Allow tool use to proceed
        return tool_use

# Use the hook
agent = Agent(hooks=[ValidationHook()])
response = agent.chat("Calculate -5 + 3")
# Output: "Error: Negative numbers not allowed"
```

### PostToolUse Hook

```python
from claude_agent_sdk import PostToolUseHook

class MetricsHook(PostToolUseHook):
    """Collect metrics about tool usage."""

    def __init__(self):
        self.tool_usage = {}

    async def on_post_tool_use(self, tool_use, result):
        # Track tool usage
        tool_name = tool_use.name
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1

        return result

# Use the hook
metrics = MetricsHook()
agent = Agent(hooks=[metrics])

agent.chat("Calculate 5 + 3")
agent.chat("Calculate 10 * 2")
agent.chat("Calculate 8 / 4")

print(metrics.tool_usage)
# Output: {'calculator': 3}
```

### Combined Pre/Post Hook

```python
from claude_agent_sdk import PreToolUseHook, PostToolUseHook

class TimingHook(PreToolUseHook, PostToolUseHook):
    """Measure tool execution time."""

    def __init__(self):
        self.start_times = {}
        self.execution_times = {}

    async def on_pre_tool_use(self, tool_use):
        # Record start time
        import time
        self.start_times[tool_use.name] = time.time()
        return tool_use

    async def on_post_tool_use(self, tool_use, result):
        # Calculate execution time
        import time
        start_time = self.start_times.get(tool_use.name, 0)
        execution_time = time.time() - start_time

        if tool_use.name not in self.execution_times:
            self.execution_times[tool_use.name] = []
        self.execution_times[tool_use.name].append(execution_time)

        return result

# Use the hook
timing = TimingHook()
agent = Agent(hooks=[timing])

agent.chat("Calculate 5 + 3")

print(timing.execution_times)
# Output: {'calculator': [0.001234]}
```

## Example 7: Audit Logging

### Basic Audit Logging

```python
from hooks.audit_logger import AuditLoggerHook

# Create audit logger
logger = AuditLoggerHook(log_file="audit.log")

# Create agent with audit logger
agent = Agent(hooks=[logger])

# Perform some operations
agent.chat("Calculate 5 + 3")
agent.chat("Calculate 10 * 2")

# Read the audit log
with open("audit.log", "r") as f:
    print(f.read())
```

### Custom Audit Format

```python
from hooks.audit_logger import AuditLoggerHook
import json

class JSONAuditLogger(AuditLoggerHook):
    """Custom audit logger that outputs JSON."""

    async def on_post_tool_use(self, tool_use, result):
        log_entry = {
            "timestamp": self._get_timestamp(),
            "tool": tool_use.name,
            "inputs": tool_use.input,
            "status": "success" if result else "failed"
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return result

# Use the custom logger
logger = JSONAuditLogger(log_file="audit.json")
agent = Agent(hooks=[logger])

agent.chat("Calculate 5 + 3")

# Read the audit log
with open("audit.json", "r") as f:
    print(f.read())
```

### Audit Log Analysis

```python
from hooks.audit_logger import AuditLoggerHook

# Create agent with audit logging
logger = AuditLoggerHook(log_file="audit.log")
agent = Agent(hooks=[logger])

# Perform operations
agent.chat("Calculate 5 + 3")
agent.chat("Calculate 10 * 2")
agent.chat("Calculate 8 / 4")

# Analyze the audit log
def analyze_audit_log(log_file):
    with open(log_file, "r") as f:
        lines = f.readlines()

    tool_usage = {}
    for line in lines:
        if "Tool:" in line:
            tool_name = line.split("Tool:")[1].strip()
            if tool_name not in tool_usage:
                tool_usage[tool_name] = 0
            tool_usage[tool_name] += 1

    return tool_usage

usage = analyze_audit_log("audit.log")
print(f"Tool usage: {usage}")
# Output: Tool usage: {'calculator': 3}
```

## Example 8: Error Handling

### Tool-Level Error Handling

```python
from claude_agent_sdk import tool

@tool
def safe_calculator(operation: str, a: float, b: float) -> str:
    """Perform arithmetic operations with error handling."""
    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return "Error: Cannot divide by zero"
            result = a / b
        else:
            return f"Error: Unknown operation {operation}"

        return f"{a} {operation} {b} = {result}"

    except Exception as e:
        return f"Error: {str(e)}"

# Use the tool
agent = Agent(tools=[safe_calculator])
response = agent.chat("Calculate 10 / 0")
print(response)
# Output: "Error: Cannot divide by zero"
```

### Agent-Level Error Handling

```python
from claude_agent_sdk import Agent

agent = Agent(tools=[calculator])

try:
    response = agent.chat("Calculate 10 / 0")
    print(response)
except Exception as e:
    print(f"Agent error: {e}")

# Graceful degradation
try:
    response = agent.chat("Execute: rm -rf /")
    print(response)
except Exception as e:
    print(f"Command blocked: {e}")
```

### Hook Error Handling

```python
from claude_agent_sdk import PreToolUseHook

class SafeHook(PreToolUseHook):
    """Hook that handles errors gracefully."""

    async def on_pre_tool_use(self, tool_use):
        try:
            # Perform validation
            if tool_use.name == "calculator":
                a = tool_use.input.get("a")
                b = tool_use.input.get("b")

                if a is None or b is None:
                    raise ValueError("Missing required parameters")

            return tool_use

        except Exception as e:
            # Log error but allow execution to continue
            print(f"Hook error: {e}")
            return tool_use

# Use the safe hook
agent = Agent(hooks=[SafeHook()])
```

## Running the Examples

Each example can be copied into a Python file and run directly:

```bash
# Create example file
cat > example1.py << 'EOF'
from tools.calculator import calculator

result = calculator.invoke(
    operation="add",
    a=10,
    b=5
)
print(result)
EOF

# Run the example
python example1.py
```

Or run them interactively:

```bash
python
>>> from tools.calculator import calculator
>>> result = calculator.invoke(operation="add", a=10, b=5)
>>> print(result)
```

## Next Steps

1. **Explore the patterns** - See the main README for pattern details
2. **Read the tests** - Test files show more usage examples
3. **Build your own** - Create custom tools and hooks
4. **Read the blog post** - See `../blog/post.md` for full tutorial

## Support

For more information:
- See `README.md` for setup instructions
- Check the test files for working examples
- Read the blog post for detailed explanations
