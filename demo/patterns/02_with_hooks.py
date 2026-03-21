"""
Pattern 2: Hooks for Control

This pattern demonstrates how to use hooks to intercept and control
agent behavior before and after tool execution.

Hooks demonstrated:
1. Command Blocker - Blocks dangerous bash commands
2. Audit Logger - Logs all tool invocations

Key Concepts:
- Hooks execute before (PreToolUse) or after (PostToolUse) tool execution
- Hooks can deny execution by returning permissionDecision: "deny"
- Hooks can modify tool inputs/outputs
- Hooks are ideal for security, logging, and monitoring
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from tools.calculator import calculate_tool
from hooks.command_blocker import pre_tool_use_hook as block_dangerous_commands
from hooks.audit_logger import pre_tool_use_hook as log_tool_use_pre
from hooks.audit_logger import post_tool_use_hook as log_tool_use_post


async def demonstrate_hooks():
    """Demonstrate hooks in action"""
    print("\n" + "="*70)
    print("Pattern 2: Hooks for Control")
    print("="*70)
    print("\nHooks allow you to intercept and control agent behavior.")
    print("This demo shows two hooks:")
    print("  1. Command Blocker - Blocks dangerous bash commands")
    print("  2. Audit Logger - Logs all tool invocations\n")

    # Hook 1: Command Blocker
    print("-" * 70)
    print("Hook 1: Command Blocker")
    print("-" * 70)

    print("\n1. Testing safe command (should be ALLOWED):")
    safe_command = {
        "tool_name": "bash",
        "tool_input": {"command": "ls -la"}
    }
    result = await block_dangerous_commands(safe_command, "test-id-1", {})
    if result == {}:
        print("   ✓ Safe command allowed to proceed")
    else:
        print(f"   ✗ Unexpected result: {result}")

    print("\n2. Testing dangerous command (should be BLOCKED):")
    dangerous_commands = [
        {"tool_name": "bash", "tool_input": {"command": "rm -rf /important/data"}},
        {"tool_name": "bash", "tool_input": {"command": ":(){:|:&};:"}},  # Fork bomb
    ]

    for dangerous_command in dangerous_commands:
        result = await block_dangerous_commands(dangerous_command, "test-id-2", {})
        if result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny":
            print(f"   ✓ Dangerous command blocked: {dangerous_command['tool_input']['command']}")
            print(f"   Reason: {result['hookSpecificOutput']['permissionDecisionReason']}")
        else:
            print(f"   ✗ Command was not blocked: {result}")

    # Hook 2: Audit Logger (PreToolUse)
    print("\n" + "-" * 70)
    print("Hook 2: Audit Logger (PreToolUse)")
    print("-" * 70)
    print("\nLogging tool invocations BEFORE execution... (check console output below)")

    # Simulate tool invocations
    tool_calls = [
        {"tool_name": "calculator", "tool_input": {"a": 10, "b": 5, "operation": "multiply"}},
        {"tool_name": "bash", "tool_input": {"command": "echo 'Hello, Hooks!'"}},
        {"tool_name": "calculator", "tool_input": {"a": 100, "b": 25, "operation": "divide"}},
    ]

    for i, tool_call in enumerate(tool_calls, 1):
        print(f"\n{i}. Calling: {tool_call['tool_name']}")
        await log_tool_use_pre(tool_call, f"tool-use-{i}", {})

    print("\n✓ All tool invocations logged to audit.log (PreToolUse)")

    # Hook 2b: Audit Logger (PostToolUse)
    print("\n" + "-" * 70)
    print("Hook 2b: Audit Logger (PostToolUse)")
    print("-" * 70)
    print("\nLogging tool execution results AFTER execution...")

    # Simulate tool outputs
    tool_outputs = [
        ("tool-use-1", {"content": [{"type": "text", "text": "50"}]}),
        ("tool-use-2", {"content": [{"type": "text", "text": "Hello, Hooks!"}]}),
        ("tool-use-3", {"content": [{"type": "text", "text": "4"}]}),
    ]

    for tool_use_id, tool_output in tool_outputs:
        await log_tool_use_post(tool_use_id, tool_output, {})

    print("\n✓ All tool results logged to audit.log (PostToolUse)")

    # Demonstrate with calculator tool
    print("\n" + "-" * 70)
    print("Putting It Together: Hooks + Tools")
    print("-" * 70)

    print("\nDemonstrating hooks with the calculator tool:")
    print("  - Audit logger will record the tool use")
    print("  - Command blocker will check for dangerous commands")

    calculator_input = {
        "tool_name": "calculator",
        "tool_input": {"a": 42, "b": 8, "operation": "add"}
    }

    print(f"\nTool call: {calculator_input['tool_name']}")
    print(f"Input: {calculator_input['tool_input']}")

    # Apply audit logger pre-hook
    print("\n[Applying Audit Logger PreToolUse Hook]")
    await log_tool_use_pre(calculator_input, "calc-use-1", {})

    # Apply command blocker hook (should allow calculator)
    print("[Applying Command Blocker Hook]")
    blocker_result = await block_dangerous_commands(calculator_input, "calc-use-1", {})

    if blocker_result == {}:
        print("✓ Command blocker allows calculator tool to proceed")

        # Execute the actual tool
        tool_result = await calculate_tool.handler(calculator_input["tool_input"])
        print(f"Tool result: {tool_result['content'][0]['text']}")

        # Apply audit logger post-hook
        print("\n[Applying Audit Logger PostToolUse Hook]")
        await log_tool_use_post("calc-use-1", tool_result, {})
        print("✓ Tool result logged")
    else:
        print(f"✗ Unexpected block: {blocker_result}")

    # Summary
    print("\n" + "="*70)
    print("Pattern 2 Summary")
    print("="*70)
    print("\nKey Takeaways:")
    print("  ✓ Hooks intercept tool execution (PreToolUse/PostToolUse)")
    print("  ✓ Hooks use SDK interface: pre_tool_use_hook and post_tool_use_hook")
    print("  ✓ Hooks can deny execution for security/safety")
    print("  ✓ Hooks can log/audit all tool invocations and results")
    print("  ✓ Hooks return empty dict for no-op, or dict with decisions")
    print("\nUse Cases:")
    print("  • Security: Block dangerous commands (rm -rf, fork bombs)")
    print("  • Compliance: Audit all tool usage and results")
    print("  • Debugging: Log inputs/outputs with timestamps")
    print("  • Monitoring: Track agent behavior and performance")
    print("="*70 + "\n")


def run():
    """Run Pattern 2 demo"""
    asyncio.run(demonstrate_hooks())


if __name__ == "__main__":
    run()
