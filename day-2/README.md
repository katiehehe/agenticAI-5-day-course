# 🧠 Day 2: Memory + MCP Tools

**Goal:** Enhance your agent with memory capabilities and MCP (Model Context Protocol) tools

## 📚 What You'll Learn

- How to add short-term and long-term memory to agents
- Understanding the Model Context Protocol (MCP)
- Integrating external tools (Spotify, Weather, Web Search, etc.)
- Tool selection strategies
- Memory management patterns

## 🎯 Today's Objectives

- [ ] Add memory to your agent (short-term and long-term)
- [ ] Install and configure an MCP server
- [ ] Integrate 1-2 tools into your agent
- [ ] Test memory persistence across conversations
- [ ] Add your agent to NANDA index
- [ ] Document your tool choices

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies for Day 2:
- `crewai[tools]` - Tool support
- Memory backends (built into CrewAI)

### 2. Set Up MCP Tools

We'll use the Model Context Protocol to integrate external services. Popular options:

**Option A: Spotify MCP**
```bash
# Get Spotify API credentials at: https://developer.spotify.com
# Add to .env:
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Option B: Weather/Web Search**
```bash
# Many MCP servers available at:
# https://github.com/modelcontextprotocol/servers
```

### 3. Run Your Memory-Enhanced Agent!

```bash
python main_with_memory.py
```

## 📖 Understanding Memory

### Short-Term Memory
- Remembers the current conversation
- Cleared when the session ends
- Perfect for context within a single task

### Long-Term Memory
- Persists across sessions
- Stores important facts and learnings
- Helps agent improve over time

### Example: Memory in Action

```python
from crewai import Agent, Task, Crew, LLM

# Enable memory for the crew
crew = Crew(
    agents=[my_agent],
    tasks=[my_task],
    memory=True,  # Enable memory!
    verbose=True
)
```

## 🛠️ Understanding MCP Tools

### What is MCP?

The Model Context Protocol is a standardized way for AI agents to interact with external services. Think of it as "USB for AI" - one standard interface for many tools.

### Available MCP Servers

Popular options from [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers):

1. **Spotify** - Music search, playlists, recommendations
2. **Weather** - Current weather, forecasts
3. **Web Search** - Brave/Google search
4. **GitHub** - Repository access, code search
5. **Google Maps** - Location data, directions
6. **Memory** - Enhanced memory capabilities

### Tool Integration Example

```python
from crewai_tools import SpotifyTool

# Initialize tool
spotify_tool = SpotifyTool(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)

# Add to agent
music_agent = Agent(
    role="Music Expert",
    goal="Help users discover music",
    backstory="You are a music expert who can search and recommend songs",
    tools=[spotify_tool],  # Add the tool here!
    llm=llm
)
```

## ✏️ Your Mission: Enhance Your Agent

### Step 1: Add Memory

Modify your crew to include memory:

```python
my_crew = Crew(
    agents=[my_agent_twin],
    tasks=[answer_question_task],
    memory=True,  # This enables memory!
    verbose=True
)
```

Now your agent will remember previous conversations!

### Step 2: Choose and Integrate a Tool

Pick a tool that matches your agent's personality:
- Music lover? → Spotify
- Travel enthusiast? → Weather/Maps
- Researcher? → Web Search
- Developer? → GitHub

### Step 3: Update Your Agent's Backstory

Tell your agent about its new capabilities:

```python
backstory="""
You are the digital twin of [YOUR NAME].

[Previous backstory...]

NEW CAPABILITIES:
- You can remember our past conversations
- You have access to [TOOL NAME] to [WHAT IT DOES]
- You use these tools to provide better, more personalized responses
"""
```

## 🧪 Experiments to Try

### Memory Tests

1. **Session memory**: Ask a question, then reference it later:
   ```
   You: "My favorite color is blue"
   Agent: "Got it!"
   You: "What's my favorite color?"
   Agent: "Your favorite color is blue!"
   ```

2. **Long-term memory**: Stop and restart the program. Does it remember?

### Tool Tests

1. **Direct tool use**: Ask your agent to use its tool explicitly
2. **Implicit tool use**: See if the agent knows when to use tools automatically
3. **Multi-step reasoning**: "Find me a song by X, then tell me about the artist"

## 📁 Project Structure

```
day-2/
├── main_with_memory.py      # Agent with memory enabled
├── main_with_tools.py        # Agent with MCP tools
├── main_complete.py          # Memory + Tools combined
├── requirements.txt          # Updated dependencies
├── env_example.txt           # New environment variables
└── README.md                 # This file!
```

## 🔧 Configuration Tips

### Memory Configuration

```python
# Fine-tune memory settings
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,
    memory_config={
        "provider": "local",  # or "redis" for production
        "storage_path": "./memory_storage"
    }
)
```

### Tool Configuration

```python
# Most tools need API keys
tool = SomeTool(
    api_key=os.getenv("TOOL_API_KEY"),
    # Optional parameters
    timeout=30,
    max_results=5
)
```

## 🐛 Troubleshooting

**Memory not persisting:**
- Check if memory is enabled: `memory=True`
- Verify storage path exists and is writable
- Check file permissions

**Tool not working:**
- Verify API credentials in `.env`
- Check API rate limits
- Read tool documentation for specific requirements

**Agent not using tools:**
- Make tools relevant to the task
- Be explicit in task description
- Check tool permissions and configuration

## 📚 Resources

- [CrewAI Memory Documentation](https://docs.crewai.com/concepts/memory)
- [CrewAI Tools](https://docs.crewai.com/concepts/tools)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Building Custom Tools](https://docs.crewai.com/concepts/tools#custom-tools)

## ✅ Day 2 Checklist

Before moving to Day 3, make sure you:
- [ ] Successfully enabled memory in your agent
- [ ] Integrated at least 1 MCP tool
- [ ] Tested memory persistence
- [ ] Agent can use tools when appropriate
- [ ] Updated .env with new API keys
- [ ] Documented your tool choices
- [ ] Added agent to NANDA index

## 🎯 Next Steps

Ready for Day 3? Head to `../day-3/` to deploy your agent to the cloud!

---

**Pro Tip:** The best agents know when to use tools vs. when to rely on their own knowledge. Experiment with different prompting strategies!

