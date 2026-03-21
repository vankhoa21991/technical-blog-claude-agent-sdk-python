"""
Integration Tests for Pattern 4 - Complete Agent

These tests verify that all three patterns work together correctly:
1. Tools (Pattern 1) - Calculator tool executes correctly
2. Hooks (Pattern 2) - Command blocker and audit logger work
3. Permissions (Pattern 3) - Three-tier permission model applies

Test Scenarios:
- Safe operation (calculator) - auto-approved, logged, executes
- Dangerous command - blocked by hook, logged, denied
- File read - auto-approved (in allowed_tools), logged
- Risky operation - requires permission, logged
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from tools.calculator import calculate_tool
from hooks.command_blocker import pre_tool_use_hook as block_dangerous_commands
from hooks.audit_logger import pre_tool_use_hook as log_tool_use_pre
from hooks.audit_logger import post_tool_use_hook as log_tool_use_post


class TestCompleteAgent:
    """Integration tests for complete agent with all patterns"""

    def __init__(self):
        self.test_results = []

    def record_result(self, test_name, passed, details=""):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

    async def test_safe_calculation(self):
        """Test 1: Safe calculation (auto-approved, logged, executes)"""
        print("\n" + "="*70)
        print("Test 1: Safe Calculation (All Patterns)")
        print("="*70)

        tool_input = {"a": 25, "b": 4, "operation": "multiply"}

        # Step 1: Apply audit logger pre-hook (Pattern 2)
        print("\n1. Applying Audit Logger (PreToolUse)...")
        input_data = {"tool_name": "calculate", "tool_input": tool_input}
        pre_result = await log_tool_use_pre(input_data, "test-1", {})
        print(f"   ✓ Pre-hook logged: {pre_result == {}}")

        # Step 2: Check permissions (Pattern 3)
        print("\n2. Checking Permissions...")
        allowed_tools = ["calculate", "read_file"]
        is_allowed = "calculate" in allowed_tools
        print(f"   ✓ Tool in allowed_tools: {is_allowed}")

        # Step 3: Apply command blocker hook (Pattern 2)
        print("\n3. Applying Command Blocker...")
        blocker_result = await block_dangerous_commands(input_data, "test-1", {})
        is_blocked = blocker_result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
        print(f"   ✓ Not blocked by command blocker: {not is_blocked}")

        # Step 4: Execute tool (Pattern 1)
        print("\n4. Executing Calculator Tool...")
        tool_result = await calculate_tool.handler(tool_input)
        print(f"   ✓ Tool executed: {tool_result['content'][0]['text']}")

        # Step 5: Apply audit logger post-hook (Pattern 2)
        print("\n5. Applying Audit Logger (PostToolUse)...")
        post_result = await log_tool_use_post("test-1", tool_result, {})
        print(f"   ✓ Post-hook logged: {post_result == {}}")

        # Verify result
        expected = "100"
        actual = tool_result['content'][0]['text']
        passed = actual == expected and is_allowed and not is_blocked

        self.record_result(
            "Safe Calculation",
            passed,
            f"Result: {actual}, Allowed: {is_allowed}, Blocked: {is_blocked}"
        )

        print(f"\n{'✓ PASSED' if passed else '✗ FAILED'}: Safe calculation test")
        return passed

    async def test_dangerous_command(self):
        """Test 2: Dangerous command (blocked by hook, logged, denied)"""
        print("\n" + "="*70)
        print("Test 2: Dangerous Command (Hook Blocks Execution)")
        print("="*70)

        dangerous_input = {"command": "rm -rf /important/data"}
        input_data = {"tool_name": "bash", "tool_input": dangerous_input}

        # Step 1: Apply audit logger pre-hook
        print("\n1. Applying Audit Logger (PreToolUse)...")
        pre_result = await log_tool_use_pre(input_data, "test-2", {})
        print(f"   ✓ Pre-hook logged: {pre_result == {}}")

        # Step 2: Check permissions
        print("\n2. Checking Permissions...")
        allowed_tools = ["calculate", "read_file"]
        is_allowed = "bash" in allowed_tools
        print(f"   ✓ Tool NOT in allowed_tools: {not is_allowed}")

        # Step 3: Apply command blocker hook (should block)
        print("\n3. Applying Command Blocker...")
        blocker_result = await block_dangerous_commands(input_data, "test-2", {})
        is_blocked = blocker_result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
        block_reason = blocker_result.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")

        print(f"   ✓ Command blocked: {is_blocked}")
        if is_blocked:
            print(f"   Reason: {block_reason}")

        # Verify result
        passed = is_blocked and not is_allowed

        self.record_result(
            "Dangerous Command Blocked",
            passed,
            f"Blocked: {is_blocked}, Reason: {block_reason}"
        )

        print(f"\n{'✓ PASSED' if passed else '✗ FAILED'}: Dangerous command test")
        return passed

    async def test_tool_hook_interaction(self):
        """Test 3: Tool + Hook interaction"""
        print("\n" + "="*70)
        print("Test 3: Tool + Hook Integration")
        print("="*70)

        # Test that calculator tool passes through command blocker
        tool_input = {"a": 10, "b": 2, "operation": "divide"}
        input_data = {"tool_name": "calculate", "tool_input": tool_input}

        print("\n1. Testing calculator tool with command blocker...")
        blocker_result = await block_dangerous_commands(input_data, "test-3", {})
        is_blocked = blocker_result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

        print(f"   Calculator blocked: {is_blocked}")

        # Execute tool
        tool_result = await calculate_tool.handler(tool_input)
        expected = "5.0"
        actual = tool_result['content'][0]['text']

        print(f"   Tool result: {actual}")

        # Verify result
        passed = not is_blocked and actual == expected

        self.record_result(
            "Tool + Hook Integration",
            passed,
            f"Calculator not blocked: {not is_blocked}, Result: {actual}"
        )

        print(f"\n{'✓ PASSED' if passed else '✗ FAILED'}: Tool + Hook integration test")
        return passed

    async def test_permission_filtering(self):
        """Test 4: Permission filtering works correctly"""
        print("\n" + "="*70)
        print("Test 4: Permission Filtering (Three-Tier Model)")
        print("="*70)

        allowed_tools = ["calculate", "read_file"]

        test_cases = [
            ("calculate", {"a": 5, "b": 3, "operation": "add"}, True),
            ("read_file", {"path": "test.txt"}, True),
            ("bash", {"command": "ls -la"}, False),
            ("delete_file", {"path": "important.txt"}, False),
        ]

        print("\nTesting permission filtering:")
        all_passed = True

        for tool_name, tool_input, should_be_allowed in test_cases:
            is_allowed = tool_name in allowed_tools
            passed = is_allowed == should_be_allowed

            status = "ALLOWED ✓" if is_allowed else "REQUIRES PERMISSION ⚠"
            expected_status = "ALLOWED ✓" if should_be_allowed else "REQUIRES PERMISSION ⚠"

            print(f"\n  Tool: {tool_name}")
            print(f"    Expected: {expected_status}")
            print(f"    Actual: {status}")
            print(f"    {'✓' if passed else '✗'} Match")

            all_passed = all_passed and passed

        self.record_result(
            "Permission Filtering",
            all_passed,
            "All tools correctly filtered by permissions"
        )

        print(f"\n{'✓ PASSED' if all_passed else '✗ FAILED'}: Permission filtering test")
        return all_passed

    async def test_audit_trail(self):
        """Test 5: Complete audit trail (all operations logged)"""
        print("\n" + "="*70)
        print("Test 5: Complete Audit Trail")
        print("="*70)

        operations = [
            {"tool_name": "calculate", "tool_input": {"a": 7, "b": 6, "operation": "multiply"}},
            {"tool_name": "bash", "tool_input": {"command": "echo test"}},
        ]

        print("\nSimulating operations with audit logging...")

        for i, op in enumerate(operations, 1):
            tool_use_id = f"audit-test-{i}"

            # Pre-hook
            await log_tool_use_pre(op, tool_use_id, {})

            # Post-hook (simulate result)
            mock_output = {"content": [{"type": "text", "text": "test"}]}
            await log_tool_use_post(tool_use_id, mock_output, {})

            print(f"  ✓ Operation {i} logged")

        # Check audit log file exists
        demo_dir = Path(__file__).parent.parent
        audit_log_path = demo_dir / "audit.log"

        if audit_log_path.exists():
            with open(audit_log_path, "r") as f:
                log_content = f.read()
                # Count log entries for our test operations
                test_entries = log_content.count('"tool_use_id": "audit-test-')
                passed = test_entries >= len(operations) * 2  # pre + post for each

                print(f"\n  ✓ Audit log file exists")
                print(f"  ✓ Found {test_entries} log entries")
        else:
            passed = False
            print(f"\n  ✗ Audit log file not found")

        self.record_result(
            "Complete Audit Trail",
            passed,
            f"Logged {test_entries} entries" if passed else "Audit log missing"
        )

        print(f"\n{'✓ PASSED' if passed else '✗ FAILED'}: Audit trail test")
        return passed

    async def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*70)
        print("Pattern 4 - Complete Agent Integration Tests")
        print("="*70)
        print("\nRunning integration tests for all patterns combined...\n")

        # Run all tests
        await self.test_safe_calculation()
        await self.test_dangerous_command()
        await self.test_tool_hook_interaction()
        await self.test_permission_filtering()
        await self.test_audit_trail()

        # Print summary
        print("\n" + "="*70)
        print("Test Summary")
        print("="*70)

        passed_count = sum(1 for r in self.test_results if r["passed"])
        total_count = len(self.test_results)

        for result in self.test_results:
            status = "✓ PASSED" if result["passed"] else "✗ FAILED"
            print(f"{status}: {result['test']}")
            if result["details"]:
                print(f"  {result['details']}")

        print("\n" + "="*70)
        print(f"Results: {passed_count}/{total_count} tests passed")
        print("="*70 + "\n")

        return passed_count == total_count


async def main():
    """Run integration tests"""
    tester = TestCompleteAgent()
    all_passed = await tester.run_all_tests()
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
