# Building Persistent AI Agents: A Complete Guide to Claude Agent SDK Sessions & Skills

Most AI agents today are forgetful. They answer your question, then immediately forget everything about the conversation. No context, no memory, no continuity. But what if your AI could remember? What if it could reference previous interactions, build on past context, and maintain a coherent conversation over multiple sessions? Enter Claude Agent SDK's Sessions & Skills pattern — the secret to building AI agents that don't just respond, but remember. In this guide, you'll learn how to transform stateless API calls into persistent, intelligent agents that maintain context, leverage specialized skills, and deliver increasingly personalized experiences.

---

## The Problem: Why Sessions Matter

Ever tried building a research agent that needs to remember previous turns? It's harder than it sounds.

**Without sessions:**
- ❌ Each prompt starts from scratch
- ❌ No context preservation across turns
- ❌ Manual state management required
- ❌ Can't explore alternative analysis paths

**With sessions:**
- ✅ Automatic context preservation
- ✅ Built-in continue/resume/fork operations
- ✅ Project context loaded automatically
- ✅ Multi-turn reasoning without custom code

Let's build a literature review agent that compares three AI frameworks:
- **LangGraph** (from LangChain)
- **AutoGen** (from Microsoft)
- **Claude Agent SDK** (from Anthropic)

---

## The Solution: Complete Working Example

Here's the complete research agent in a single file. Don't worry about understanding every line yet — we'll break it down in the next section.

```python
from claude_agent_sdk import ClaudeSDKClient, query, ClaudeAgentOptions

async def research_agent():
    """Multi-turn literature review agent with sessions and skills."""

    client = ClaudeSDKClient()

    # Phase 1: Initial Research
    print("🔍 Phase 1: Conducting initial research...\n")

    async for message in query(
        prompt="Conduct a literature review comparing LangGraph, AutoGen, and Claude Agent SDK. "
              "Compare their architectures, key features, and ideal use cases. "
              "Provide a structured report with strengths and weaknesses of each.",
        options=ClaudeAgentOptions(
            setting_sources=["project"],  # Load CLAUDE.md and skills
            allowed_tools=["Skill", "Read", "Bash", "web_search"],
            effort="high"  # Deeper reasoning per turn
        )
    ):
        print(message.content)

    # Get session ID for continuation
    session_id = client.get_most_recent_session_id()
    print(f"\n💾 Session ID: {session_id}")

    # Phase 2: User Feedback (Interactive)
    print("\n" + "="*70)
    direction = input("Focus deeper on [architecture/use cases/learning curve/performance]? ")
    print("="*70 + "\n")

    # Phase 3: Refined Analysis (Continue same session)
    print(f"🎯 Phase 3: Deepening analysis on {direction}...\n")

    async for message in query(
        prompt=f"Great, focusing on {direction}. Provide a detailed comparison "
              f"specifically about {direction}. Include code examples if relevant.",
        options=ClaudeAgentOptions(
            setting_sources=["project"],
            session_id=session_id  # Continue same session (context preserved)
        )
    ):
        print(message.content)

    # Phase 4: Optional Fork (Explore alternative)
    print("\n" + "="*70)
    explore_alt = input("Explore alternative direction? [y/N]: ")
    print("="*70 + "\n")

    if explore_alt.lower() == 'y':
        print("🔄 Phase 4: Exploring alternative direction...\n")

        async for message in query(
            prompt="Now compare the learning curves and documentation quality "
                  "of these three frameworks. Which is most beginner-friendly?",
            options=ClaudeAgentOptions(
                setting_sources=["project"],
                fork_from=session_id  # Fork: new session with copied history
            )
        ):
            print(message.content)

        new_session_id = client.get_most_recent_session_id()
        print(f"\n💾 New Session ID (fork): {new_session_id}")

    print("\n✅ Research complete!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(research_agent())
```

**That's it.** No manual session handling, no state management, no custom conversation loops. The SDK handles everything.

---

## How It Works: 3 Key Concepts

### 1. ClaudeSDKClient - Automatic Session Management

Think of `ClaudeSDKClient` like a conversation manager — it automatically creates sessions, tracks context, and handles history.

```python
client = ClaudeSDKClient()

# First query() creates session automatically
async for message in query(prompt="...", options=...):
    print(message.content)

# Get session ID for later use
session_id = client.get_most_recent_session_id()
```

**What happens:**
- SDK creates session on first `query()`
- Tracks all conversation history
- Returns session ID for continuation

**No manual state management required.**

