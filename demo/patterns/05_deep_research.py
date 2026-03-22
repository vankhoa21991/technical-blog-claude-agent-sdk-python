#!/usr/bin/env python3
"""
Pattern 5: Deep Research Agent with Sessions

This demo showcases advanced Claude Agent SDK Python features:
- ClaudeSDKClient for session management
- Session persistence across multiple conversation turns
- Continuing conversations with session_id
- Forking sessions to explore alternatives

The agent compares three AI agent frameworks:
- LangGraph (from LangChain)
- AutoGen (from Microsoft)
- Claude Agent SDK (from Anthropic)

Usage:
    python patterns/05_deep_research.py

The demo runs in four phases:
1. Initial research - Agent does quick web search for basic info
2. User feedback - Manual pause to get human direction
3. Refined analysis - Agent focuses on specific aspect
4. Fork session - Optional exploration of alternative direction

Expected output: Concise summaries of each framework
"""
import asyncio
import sys
from pathlib import Path
import uuid

# Add demo directory to path for imports
demo_dir = Path(__file__).parent.parent
sys.path.insert(0, str(demo_dir))

from claude_agent_sdk import ClaudeSDKClient


def print_separator(title: str = "") -> None:
    """Print a visual separator."""
    width = 60
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"{'=' * padding} {title} {'=' * padding}")
    else:
        print("=" * width)


async def phase_1_initial_research(client: ClaudeSDKClient, session_id: str) -> None:
    """
    Phase 1: Initial quick research on all three frameworks.

    Agent uses web search to find basic information about each framework.
    Keeps it simple - what it is, use cases, and key features.

    Args:
        client: ClaudeSDKClient instance
        session_id: Session ID to use for this phase
    """
    print_separator("PHASE 1: Initial Research")

    prompt = """
    Search the web for information about these three AI agent frameworks:
    1. LangGraph (from LangChain)
    2. AutoGen (from Microsoft)
    3. Claude Agent SDK (from Anthropic)

    For each framework, provide a brief summary covering:
    - What it is
    - Main use cases
    - Key features

    Keep it concise - just the essentials.
    """

    try:
        # Send the prompt
        await client.query(
            prompt=prompt,
            session_id=session_id
        )

        # Receive and print messages
        message_count = 0
        max_messages = 100  # Safety limit to prevent infinite loops

        async for message in client.receive_messages():
            message_count += 1
            if message_count > max_messages:
                print("\n\n[Message limit reached, stopping...]")
                break

            # Only print text content, skip internal system messages
            if hasattr(message, 'content'):
                print(message.content, end='', flush=True)
            elif hasattr(message, 'text'):
                print(message.text, end='', flush=True)
            # Check if this is a result message (end of response)
            elif hasattr(message, 'stop_reason'):
                # End of turn reached
                break
            # Skip SystemMessage, ThinkingBlock, ToolUseBlock, ToolResultBlock, etc.
            # These are internal debug messages, not user-facing content

        print(f"\n\n✓ Phase 1 complete. Session ID: {session_id}")

    except Exception as e:
        print(f"\n\n✗ Phase 1 failed: {e}")
        raise


def phase_2_user_feedback() -> str:
    """
    Phase 2: Manual pause for human direction.

    This is a manual CLI pause - the SDK doesn't provide an "ask user" API.
    In production, you might implement a webhook or UI for this.

    Returns:
        User's direction for refinement
    """
    print_separator("PHASE 2: User Feedback")

    print("\n🔍 Initial research complete!")
    print("\nWhat would you like to focus on for deeper analysis?")
    print("  1. Architecture patterns")
    print("  2. Use cases and applications")
    print("  3. Learning curve and adoption")
    print("  4. Performance benchmarks")
    print("  5. Custom topic")

    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == "1":
            return "architecture patterns and design philosophy"
        elif choice == "2":
            return "real-world use cases and applications"
        elif choice == "3":
            return "learning curve, documentation quality, and adoption"
        elif choice == "4":
            return "performance benchmarks and efficiency"
        elif choice == "5":
            custom = input("Enter your topic: ").strip()
            if custom:
                return custom
        else:
            print("Invalid choice. Please enter 1-5.")


