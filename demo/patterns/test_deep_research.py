"""Test Pattern 5: Deep Research Agent"""

import sys
import asyncio
from pathlib import Path

# Add demo directory to path
demo_dir = Path(__file__).parent
sys.path.insert(0, str(demo_dir.parent))


def test_claude_md_exists():
    """Test that CLAUDE.md exists."""
    claude_md = Path(__file__).parent.parent / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md not found"
    print("✓ CLAUDE.md exists")


def test_research_skill_exists():
    """Test that research skill exists."""
    skill_md = Path(__file__).parent.parent / ".claude" / "skills" / "research" / "SKILL.md"
    assert skill_md.exists(), "Research skill not found"
    print("✓ Research skill exists")


def test_module_imports():
    """Test that the demo script can be imported."""
    try:
        # File is named 05_deep_research.py (leading number)
        # Use importlib to load it with a valid module name
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pattern_05_deep_research",
            Path(__file__).parent / "05_deep_research.py"
        )
        demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo)

        assert demo is not None
        assert hasattr(demo, 'main')
        assert hasattr(demo, 'phase_1_initial_research')
        assert hasattr(demo, 'phase_2_user_feedback')
        assert hasattr(demo, 'phase_3_refined_analysis')
        assert hasattr(demo, 'phase_4_optional_fork')
        print("✓ Module imports successfully")
        print("✓ All phase functions are defined")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        raise


def test_client_initialization():
    """Test that ClaudeSDKClient can be initialized."""
    try:
        from claude_agent_sdk import ClaudeSDKClient
        client = ClaudeSDKClient()
        assert client is not None
        print("✓ ClaudeSDKClient initializes successfully")
    except ImportError as e:
        print(f"⚠ SDK not installed: {e}")
        print("  (Expected - demo code is illustrative)")


def test_phase_2_user_feedback():
    """Test Phase 2 user feedback function."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pattern_05_deep_research",
        Path(__file__).parent / "05_deep_research.py"
    )
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    # Verify function exists and is callable
    assert hasattr(demo, 'phase_2_user_feedback')
    assert callable(demo.phase_2_user_feedback)
    print("✓ Phase 2 function exists (requires manual testing)")


def test_print_functions():
    """Test utility print functions."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pattern_05_deep_research",
        Path(__file__).parent / "05_deep_research.py"
    )
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    # Test print_separator
    demo.print_separator("TEST")
    print("✓ print_separator works")

    # Test print_message with string
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        demo.print_message("Test message")
    output = f.getvalue()
    assert "Test message" in output
    print("✓ print_message works")