### 2. Agent Loop - Multi-Turn Reasoning Without Custom Code

The Agent Loop is the engine that powers multi-turn reasoning.

```python
async for message in query(
    prompt="Conduct literature review...",  # Complex task
    options=ClaudeAgentOptions(
        effort="high"  # Control reasoning depth
    )
):
    print(message.content)
```

**What happens:**
- Agent automatically does multi-step analysis
- Each turn can use tools, search web, read files
- No custom "thinking" loops required
- `effort` parameter controls depth (low/medium/high/max)

**You don't write the reasoning loop — the SDK does.**

### 3. settingSources - Load CLAUDE.md and Skills

This is the magic that gives your agent project context and domain expertise.

```python
options=ClaudeAgentOptions(
    setting_sources=["project"]  # Load CLAUDE.md and skills
)
```

**What loads:**
- `CLAUDE.md` - Project instructions and context
- `.claude/skills/*/SKILL.md` - Domain expertise (loaded on-demand via `Skill` tool)

**Example skill** (`demo/.claude/skills/research/SKILL.md`):
```markdown
---
name: research
description: Research methodology for deep analysis
---

# Research Methodology

## Phase 1: Information Gathering
- Search official documentation first
- Find comparison guides and benchmarks
- Identify key differentiators

## Phase 2: Analysis
- Compare architecture patterns
- Evaluate use cases and trade-offs
- Assess strengths and weaknesses

## Phase 3: Synthesis
- Identify patterns and trends
- Highlight key differences
- Provide concrete recommendations
```

**Agent loads this skill automatically** when it needs research expertise.

---

## Live Demo: What You'll Experience

When you run the code above, here's what happens:

### Phase 1: Initial Research
```
🔍 Phase 1: Conducting initial research...

# Literature Review: LangGraph vs AutoGen vs Claude Agent SDK

## Overview
This report compares three leading frameworks for building AI agents...

## LangGraph
**Architecture:** Graph-based agent orchestration...
**Strengths:** Visual debugging, complex multi-agent workflows...
**Weaknesses:** Steep learning curve, heavy abstraction...

## AutoGen
**Architecture:** Multi-agent conversation framework...
**Strengths:** Natural multi-agent patterns, Microsoft backing...
**Weaknesses:** Less mature ecosystem, Python-only...

## Claude Agent SDK
**Architecture:** Tool-calling with agent loop...
**Strengths:** Simple API, built-in session management...
**Weaknesses:** Newer framework, fewer examples...

💾 Session ID: sess_abc123...
```

### Phase 2: Your Turn
```
======================================================================
Focus deeper on [architecture/use cases/learning curve/performance]? architecture
======================================================================
```

### Phase 3: Refined Analysis
```
🎯 Phase 3: Deepening analysis on architecture...

# Deep Dive: Architectural Comparison

## LangGraph Architecture
LangGraph uses a graph-based approach where agents are nodes...
[Detailed architectural analysis with code examples]

## AutoGen Architecture
AutoGen focuses on multi-agent conversations...
[More detailed analysis]

## Claude Agent SDK Architecture
The SDK uses a tool-calling approach with the Agent Loop...
[Complete architectural deep dive]
```

### Phase 4: Optional Fork
```
======================================================================
Explore alternative direction? [y/N]: y
======================================================================

🔄 Phase 4: Exploring alternative direction...

# Learning Curve Comparison

## Beginner-Friendliness Rankings...
💾 New Session ID (fork): sess_xyz789...
```

**Key insight:** Each phase builds on the previous one. The agent remembers context, uses skills, and refines analysis based on your feedback.

---

## Advanced Features

### Fork Sessions - Explore Alternatives

Forking creates a new session with copied history — perfect for exploring alternative directions.

```python
async for message in query(
    prompt="Now compare learning curves instead",  # New direction
    options=ClaudeAgentOptions(
        setting_sources=["project"],
        fork_from=session_id  # Fork: new session + copied history
    )
):
    print(message.content)
```

**Use cases:**
- Explore alternative analysis paths
- Compare different approaches
- A/B test research directions
- Keep original session intact

### Resume Sessions - Long-Running Tasks

Resume a session by ID for long-running research tasks.

```python
# Day 1: Start research
async for message in query(prompt="Compare X and Y..."):
    print(message.content)
session_id = client.get_most_recent_session_id()

# Save session_id to database...

# Day 2: Resume research
async for message in query(
    prompt="Continue the analysis, focusing on performance...",
    options=ClaudeAgentOptions(
        session_id=session_id  # Resume from Day 1
    )
):
    print(message.content)
```

