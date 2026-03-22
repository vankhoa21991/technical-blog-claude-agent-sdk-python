#!/usr/bin/env python3
"""
Pattern 5: Deep Research Agent with Sessions and Skills

This demo showcases advanced Claude Agent SDK Python features:
- ClaudeSDKClient for automatic session management
- Agent loop for multi-turn reasoning
- settingSources to load CLAUDE.md and skills
- Session operations: continue, resume, fork
- Web search integration for finding documentation

The agent performs a literature review comparing three AI agent frameworks:
- LangGraph (LangChain)
- AutoGen (Microsoft)
- Claude Agent SDK (Anthropic)

Usage:
    python patterns/05_deep_research.py

The demo runs in four phases:
1. Initial research - Agent searches web, analyzes frameworks
2. User feedback - Manual pause to get human direction
3. Refined analysis - Agent focuses on specific aspect
4. Fork session - Optional exploration of alternative direction

Expected output: 1-2 page summary report in Markdown format
"""
import asyncio
import sys
from pathlib import Path

# Add demo directory to path for imports
demo_dir = Path(__file__).parent.parent
sys.path.insert(0, str(demo_dir))

from claude_agent_sdk import ClaudeSDKClient, query, ClaudeAgentOptions


def print_separator(title: str = "") -> None:
    """Print a visual separator."""
    width = 60
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"{'=' * padding} {title} {'=' * padding}")
    else:
        print("=" * width)


def print_message(message) -> None:
    """Print a message from the agent."""
    if hasattr(message, 'content'):
        print(message.content, end='', flush=True)
    else:
        print(str(message), end='', flush=True)


async def phase_1_initial_research(client: ClaudeSDKClient) -> str:
    """
    Phase 1: Initial broad research on all three frameworks.

    Agent uses web search to find official documentation and comparison guides.
    Agent loop handles multi-turn reasoning automatically.

    Returns:
        Session ID for continuation
    """
    print_separator("PHASE 1: Initial Research")

    prompt = """
    Please conduct a literature review comparing these three AI agent frameworks:
    1. LangGraph (from LangChain)
    2. AutoGen (from Microsoft)
    3. Claude Agent SDK (from Anthropic)

    For each framework, identify:
    - Core architecture and design philosophy
    - Key features and capabilities
    - Primary use cases and target applications
    - Strengths and weaknesses

    Use web search to find official documentation and comparison guides.
    Provide a 1-2 page summary report in Markdown format with proper source citations.
    """

    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                setting_sources=["project"],  # Loads CLAUDE.md and skills
                allowed_tools=[
                    "Skill",      # Load research methodology
                    "Read",       # Read CLAUDE.md
                    "Bash",       # Run commands if needed
                    "web_search"  # Search for documentation
                ],
                effort="high"  # Deeper reasoning per turn
            )
        ):
            print_message(message)

        # Get session ID from client after query completes
        session_id = client.get_most_recent_session_id()

        print(f"\n\n✓ Phase 1 complete. Session ID: {session_id}")
        return session_id

    except Exception as e:
        print(f"\n\n✗ Phase 1 failed: {e}")
        raise


async def phase_2_user_feedback() -> str:
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
        session_id: Session ID from Phase 1
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
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                setting_sources=["project"],
                allowed_tools=["Skill", "Read", "Bash", "web_search"],
                session_id=session_id,  # Continue same session
                effort="high"
            )
        ):
            print_message(message)

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

    Forking creates a new session with copied history,
    allowing exploration without changing the original.

    Args:
        client: ClaudeSDKClient instance
        original_session_id: Session ID to fork from
    """
    print_separator("PHASE 4: Optional Fork")

    choice = input("\nWould you like to explore an alternative direction? (y/n): ").strip().lower()

    if choice not in ['y', 'yes']:
        print("Skipping fork phase.")
        return

    print("\n🔀 Creating forked session to explore alternative direction...")
    print("This creates a new session with copied history.")
    print("The original session remains unchanged.")

    prompt = """
    Now let's explore a different angle: compare the **community and ecosystem**
    around these three frameworks.

    Analyze:
    - GitHub activity (stars, contributors, commits)
    - Community support (Discord, Slack, forums)
    - Third-party integrations and extensions
    - Commercial support and backing

    This analysis starts fresh from the forked point.
    """

    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                setting_sources=["project"],
                allowed_tools=["Skill", "Read", "Bash", "web_search"],
                fork_from=original_session_id,  # Fork: new session with copied history
                effort="medium"
            )
        ):
            print_message(message)

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
    print("  • settingSources to load CLAUDE.md and skills")
    print("  • Session operations: continue, resume, fork")
    print("  • Web search for finding documentation")
    print()

    choice = input("Press Enter to continue or 'q' to quit: ").strip()
    if choice.lower() == 'q':
        print("Demo cancelled.")
        return

    # Initialize client (handles sessions automatically)
    client = ClaudeSDKClient()

    try:
        # Phase 1: Initial research
        session_id = await phase_1_initial_research(client)

        # Phase 2: User feedback
        direction = await phase_2_user_feedback()

        # Phase 3: Refined analysis (continues session)
        await phase_3_refined_analysis(client, session_id, direction)

        # Phase 4: Optional fork
        await phase_4_optional_fork(client, session_id)

        print_separator("Demo Complete")
        print("\n✓ All phases finished successfully!")
        print(f"\nSession ID: {session_id}")
        print("You can resume this session later using the session ID.")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
