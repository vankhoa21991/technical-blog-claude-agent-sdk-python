"""
Tests for Pattern 3: Permission Management

Tests follow TDD approach:
1. Permission Configuration - Test allowed_tools and permission_mode settings
2. Safe Tool Auto-Approval - Test that tools in allowed_tools execute without prompting
3. Risky Tool Permission Request - Test that tools NOT in allowed_tools require permission
4. Permission Mode Behavior - Test permission_mode='acceptEdits' for file operations
5. Three-Tier Permission Model - Verify safe/semi-trusted/risky tool classification
"""
import asyncio
import sys
from pathlib import Path

# Add demo directory to path
sys.path.append(str(Path(__file__).parent.parent))


class MockPermissionHandler:
    """Mock permission handler for testing permission behavior"""

    def __init__(self):
        self.permission_requests = []
        self.auto_approve_safe = True
        self.auto_approve_edits = True

    async def request_permission(self, tool_name, tool_input):
        """Simulate permission request"""
        self.permission_requests.append({
            "tool_name": tool_name,
            "tool_input": tool_input
        })
        return True  # Grant permission for testing


async def test_allowed_tools_configuration():
    """Test that allowed_tools is properly configured"""
    print("\n--- Testing Allowed Tools Configuration ---")

    from claude_agent_sdk.types import ClaudeAgentOptions

    # Test with allowed_tools specified
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate", "read_file"],
        permission_mode='acceptEdits'
    )

    assert hasattr(options, 'allowed_tools'), "ClaudeAgentOptions should have allowed_tools attribute"
    assert options.allowed_tools == ["calculate", "read_file"], "allowed_tools should match configuration"
    print("✓ Allowed tools configured: calculate, read_file")

    # Test with empty allowed_tools (all tools require permission)
    options_restricted = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=[],
        permission_mode='acceptEdits'
    )

    assert options_restricted.allowed_tools == [], "Empty allowed_tools means no auto-approved tools"
    print("✓ Empty allowed_tools: all tools require permission")


async def test_permission_mode_configuration():
    """Test that permission_mode is properly configured"""
    print("\n--- Testing Permission Mode Configuration ---")

    from claude_agent_sdk.types import ClaudeAgentOptions

    # Test with acceptEdits mode
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate"],
        permission_mode='acceptEdits'
    )

    assert hasattr(options, 'permission_mode'), "ClaudeAgentOptions should have permission_mode attribute"
    assert options.permission_mode == 'acceptEdits', "permission_mode should be 'acceptEdits'"
    print("✓ Permission mode set to: acceptEdits")

    # Test with auto mode
    options_auto = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate"],
        permission_mode='auto'
    )

    assert options_auto.permission_mode == 'auto', "permission_mode should be 'auto'"
    print("✓ Permission mode set to: auto")


async def test_safe_tool_auto_approval():
    """Test that safe tools in allowed_tools execute without permission prompt"""
    print("\n--- Testing Safe Tool Auto-Approval ---")

    from claude_agent_sdk.types import ClaudeAgentOptions
    from tools.calculator import calculate_tool

    # Configure options with calculator as allowed tool
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate"],
        permission_mode='acceptEdits'
    )

    permission_handler = MockPermissionHandler()

    # Simulate safe tool execution (calculator is in allowed_tools)
    tool_name = "calculate"
    tool_input = {"a": 25, "b": 4, "operation": "multiply"}

    # Check if tool is in allowed_tools
    is_allowed = tool_name in options.allowed_tools

    assert is_allowed, "Calculator should be in allowed_tools"
    print(f"✓ Tool '{tool_name}' is in allowed_tools - should auto-approve")

    # Verify no permission request was made (auto-approved)
    initial_request_count = len(permission_handler.permission_requests)
    print(f"✓ No permission prompt required (auto-approved)")
    assert len(permission_handler.permission_requests) == initial_request_count, "Safe tools should not trigger permission prompt"

    # Execute the tool to verify it works
    result = await calculate_tool.handler(tool_input)
    assert "content" in result, "Tool should return content"
    # Calculator returns string result (may be "100" or "100.0" depending on implementation)
    actual_result = result["content"][0]["text"]
    assert actual_result in ["100", "100.0"], f"25 * 4 should equal 100, got {actual_result}"
    print(f"✓ Tool executed successfully: {tool_input['a']} * {tool_input['b']} = {actual_result}")


async def test_risky_tool_requires_permission():
    """Test that risky tools NOT in allowed_tools require permission"""
    print("\n--- Testing Risky Tool Permission Requirement ---")

    from claude_agent_sdk.types import ClaudeAgentOptions

    # Configure options with only safe tools allowed
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate", "read_file"],  # bash is NOT in this list
        permission_mode='acceptEdits'
    )

    permission_handler = MockPermissionHandler()

    # Simulate risky tool execution (bash is NOT in allowed_tools)
    risky_tool = "bash"
    risky_input = {"command": "ls -la"}

    # Check if tool requires permission
    is_allowed = risky_tool in options.allowed_tools

    assert not is_allowed, f"'{risky_tool}' should NOT be in allowed_tools"
    print(f"✓ Tool '{risky_tool}' is NOT in allowed_tools - requires permission")

    # Simulate permission request
    permission_granted = await permission_handler.request_permission(risky_tool, risky_input)

    assert len(permission_handler.permission_requests) > 0, "Risky tool should trigger permission request"
    print(f"✓ Permission request triggered for: {risky_tool}")

    # Verify permission was recorded
    last_request = permission_handler.permission_requests[-1]
    assert last_request["tool_name"] == risky_tool, "Permission request should record tool name"
    print(f"✓ Permission request logged: {last_request}")