**Use cases:**
- Long-term research projects
- Batch processing with breaks
- Multi-day analysis tasks
- Pause and resume workflows

### Effort Levels - Control Reasoning Depth

The `effort` parameter controls how deep the agent reasons per turn.

```python
options=ClaudeAgentOptions(
    effort="low"    # Quick, shallow reasoning
    # effort="medium"  # Balanced (default)
    # effort="high"    # Deep, thorough reasoning
    # effort="max"     # Maximum depth (slowest)
)
```

**When to use each:**
- `low`: Quick summaries, simple queries
- `medium`: Standard analysis (default)
- `high`: Deep research, complex comparisons
- `max`: Exhaustive analysis (slowest, most thorough)

---

## Common Pitfalls

### ⚠️ Pitfall 1: Forgetting web_search in allowed_tools

```python
# ❌ Bad - Agent can't search web
options=ClaudeAgentOptions(
    allowed_tools=["Skill", "Read", "Bash"]  # No web_search!
)

# ✅ Good - Includes web_search for research
options=ClaudeAgentOptions(
    allowed_tools=["Skill", "Read", "Bash", "web_search"]
)
```

**Why it matters:** Research agents need web search to find documentation and comparisons.

### ⚠️ Pitfall 2: Using Wrong session_id

```python
# ❌ Bad - Typo in session_id creates new session
session_id="sess_abc123"  # Missing last digit!

async for message in query(
    prompt="Continue analysis...",
    options=ClaudeAgentOptions(session_id=session_id)
):
    print(message.content)
# Result: New session (context lost!)

# ✅ Good - Use SDK method to get session ID
session_id = client.get_most_recent_session_id()  # Exact match
```

**Why it matters:** Wrong session_id = new session = lost context.

### ⚠️ Pitfall 3: Not Setting Effort Level

```python
# ❌ Bad - Default effort may be too shallow
options=ClaudeAgentOptions(
    setting_sources=["project"]
)
# Result: Surface-level analysis

# ✅ Good - Explicit effort for deep research
options=ClaudeAgentOptions(
    setting_sources=["project"],
    effort="high"  # Deeper reasoning per turn
)
```

**Why it matters:** Research tasks need deeper reasoning (`effort="high"` or `"max"`).

### ⚠️ Pitfall 4: Missing settingSources

```python
# ❌ Bad - No project context or skills
options=ClaudeAgentOptions(
    allowed_tools=["Skill", "web_search"]
)
# Result: Agent can't load skills or CLAUDE.md

# ✅ Good - Loads project context automatically
options=ClaudeAgentOptions(
    setting_sources=["project"],  # Load CLAUDE.md and skills
    allowed_tools=["Skill", "web_search"]
)
```

**Why it matters:** `setting_sources=["project"]` enables automatic skill loading and project context.

---

## Production Example: Error Handling & Monitoring

Here's a production-ready version with error handling and monitoring:

```python
import logging
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient, query, ClaudeAgentOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('research_agent')

async def production_research_agent():
    """Production research agent with error handling and monitoring."""

    client = ClaudeSDKClient()
    session_id = None

    try:
        # Phase 1: Initial Research
        logger.info("Starting Phase 1: Initial research")
        start_time = datetime.now()

        async for message in query(
            prompt="Conduct literature review comparing LangGraph, AutoGen, and Claude Agent SDK...",
            options=ClaudeAgentOptions(
                setting_sources=["project"],
                allowed_tools=["Skill", "Read", "Bash", "web_search"],
                effort="high"
            )
        ):
            print(message.content)

        session_id = client.get_most_recent_session_id()
        phase1_duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Phase 1 complete in {phase1_duration:.2f}s. Session: {session_id}")

        # Phase 2: User Feedback
        direction = input("\nFocus deeper on [architecture/use cases/learning curve]? ")
        logger.info(f"User requested focus on: {direction}")

        # Phase 3: Refined Analysis
        logger.info("Starting Phase 3: Refined analysis")
        start_time = datetime.now()

        async for message in query(
            prompt=f"Deepen analysis on {direction}...",
            options=ClaudeAgentOptions(
                setting_sources=["project"],
                session_id=session_id
            )
        ):
            print(message.content)

        phase3_duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Phase 3 complete in {phase3_duration:.2f}s")

    except Exception as e:
        logger.error(f"Research agent failed: {str(e)}")
        if session_id:
            logger.info(f"Session {session_id} preserved for resuming")
        raise

    finally:
        logger.info("Research agent execution complete")

if __name__ == "__main__":
    import asyncio
    asyncio.run(production_research_agent())
```

