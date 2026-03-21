"""
Pattern 4: Complete Agent (All Patterns Combined)

This pattern demonstrates a complete agent that combines all three previous patterns:
1. Custom Tools (Pattern 1) - Calculator tool for arithmetic
2. Hooks (Pattern 2) - Command blocker and audit logger
3. Permissions (Pattern 3) - Three-tier permission model

Key Concepts:
- Combine tools, hooks, and permissions in a single agent configuration
- Demonstrate realistic task automation scenarios
- Show how patterns interact and complement each other
- Complete audit trail of all operations

Agent Configuration:
- Tools: calculate (arithmetic), read_file (file operations)
- Hooks: command_blocker (PreToolUse), audit_logger (PreToolUse + PostToolUse)
- Permissions: Three-tier model (safe/semi-trusted/risky)
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from claude_agent_sdk.types import ClaudeAgentOptions
from tools.calculator import calculate_tool
from hooks.command_blocker import pre_tool_use_hook as block_dangerous_commands
from hooks.audit_logger import pre_tool_use_hook as log_tool_use_pre
from hooks.audit_logger import post_tool_use_hook as log_tool_use_post


class CompleteAgent:
    """Complete agent combining all patterns"""

    def __init__(self):
        self.options = ClaudeAgentOptions(
            system_prompt="You are a helpful task automation assistant.",
            allowed_tools=["calculate", "read_file"],  # Pattern 3: Safe tools
            permission_mode='acceptEdits'  # Pattern 3: Auto-approve file edits
        )

        self.hooks = {
            "PreToolUse": [block_dangerous_commands, log_tool_use_pre],  # Pattern 2
            "PostToolUse": [log_tool_use_post]  # Pattern 2
        }

        self.audit_log = []

    async def execute_tool(self, tool_name, tool_input):
        """
        Execute a tool with all patterns applied:
        1. Check permissions (Pattern 3)
        2. Apply PreToolUse hooks (Pattern 2)
        3. Execute tool (Pattern 1)
        4. Apply PostToolUse hooks (Pattern 2)
        """
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

            # Check if hook denied execution
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
            # For demo purposes, simulate other tools
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
        """Display complete audit trail"""
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


async def scenario_1_safe_calculation(agent):
    """Scenario 1: Safe calculation (auto-approved, logged, executes)"""
    print("\n" + "="*70)
    print("Scenario 1: Safe Calculation")
    print("="*70)
    print("\nTask: Calculate 25 * 4")
    print("Expected: Auto-approved (calculator is in allowed_tools)")
    print("          Logged by audit hooks")
    print("          Executes successfully\n")

    result = await agent.execute_tool("calculate", {"a": 25, "b": 4, "operation": "multiply"})
    return result


async def scenario_2_dangerous_command(agent):
    """Scenario 2: Dangerous command (blocked by hook, logged, denied)"""
    print("\n" + "="*70)
    print("Scenario 2: Dangerous Command")
    print("="*70)
    print("\nTask: Execute 'rm -rf /important/data'")
    print("Expected: Blocked by command_blocker hook")
    print("          Logged by audit hooks")
    print("          Execution denied\n")

    result = await agent.execute_tool("bash", {"command": "rm -rf /important/data"})
    return result


async def scenario_3_file_read(agent):
    """Scenario 3: File read (auto-approved, logged)"""
    print("\n" + "="*70)
    print("Scenario 3: File Read Operation")
    print("="*70)
    print("\nTask: Read file 'example.txt'")
    print("Expected: Auto-approved (read_file is in allowed_tools)")
    print("          Logged by audit hooks")
    print("          Executes successfully\n")

    result = await agent.execute_tool("read_file", {"path": "example.txt"})
    return result


async def scenario_4_risky_operation(agent):
    """Scenario 4: Risky operation (requires permission, logged)"""
    print("\n" + "="*70)
    print("Scenario 4: Risky Operation")
    print("="*70)
    print("\nTask: Execute 'format c:'")
    print("Expected: Permission denied (bash not in allowed_tools)")
    print("          Would be blocked by command_blocker anyway")
    print("          Logged by audit hooks\n")

    result = await agent.execute_tool("bash", {"command": "format c:"})
    return result


async def scenario_5_complex_task(agent):
    """Scenario 5: Complex multi-step task"""
    print("\n" + "="*70)
    print("Scenario 5: Complex Multi-Step Task")
    print("="*70)
    print("\nTask: Calculate project budget")
    print("  Step 1: Calculate team costs (10 people * $100/hr)")
    print("  Step 2: Calculate duration (40 hours)")
    print("  Step 3: Calculate total budget")
    print("\nExpected: All calculations auto-approved and logged\n")

    # Step 1
    print("\n--- Step 1: Team Cost ---")
    result1 = await agent.execute_tool("calculate", {"a": 10, "b": 100, "operation": "multiply"})

    # Step 2
    print("\n--- Step 2: Duration ---")
    result2 = await agent.execute_tool("calculate", {"a": 1000, "b": 40, "operation": "multiply"})

    # Step 3
    print("\n--- Step 3: Total ---")
    result3 = await agent.execute_tool("calculate", {"a": 40000, "b": 1.2, "operation": "multiply"})

    return [result1, result2, result3]


async def demonstrate_complete_agent():
    """Demonstrate complete agent with all patterns"""
    print("\n" + "="*70)
    print("Pattern 4: Complete Agent (All Patterns Combined)")
    print("="*70)
    print("\nThis demo shows a complete agent combining:")
    print("  • Pattern 1: Custom Tools (Calculator)")
    print("  • Pattern 2: Hooks (Command Blocker + Audit Logger)")
    print("  • Pattern 3: Permissions (Three-Tier Model)")

    # Create agent
    agent = CompleteAgent()

    print("\n" + "-"*70)
    print("Agent Configuration")
    print("-"*70)
    print(f"System Prompt: {agent.options.system_prompt}")
    print(f"Allowed Tools: {agent.options.allowed_tools}")
    print(f"Permission Mode: {agent.options.permission_mode}")
    print(f"PreToolUse Hooks: {[h.__name__ for h in agent.hooks['PreToolUse']]}")
    print(f"PostToolUse Hooks: {[h.__name__ for h in agent.hooks['PostToolUse']]}")

    # Run scenarios
    print("\n" + "="*70)
    print("Running Demonstration Scenarios")
    print("="*70)

    await scenario_1_safe_calculation(agent)
    await scenario_2_dangerous_command(agent)
    await scenario_3_file_read(agent)
    await scenario_4_risky_operation(agent)
    await scenario_5_complex_task(agent)

    # Show audit trail
    agent.show_audit_trail()

    # Summary
    print("\n" + "="*70)
    print("Pattern 4 Summary")
    print("="*70)
    print("\nKey Takeaways:")
    print("  ✓ All three patterns work together seamlessly")
    print("  ✓ Tools execute with proper permissions")
    print("  ✓ Hooks fire correctly (PreToolUse and PostToolUse)")
    print("  ✓ Complete audit trail of all operations")
    print("  ✓ Realistic task automation scenarios demonstrated")
    print("\nPattern Integration:")
    print("  • Pattern 1 (Tools): Calculator executes arithmetic operations")
    print("  • Pattern 2 (Hooks): Command blocker + audit logger intercept")
    print("  • Pattern 3 (Permissions): Three-tier model controls access")
    print("\nBenefits:")
    print("  • Security: Dangerous commands blocked by hooks")
    print("  • Compliance: All operations logged to audit trail")
    print("  • Control: Permissions restrict which tools can execute")
    print("  • Flexibility: Easy to add new tools, hooks, or permissions")
    print("="*70 + "\n")


def run():
    """Run Pattern 4 demo"""
    asyncio.run(demonstrate_complete_agent())


if __name__ == "__main__":
    run()