async def phase_3_refined_analysis(
    client: ClaudeSDKClient,
    session_id: str,
    direction: str
) -> None:
    """
    Phase 3: Refined analysis based on user feedback.

    Continues the same session with accumulated context.

    Args:
        client: ClaudeSDKClient instance
        session_id: Session ID to use for this phase
        direction: User's chosen focus area
    """
    print_separator("PHASE 3: Refined Analysis")

    prompt = f"""
    Excellent! Now please provide a deeper analysis focusing specifically on:
    {direction}

    Build upon your previous research and provide detailed insights
    specifically for this aspect. Include specific examples and
    concrete comparisons between the three frameworks.
    """

    try:
        # Send the prompt
        await client.query(
            prompt=prompt,
            session_id=session_id
        )

        # Receive and print messages
        message_count = 0
        max_messages = 100  # Safety limit to prevent infinite loops

        async for message in client.receive_messages():
            message_count += 1
            if message_count > max_messages:
                print("\n\n[Message limit reached, stopping...]")
                break

            # Only print text content, skip internal system messages
            if hasattr(message, 'content'):
                print(message.content, end='', flush=True)
            elif hasattr(message, 'text'):
                print(message.text, end='', flush=True)
            # Check if this is a result message (end of response)
            elif hasattr(message, 'stop_reason'):
                # End of turn reached
                break
            # Skip SystemMessage, ThinkingBlock, ToolUseBlock, ToolResultBlock, etc.
            # These are internal debug messages, not user-facing content

        print("\n\n✓ Phase 3 complete. Session updated with refined analysis.")

    except Exception as e:
        print(f"\n\n✗ Phase 3 failed: {e}")
        raise


async def phase_4_optional_fork(
    client: ClaudeSDKClient,
    original_session_id: str
) -> None:
    """
    Phase 4: Optional fork to explore alternative direction.

    Creates a new session with a different ID to explore alternatives
    without changing the original session.

    Args:
        client: ClaudeSDKClient instance
        original_session_id: Original session ID (not modified)
    """
    print_separator("PHASE 4: Optional Fork")

    choice = input("\nWould you like to explore an alternative direction? (y/n): ").strip().lower()

    if choice not in ['y', 'yes']:
        print("Skipping fork phase.")
        return

    # Create a new session ID for the fork
    fork_session_id = f"{original_session_id}-fork"

    print("\n🔀 Creating forked session to explore alternative direction...")
    print(f"Original session: {original_session_id}")
    print(f"Fork session: {fork_session_id}")
    print("The original session remains unchanged.")

    prompt = """
    Now let's explore a different angle: compare the **community and ecosystem**
    around these three frameworks.

    Analyze:
    - GitHub activity (stars, contributors, commits)
    - Community support (Discord, Slack, forums)
    - Third-party integrations and extensions
    - Commercial support and backing

    This analysis starts fresh in the forked session.
    """

    try:
        # Send the prompt
        await client.query(
            prompt=prompt,
            session_id=fork_session_id
        )

        # Receive and print messages
        message_count = 0
        max_messages = 100  # Safety limit to prevent infinite loops

        async for message in client.receive_messages():
            message_count += 1
            if message_count > max_messages:
                print("\n\n[Message limit reached, stopping...]")
                break

            # Only print text content, skip internal system messages
            if hasattr(message, 'content'):
                print(message.content, end='', flush=True)
            elif hasattr(message, 'text'):
                print(message.text, end='', flush=True)
            # Check if this is a result message (end of response)
            elif hasattr(message, 'stop_reason'):
                # End of turn reached
                break
            # Skip SystemMessage, ThinkingBlock, ToolUseBlock, ToolResultBlock, etc.
            # These are internal debug messages, not user-facing content

        print("\n\n✓ Phase 4 complete. Forked session created.")

    except Exception as e:
        print(f"\n\n✗ Phase 4 failed: {e}")
        raise


async def main() -> None:
    """Run the deep research agent demo."""
    print_separator("Deep Research Agent Demo")
    print("\nThis demo showcases:")
    print("  • ClaudeSDKClient for session management")
    print("  • Agent loop for multi-turn reasoning")
    print("  • Session persistence across multiple turns")
    print("  • Web search for finding documentation")
    print()

    choice = input("Press Enter to continue or 'q' to quit: ").strip()
    if choice.lower() == 'q':
        print("Demo cancelled.")
        return

    # Initialize client
    client = ClaudeSDKClient()

    # Connect to Claude Code
    print("Connecting to Claude Code...")
    await client.connect()
    print("✓ Connected\n")

    # Generate a unique session ID for this demo run
    session_id = f"research-{uuid.uuid4().hex[:8]}"

    print(f"📝 Session ID: {session_id}")
    print("This session will persist across all phases.\n")

    try:
        # Phase 1: Initial research
        await phase_1_initial_research(client, session_id)

        # Phase 2: User feedback
        direction = phase_2_user_feedback()

        # Phase 3: Refined analysis (continues session)
        await phase_3_refined_analysis(client, session_id, direction)

        # Phase 4: Optional fork
        await phase_4_optional_fork(client, session_id)

        print_separator("Demo Complete")
        print("\n✓ All phases finished successfully!")
        print(f"\nMain Session ID: {session_id}")
        print("You can use this session ID to resume the conversation later.")

        # Disconnect
        await client.disconnect()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        await client.disconnect()
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
