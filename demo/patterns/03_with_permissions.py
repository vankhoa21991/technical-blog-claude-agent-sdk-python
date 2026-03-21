"""
Pattern 3: Permission Management

This pattern demonstrates how to control tool access using a three-tier permission model:
1. Safe Tools (allowed_tools) - Auto-approved without prompting
2. Semi-trusted (permission_mode='acceptEdits') - File operations auto-approved
3. Risky Tools (not in allowed_tools) - Require explicit permission

Key Concepts:
- allowed_tools: List of tool names that execute without permission prompts
- permission_mode: Controls auto-approval behavior ('acceptEdits', 'auto', 'default')
- Three-tier model: Safe / Semi-trusted / Risky
- Runtime permission control: can_use_tool callback for custom permission logic
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from claude_agent_sdk.types import ClaudeAgentOptions
from tools.calculator import calculate_tool


class PermissionDemoHandler:
    """Demo permission handler that tracks permission requests"""

    def __init__(self):
        self.permission_requests = []

    async def request_permission(self, tool_name, tool_input):
        """Simulate permission request"""
        self.permission_requests.append({
            "tool_name": tool_name,
            "tool_input": tool_input
        })
        return True  # Grant for demo


async def demonstrate_permission_configuration():
    """Demonstrate basic permission configuration"""
    print("\n" + "="*70)
    print("Pattern 3: Permission Management")
    print("="*70)
    print("\nPermissions control which tools can execute without user approval.")
    print("This demo shows the three-tier permission model:\n")

    print("-" * 70)
    print("1. Permission Configuration")
    print("-" * 70)

    # Configure with safe tools only
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate", "read_file"],  # Safe tools
        permission_mode='acceptEdits'  # Auto-approve file edits
    )

    print("\nConfiguration:")
    print(f"  allowed_tools: {options.allowed_tools}")
    print(f"  permission_mode: {options.permission_mode}")
    print("\nExplanation:")
    print("  • Tools in allowed_tools execute WITHOUT permission prompts")
    print("  • permission_mode='acceptEdits' auto-approves file operations")
    print("  • Tools NOT in allowed_tools require explicit permission")


async def demonstrate_safe_tools():
    """Demonstrate safe tools (auto-approved)"""
    print("\n" + "-" * 70)
    print("2. Safe Tools (Tier 1: Auto-Approved)")
    print("-" * 70)

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate"],
        permission_mode='acceptEdits'
    )

    handler = PermissionDemoHandler()

    # Test calculator (safe tool)
    print("\nTest: Calculator tool (in allowed_tools)")
    tool_name = "calculate"
    tool_input = {"a": 15, "b": 3, "operation": "multiply"}

    is_allowed = tool_name in options.allowed_tools
    print(f"  Tool: {tool_name}")
    print(f"  Input: {tool_input}")
    print(f"  In allowed_tools: {is_allowed}")
    print(f"  Permission required: {'No' if is_allowed else 'Yes'}")

    if is_allowed:
        print(f"\n  ✓ Auto-approved (no permission prompt)")
        result = await calculate_tool.handler(tool_input)
        print(f"  Result: {result['content'][0]['text']}")
    else:
        print(f"\n  ✗ Would require permission prompt")


async def demonstrate_semi_trusted_operations():
    """Demonstrate semi-trusted operations (permission_mode)"""
    print("\n" + "-" * 70)
    print("3. Semi-trusted Operations (Tier 2: Auto-Approved with Mode)")
    print("-" * 70)

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate"],
        permission_mode='acceptEdits'  # Auto-approve file operations
    )

    print("\nConfiguration: permission_mode='acceptEdits'")
    print("\nSemi-trusted file operations:")
    file_operations = [
        ("write_file", {"path": "example.txt", "content": "Hello"}),
        ("edit_file", {"path": "example.txt", "changes": "World"}),
    ]

    for op_name, op_input in file_operations:
        is_auto_approved = options.permission_mode == 'acceptEdits'
        print(f"\n  Operation: {op_name}")
        print(f"  Auto-approved: {is_auto_approved}")
        if is_auto_approved:
            print(f"  ✓ File edit auto-approved via permission_mode")


async def demonstrate_risky_tools():
    """Demonstrate risky tools (require permission)"""
    print("\n" + "-" * 70)
    print("4. Risky Tools (Tier 3: Require Permission)")
    print("-" * 70)

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate", "read_file"],  # bash is NOT in this list
        permission_mode='acceptEdits'
    )

    handler = PermissionDemoHandler()

    risky_tools = [
        ("bash", {"command": "ls -la"}),
        ("delete_file", {"path": "important.txt"}),
        ("format_disk", {"device": "/dev/sda1"}),
    ]

    print("\nRisky tools NOT in allowed_tools:")
    for tool_name, tool_input in risky_tools:
        is_allowed = tool_name in options.allowed_tools
        print(f"\n  Tool: {tool_name}")
        print(f"  Input: {tool_input}")
        print(f"  In allowed_tools: {is_allowed}")

        if not is_allowed:
            print(f"  ⚠ Permission REQUIRED")
            # Simulate permission request
            await handler.request_permission(tool_name, tool_input)
            print(f"  → Permission request logged")


async def demonstrate_three_tier_model():
    """Demonstrate complete three-tier permission model"""
    print("\n" + "-" * 70)
    print("5. Three-Tier Permission Model Summary")
    print("-" * 70)

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate", "read_file"],
        permission_mode='acceptEdits'
    )

    print("\nTier 1: Safe Tools (allowed_tools)")
    print("  Status: Auto-approved without prompting")
    for tool in options.allowed_tools:
        print(f"    ✓ {tool}")

    print("\nTier 2: Semi-trusted (permission_mode='acceptEdits')")
    print("  Status: Auto-approved via permission mode")
    semi_trusted = ["write_file", "edit_file", "create_file"]
    for tool in semi_trusted:
        print(f"    ✓ {tool}")

    print("\nTier 3: Risky Tools (NOT in allowed_tools)")
    print("  Status: Require explicit permission")
    risky = ["bash", "delete_file", "format_disk", "network"]
    for tool in risky:
        print(f"    ⚠ {tool}")


async def demonstrate_permission_filtering():
    """Demonstrate how permission filtering works"""
    print("\n" + "-" * 70)
    print("6. Permission Filtering in Action")
    print("-" * 70)

    scenarios = [
        {
            "name": "Strict Mode (no auto-approved tools)",
            "allowed_tools": [],
            "test_tools": ["calculate", "bash", "read_file"]
        },
        {
            "name": "Balanced Mode (calculator + read)",
            "allowed_tools": ["calculate", "read_file"],
            "test_tools": ["calculate", "bash", "read_file"]
        },
        {
            "name": "Permissive Mode (many tools allowed)",
            "allowed_tools": ["calculate", "read_file", "write_file", "edit_file"],
            "test_tools": ["calculate", "bash", "write_file"]
        }
    ]

    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        options = ClaudeAgentOptions(
            system_prompt="You are a helpful assistant.",
            allowed_tools=scenario["allowed_tools"],
            permission_mode='acceptEdits'
        )

        print(f"  allowed_tools: {scenario['allowed_tools']}")
        print(f"\n  Tool access:")
        for tool in scenario["test_tools"]:
            is_allowed = tool in options.allowed_tools
            status = "ALLOWED ✓" if is_allowed else "REQUIRES PERMISSION ⚠"
            print(f"    {tool}: {status}")


async def demonstrate_use_cases():
    """Demonstrate practical use cases"""
    print("\n" + "-" * 70)
    print("7. Practical Use Cases")
    print("-" * 70)

    use_cases = [
        {
            "name": "Production Agent (Safe Only)",
            "allowed_tools": ["calculate"],
            "permission_mode": "default",
            "description": "Only allow calculator, prompt for everything else"
        },
        {
            "name": "Development Agent (File Edits OK)",
            "allowed_tools": ["calculate", "read_file", "write_file"],
            "permission_mode": "acceptEdits",
            "description": "Allow calculator + file operations, block bash"
        },
        {
            "name": "Sandboxed Agent (Fully Autonomous)",
            "allowed_tools": ["calculate", "read_file", "write_file", "bash"],
            "permission_mode": "auto",
            "description": "Auto-approve all tools (use with caution!)"
        }
    ]

    for use_case in use_cases:
        print(f"\n{use_case['name']}:")
        options = ClaudeAgentOptions(
            system_prompt="You are a helpful assistant.",
            allowed_tools=use_case["allowed_tools"],
            permission_mode=use_case["permission_mode"]
        )
        print(f"  Configuration:")
        print(f"    allowed_tools: {use_case['allowed_tools']}")
        print(f"    permission_mode: {use_case['permission_mode']}")
        print(f"  Use case: {use_case['description']}")


async def demonstrate_permissions():
    """Main demonstration function"""
    await demonstrate_permission_configuration()
    await demonstrate_safe_tools()
    await demonstrate_semi_trusted_operations()
    await demonstrate_risky_tools()
    await demonstrate_three_tier_model()
    await demonstrate_permission_filtering()
    await demonstrate_use_cases()

    # Summary
    print("\n" + "="*70)
    print("Pattern 3 Summary")
    print("="*70)
    print("\nKey Takeaways:")
    print("  ✓ allowed_tools controls which tools execute without prompts")
    print("  ✓ permission_mode='acceptEdits' auto-approves file operations")
    print("  ✓ Three-tier model: Safe / Semi-trusted / Risky")
    print("  ✓ Tools NOT in allowed_tools trigger permission requests")
    print("  ✓ can_use_tool callback enables custom permission logic")
    print("\nPermission Tiers:")
    print("  Tier 1 (Safe): Tools in allowed_tools → Auto-approved")
    print("  Tier 2 (Semi-trusted): File operations via permission_mode → Auto-approved")
    print("  Tier 3 (Risky): Everything else → Requires permission")
    print("\nUse Cases:")
    print("  • Production: Restrict to safe tools only")
    print("  • Development: Allow file edits with acceptEdits")
    print("  • Autonomous: Use permission_mode='auto' (caution!)")
    print("="*70 + "\n")


def run():
    """Run Pattern 3 demo"""
    asyncio.run(demonstrate_permissions())


if __name__ == "__main__":
    run()