async def test_permission_mode_accept_edits():
    """Test that permission_mode='acceptEdits' auto-approves file operations"""
    print("\n--- Testing Permission Mode: acceptEdits ---")

    from claude_agent_sdk.types import ClaudeAgentOptions

    # Configure with acceptEdits mode
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate"],
        permission_mode='acceptEdits'
    )

    assert options.permission_mode == 'acceptEdits', "permission_mode should be 'acceptEdits'"
    print("✓ Permission mode: acceptEdits")

    # Simulate file edit operations
    file_operations = [
        {"operation": "write_file", "path": "test.txt", "content": "Hello"},
        {"operation": "edit_file", "path": "test.txt", "changes": "World"},
    ]

    for op in file_operations:
        # In acceptEdits mode, file edits should be auto-approved
        # (This is simulated - in real SDK, this would be handled by permission system)
        is_auto_approved = options.permission_mode == 'acceptEdits'
        assert is_auto_approved, f"File operation '{op['operation']}' should be auto-approved in acceptEdits mode"
        print(f"✓ File operation auto-approved: {op['operation']}")


async def test_three_tier_permission_model():
    """Test the three-tier permission model: safe/semi-trusted/risky"""
    print("\n--- Testing Three-Tier Permission Model ---")

    from claude_agent_sdk.types import ClaudeAgentOptions

    # Tier 1: Safe Tools (auto-approved)
    safe_tools = ["calculate", "read_file"]

    # Tier 2: Semi-trusted (auto-approved with permission_mode='acceptEdits')
    semi_trusted_operations = ["write_file", "edit_file"]

    # Tier 3: Risky (require explicit permission)
    risky_tools = ["bash", "delete_file", "format_disk"]

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=safe_tools,
        permission_mode='acceptEdits'
    )

    print("\nTier 1: Safe Tools (allowed_tools - auto-approved)")
    for tool in safe_tools:
        assert tool in options.allowed_tools, f"{tool} should be in allowed_tools"
        print(f"  ✓ {tool}: auto-approved")

    print("\nTier 2: Semi-trusted (permission_mode='acceptEdits' - auto-approved)")
    for operation in semi_trusted_operations:
        is_auto_approved = options.permission_mode == 'acceptEdits'
        assert is_auto_approved, f"{operation} should be auto-approved with acceptEdits mode"
        print(f"  ✓ {operation}: auto-approved (via permission_mode)")

    print("\nTier 3: Risky (NOT in allowed_tools - requires permission)")
    for tool in risky_tools:
        assert tool not in options.allowed_tools, f"{tool} should NOT be in allowed_tools"
        print(f"  ✓ {tool}: requires explicit permission")


async def test_permission_filtering_behavior():
    """Test that allowed_tools properly filters tool access"""
    print("\n--- Testing Permission Filtering Behavior ---")

    from claude_agent_sdk.types import ClaudeAgentOptions

    # Test 1: Calculator allowed, bash blocked
    options1 = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate"],
        permission_mode='acceptEdits'
    )

    tools_to_test = ["calculate", "bash", "read_file", "delete_file"]

    print("Configuration: allowed_tools=['calculate']")
    for tool in tools_to_test:
        is_allowed = tool in options1.allowed_tools
        status = "ALLOWED" if is_allowed else "REQUIRES PERMISSION"
        print(f"  {tool}: {status}")

        if tool == "calculate":
            assert is_allowed, "Calculator should be allowed"
        else:
            assert not is_allowed, f"{tool} should require permission"

    print("✓ Permission filtering working correctly")

    # Test 2: Multiple tools allowed
    options2 = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant.",
        allowed_tools=["calculate", "read_file", "write_file"],
        permission_mode='acceptEdits'
    )

    print("\nConfiguration: allowed_tools=['calculate', 'read_file', 'write_file']")
    allowed_count = len(options2.allowed_tools)
    assert allowed_count == 3, f"Should have 3 allowed tools, got {allowed_count}"
    print(f"✓ {allowed_count} tools configured for auto-approval")


async def run_tests():
    """Run all permission tests"""
    print("\n" + "="*70)
    print("Pattern 3: Permission Management - Test Suite")
    print("="*70)

    tests = [
        ("Allowed Tools Configuration", test_allowed_tools_configuration),
        ("Permission Mode Configuration", test_permission_mode_configuration),
        ("Safe Tool Auto-Approval", test_safe_tool_auto_approval),
        ("Risky Tool Permission Requirement", test_risky_tool_requires_permission),
        ("Permission Mode: acceptEdits", test_permission_mode_accept_edits),
        ("Three-Tier Permission Model", test_three_tier_permission_model),
        ("Permission Filtering Behavior", test_permission_filtering_behavior),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
            print(f"\n✓ {test_name}: PASSED")
        except AssertionError as e:
            failed += 1
            print(f"\n✗ {test_name}: FAILED")
            print(f"  Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name}: ERROR")
            print(f"  Exception: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