**Production features:**
- ✅ Comprehensive error handling
- ✅ Structured logging
- ✅ Performance monitoring (phase durations)
- ✅ Session preservation on error
- ✅ Audit trail

---

## When to Use Pattern 5

### ✅ Use Sessions & Skills when:

- **Building research or analysis agents** - Multi-turn reasoning with context
- **Need user feedback loops** - Accept input, refine analysis
- **Long-running tasks** - Resume sessions across hours/days
- **Domain expertise required** - Skills provide methodology
- **Exploring alternatives** - Fork sessions to compare directions

### ❌ Consider alternatives when:

- **Simple single-turn tasks** - Use Pattern 1 (custom tools only)
- **No user feedback needed** - Use Pattern 4 (complete agent)
- **Custom session handling** - Build your own session management
- **No skills or CLAUDE.md** - `setting_sources` requires filesystem structure

---

## Key Takeaways

**Sessions vs. Single Prompts:**
- ✅ Automatic context preservation across turns
- ✅ Built-in continue/resume/fork operations
- ✅ No manual state management required
- ❌ Less control over session lifecycle (trade-off)

**Agent Loop vs. Custom Thinking:**
- ✅ Multi-turn reasoning automatic
- ✅ No custom "thinking" prompts needed
- ✅ Handles tool use naturally
- ❌ Less transparent reasoning process (trade-off)

**settingSources vs. Manual Context:**
- ✅ Automatic CLAUDE.md loading
- ✅ On-demand skill loading via `Skill` tool
- ✅ Project context always available
- ❌ Requires specific filesystem structure (trade-off)

---

## Try It Yourself

### 1. Run the Demo

```bash
cd demo
python patterns/05_deep_research.py
```

**What to try:**
- Focus on "architecture" (see technical deep dive)
- Focus on "use cases" (see practical examples)
- Explore alternative direction (fork session)

### 2. Experiment with Effort Levels

```python
# Try different effort levels
options=ClaudeAgentOptions(
    setting_sources=["project"],
    effort="low"    # Fast, shallow
    # effort="high"  # Slower, deeper
    # effort="max"   # Slowest, most thorough
)
```

**Notice:** How analysis depth changes with effort level.

### 3. Create Your Own Skill

```bash
mkdir -p demo/.claude/skills/my-domain
```

**File:** `demo/.claude/skills/my-domain/SKILL.md`
```markdown
---
name: my-domain
description: My domain expertise
---

# My Domain Methodology

## Step 1: Analysis
- Analyze X
- Compare Y

## Step 2: Synthesis
- Identify patterns
- Provide recommendations
```

**Use it:**
```python
options=ClaudeAgentOptions(
    setting_sources=["project"],  # Loads your skill automatically
    allowed_tools=["Skill", "web_search"]
)
```

---

## What's Next?

You've now mastered all five patterns:

| Pattern | Capability | Use Case |
|---------|-----------|----------|
| 1. Custom Tools | Extend Claude with Python functions | Calculators, APIs, utilities |
| 2. Hooks | Intercept agent behavior | Security, validation, audit |
| 3. Permissions | Control tool access | Tiered access, safety |
| 4. Complete Agent | All patterns combined | Production agents |
| **5. Sessions & Skills** | **Multi-turn reasoning with context** | **Research, analysis, feedback** |

**Pattern 5 is the most powerful** — it enables agents that:
- Maintain state across interactions
- Learn from project context (CLAUDE.md)
- Use domain expertise (skills)
- Iterate with human feedback
- Explore alternatives (fork)

This is how you build production AI agents that tackle complex, multi-step research tasks while maintaining context and adapting to user feedback.

**Ready to build your own research agent?** Start with the demo code and extend it for your use case.

---

## Next Steps

1. **Run the demo:** `cd demo && python patterns/05_deep_research.py`
2. **Experiment with feedback:** Try different focus areas
3. **Create custom skills:** Add your domain expertise
4. **Deploy to production:** Add error handling and monitoring

## Resources

- [Sessions Documentation](https://platform.claude.com/docs/en/agent-sdk/sessions)
- [Agent Loop Documentation](https://platform.claude.com/docs/en/agent-sdk/agent-loop)
- [Claude Code Features](https://platform.claude.com/docs/en/agent-sdk/claude-code-features)

---

Happy building! 🚀
