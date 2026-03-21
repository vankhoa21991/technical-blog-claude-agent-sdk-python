"""
Tests for Pattern 2: Hooks for Control

Tests follow TDD approach:
1. Command Blocker Hook (pre_tool_use_hook) - denies dangerous bash commands
2. Audit Logger Hook (pre_tool_use_hook) - logs tool invocations before execution
3. Audit Logger Hook (post_tool_use_hook) - logs tool results after execution
"""
import asyncio
import sys
import os
from pathlib import Path

# Add demo directory to path
sys.path.append(str(Path(__file__).parent.parent))

from hooks.command_blocker import pre_tool_use_hook as command_blocker_hook
from hooks.audit_logger import pre_tool_use_hook as audit_pre_hook
from hooks.audit_logger import post_tool_use_hook as audit_post_hook


async def test_command_blocker_denies_dangerous_commands():
    """Test that command blocker denies dangerous bash commands using regex"""
    print("\n--- Testing Command Blocker: Deny Dangerous Commands (Regex) ---")

    dangerous_commands = [
        {"tool_name": "bash", "tool_input": {"command": "rm -rf /"}},
        {"tool_name": "bash", "tool_input": {"command": "format c:"}},
        {"tool_name": "bash", "tool_input": {"command": "mkfs.ext4 /dev/sda1"}},
        {"tool_name": "bash", "tool_input": {"command": "dd if=/dev/zero of=/dev/sda"}},
        {"tool_name": "bash", "tool_input": {"command": "echo test > /dev/sda"}},
        {"tool_name": "bash", "tool_input": {"command": ":(){:|:&};:"}},  # Fork bomb
    ]

    for test_input in dangerous_commands:
        result = await command_blocker_hook(test_input, "test-id", {})

        # Verify hook returns deny decision
        assert "hookSpecificOutput" in result, f"Missing hookSpecificOutput for: {test_input['tool_input']['command']}"
        assert result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "permissionDecisionReason" in result["hookSpecificOutput"]
        print(f"✓ Blocked: {test_input['tool_input']['command']}")


async def test_command_blocker_allows_safe_commands():
    """Test that command blocker allows safe bash commands"""
    print("\n--- Testing Command Blocker: Allow Safe Commands ---")

    safe_commands = [
        {"tool_name": "bash", "tool_input": {"command": "ls -la"}},
        {"tool_name": "bash", "tool_input": {"command": "echo 'hello world'"}},
        {"tool_name": "bash", "tool_input": {"command": "cat README.md"}},
        {"tool_name": "bash", "tool_input": {"command": "rm -rf myfile.txt"}},  # Safe: not rm -rf /
        {"tool_name": "calculator", "tool_input": {"a": 5, "b": 3, "operation": "add"}},
    ]

    for test_input in safe_commands:
        result = await command_blocker_hook(test_input, "test-id", {})

        # Verify hook returns empty dict (no interception)
        assert result == {}, f"Safe command was blocked: {test_input.get('tool_input', test_input)}"
        print(f"✓ Allowed: {test_input.get('tool_name', test_input)}")


async def test_audit_logger_logs_tool_invocations():
    """Test that audit logger pre_tool_use_hook logs all tool invocations"""
    print("\n--- Testing Audit Logger: PreToolUse Hook ---")

    # Clean up any existing audit log
    audit_log_path = Path(__file__).parent.parent / "audit.log"
    if audit_log_path.exists():
        audit_log_path.unlink()

    test_cases = [
        {"tool_name": "bash", "tool_input": {"command": "ls -la"}},
        {"tool_name": "calculator", "tool_input": {"a": 5, "b": 3, "operation": "add"}},
    ]

    for test_input in test_cases:
        result = await audit_pre_hook(test_input, "test-tool-id", {})

        # Verify hook returns empty dict (no interception)
        assert result == {}, "Audit logger should not intercept"

    # Verify log file was created and contains entries
    assert audit_log_path.exists(), "Audit log file was not created"

    with open(audit_log_path, "r") as f:
        log_content = f.read()
        # Should have 2 log entries
        log_lines = [line for line in log_content.strip().split("\n") if line]
        assert len(log_lines) == 2, f"Expected 2 log entries, got {len(log_lines)}"

        # Verify log contains expected fields
        for line in log_lines:
            import json
            log_entry = json.loads(line)
            assert "timestamp" in log_entry
            assert "event" in log_entry
            assert log_entry["event"] == "PreToolUse"
            assert "tool" in log_entry
            assert "input" in log_entry
            assert "tool_use_id" in log_entry
            print(f"✓ Logged (PRE): {log_entry['tool']}")

    # Clean up
    if audit_log_path.exists():
        audit_log_path.unlink()


async def test_audit_logger_post_hook():
    """Test that audit logger post_tool_use_hook logs tool results"""
    print("\n--- Testing Audit Logger: PostToolUse Hook ---")

    # Clean up any existing audit log
    audit_log_path = Path(__file__).parent.parent / "audit.log"
    if audit_log_path.exists():
        audit_log_path.unlink()

    # Simulate tool outputs
    test_cases = [
        ("tool-use-1", {"content": [{"type": "text", "text": "42"}]}),
        ("tool-use-2", {"content": [{"type": "text", "text": "Hello, World!"}]}),
    ]

    for tool_use_id, tool_output in test_cases:
        result = await audit_post_hook(tool_use_id, tool_output, {})

        # Verify hook returns empty dict (no interception)
        assert result == {}, "Audit logger should not modify output"

    # Verify log file was created and contains entries
    assert audit_log_path.exists(), "Audit log file was not created"

    with open(audit_log_path, "r") as f:
        log_content = f.read()
        # Should have 2 log entries
        log_lines = [line for line in log_content.strip().split("\n") if line]
        assert len(log_lines) == 2, f"Expected 2 log entries, got {len(log_lines)}"

        # Verify log contains expected fields
        for line in log_lines:
            import json
            log_entry = json.loads(line)
            assert "timestamp" in log_entry
            assert "event" in log_entry
            assert log_entry["event"] == "PostToolUse"
            assert "tool_use_id" in log_entry
            assert "output" in log_entry
            print(f"✓ Logged (POST): {log_entry['tool_use_id']}")

    # Clean up
    if audit_log_path.exists():
        audit_log_path.unlink()


async def test_hook_return_format():
    """Test that hooks return correct format"""
    print("\n--- Testing Hook Return Format ---")

    # Test deny format (command blocker)
    deny_result = await command_blocker_hook(
        {"tool_name": "bash", "tool_input": {"command": "rm -rf /"}},
        "test-id",
        {}
    )

    assert isinstance(deny_result, dict)
    assert "hookSpecificOutput" in deny_result
    assert isinstance(deny_result["hookSpecificOutput"], dict)
    assert "hookEventName" in deny_result["hookSpecificOutput"]
    assert "permissionDecision" in deny_result["hookSpecificOutput"]
    assert "permissionDecisionReason" in deny_result["hookSpecificOutput"]
    print("✓ Deny format correct")

    # Test no-op format (command blocker)
    no_op_result = await command_blocker_hook(
        {"tool_name": "calculator", "tool_input": {"a": 1, "b": 2, "operation": "add"}},
        "test-id",
        {}
    )

    assert isinstance(no_op_result, dict)
    assert no_op_result == {}, "No-op hook should return empty dict"
    print("✓ No-op format correct")

    # Test pre_tool_use_hook format (audit logger)
    pre_result = await audit_pre_hook(
        {"tool_name": "calculator", "tool_input": {"a": 1, "b": 2, "operation": "add"}},
        "test-id",
        {}
    )

    assert isinstance(pre_result, dict)
    assert pre_result == {}, "Audit logger pre-hook should return empty dict"
    print("✓ PreToolUse format correct")

    # Test post_tool_use_hook format (audit logger)
    post_result = await audit_post_hook(
        "test-id",
        {"content": [{"type": "text", "text": "3"}]},
        {}
    )

    assert isinstance(post_result, dict)
    assert post_result == {}, "Audit logger post-hook should return empty dict"
    print("✓ PostToolUse format correct")


async def run_tests():
    """Run all hook tests"""
    print("\n" + "="*60)
    print("Pattern 2: Hooks for Control - Test Suite")
    print("="*60)

    tests = [
        ("Command Blocker - Deny Dangerous (Regex)", test_command_blocker_denies_dangerous_commands),
        ("Command Blocker - Allow Safe", test_command_blocker_allows_safe_commands),
        ("Audit Logger - PreToolUse", test_audit_logger_logs_tool_invocations),
        ("Audit Logger - PostToolUse", test_audit_logger_post_hook),
        ("Hook Return Format", test_hook_return_format),
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

    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
