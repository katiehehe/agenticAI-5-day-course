# Day 4: A2A Communication Protocol

**Goal:** Implement Agent-to-Agent (A2A) communication protocol, allowing agents to discover and message each other

---

## Quick Update from Day 3

Already deployed yesterday? Here's your simple checklist:

### Step-by-Step Deployment

1. **Edit Your Agent Info** (in `main.py`, lines 108-116)

   ```python
   MY_AGENT_USERNAME = "your-username"      # Change this
   MY_AGENT_NAME = "Your Agent Name"        # Change this
   MY_AGENT_DESCRIPTION = "What your agent does"  # Change this
   MY_AGENT_PROVIDER = "Your Name"          # Change this
   MY_AGENT_PROVIDER_URL = "https://your-website.com"  # Change this
   ```

   These are NOT secrets - they're public info shown in AgentFacts!

2. **Deploy**

   ```bash
   cd day-4
   railway link  # Link to your existing project from Day 3
   railway up    # Deploys the new code with your info
   ```

   Your existing `OPENAI_API_KEY` environment variable is still there from Day 3

3. **Get Your URL**

   ```bash
   railway domain  # Gets your public URL
   ```

   Example: `https://day-4-agent.up.railway.app`

4. **Test Your New Endpoints**

   ```bash
   # Test AgentFacts
   curl https://YOUR_URL.up.railway.app/agentfacts

   # Test A2A endpoint (direct message to your agent)
   curl -X POST https://YOUR_URL.up.railway.app/a2a \
     -H "Content-Type: application/json" \
     -d '{
       "content": {
         "text": "Hello! What can you help me with?",
         "type": "text"
       },
       "role": "user",
       "conversation_id": "test123"
     }'

   # Test A2A routing (message another agent via your agent)
   curl -X POST https://YOUR_URL.up.railway.app/a2a \
     -H "Content-Type: application/json" \
     -d '{
       "content": {
         "text": "@classmate-agent Can you help with this task?",
         "type": "text"
       },
       "role": "user",
       "conversation_id": "test456"
     }'

   # Test smart search (auto-find and route to suitable agent)
   curl -X POST https://YOUR_URL.up.railway.app/search \
     -H "Content-Type: application/json" \
     -d '{
       "query": "send an email",
       "conversation_id": "search-123"
     }'
   ```

5. **Register in Central Registry** (Important for A2A!)
   - Go to: `https://nest.projectnanda.org`
   - Click "Add Agent"
   - Enter your agent info (username, name, URL, description)
   - Your agent will now automatically discover other registered agents!

6. **Done!** Your agent now has:
   - A2A messaging at `/a2a`
   - Smart agent search at `/search` (auto-finds best agent)
   - AgentFacts at `/agentfacts`
   - Automatic agent discovery via central registry
   - All Day 3 features (memory, tools)
   - Standalone testing GUI in `testing/agent_test_gui.html`

**Need more details?** See full guide below

---

## What You'll Learn

- **What is A2A?** Agent-to-Agent communication protocol
- **Message Routing:** Using `@agent-id` syntax to route messages
- **Agent Discovery:** Using AgentFacts for capability sharing
- **Smart Agent Search:** Automatic agent selection using LLM
- **Cross-Agent Collaboration:** Agents working together on tasks

---

## Understanding A2A Communication Protocol

### What is A2A (Agent-to-Agent Communication)?

A2A is a communication protocol that allows agents to:

- **Discover each other** - Find other agents and their capabilities
- **Send messages** - Direct communication between agents
- **Collaborate** - Work together on complex tasks
- **Stay opaque** - Don't expose internal logic or tools

### Simple Example

```
Your Agent → "@furniture-expert What sofa should I buy?" → Furniture Agent
                                                                    ↓
Your Agent ← "I recommend a modern sectional sofa..." ← Furniture Agent
```

### Based on NEST/NANDA Approach

This implementation is inspired by the [NEST repository](https://github.com/projnanda/NEST), which uses:

- Simple `@agent-id` syntax for routing
- HTTP-based communication
- Agent registry for discovery
- Direct message forwarding

---

## Architecture

```
                    ┌──────────────────────────────────────┐
                    │   Central Agent Registry             │
                    │   nanda-testbed-production           │
                    │                                      │
                    │   - Stores all registered agents     │
                    │   - Agents fetch list on startup     │
                    │   - Automatic discovery!             │
                    └──────────────────────────────────────┘
                                    ↑
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
        ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
        │  Your Agent    │  │ Classmate's    │  │  Other Agents  │
        │  (Day 4)       │  │ Agent          │  │                │
        └────────────────┘  └────────────────┘  └────────────────┘
                ↕ A2A Messages (@agent-id routing) ↕

┌─────────────────────────────────────┐
│  Your Agent (Day 4)                 │
│  https://your-agent.railway.app     │
│                                     │
│  New Endpoints:                     │
│  - GET  /agentfacts (NEW!)          │  ← Discovery
│  - POST /a2a        (NEW!)          │  ← Agent-to-Agent ONLY (requires @agent-id)
│  - POST /search     (NEW!)          │  ← Auto-find and route to suitable agent
│  - GET  /agents     (NEW!)          │  ← List known agents
│                                     │
│  From Day 3:                        │
│  - POST /query                      │  ← Direct queries to this agent
│  - GET  /health                     │
│                                     │
│  Testing:                           │
│  - testing/agent_test_gui.html     │  ← Standalone testing GUI
│                                     │
│  Logging:                           │
│  - logs/a2a_messages.log            │  ← All A2A routing messages
│                                     │
│  On Startup:                        │
│  - Fetches agents from registry     │
│  - Auto-discovers all agents        │
└─────────────────────────────────────┘
```

### Important: Three Endpoints for Different Purposes

1. **`POST /query`** (from Day 3) - Direct queries to YOUR agent

   ```bash
   curl -X POST .../query -d '{"question": "What is 2+2?"}'
   ```

2. **`POST /a2a`** (NEW!) - Agent-to-agent routing ONLY

   ```bash
   curl -X POST .../a2a -d '{"content":{"text":"@other-agent Help!","type":"text"},...}'
   ```

   **Must include `@agent-id` or you'll get an error!**

3. **`POST /search`** (NEW!) - Smart agent search and routing
   ```bash
   curl -X POST .../search -d '{"query": "send an email", "conversation_id": "conv-123"}'
   ```
   **Automatically finds the best agent from the database and routes your message!**

### Central Registry

All agents are registered in a central registry at:

- **URL:** `https://nest.projectnanda.org`
- **API:** `https://nest.projectnanda.org/api/agents`

**Benefits:**

- Single source of truth for all agents
- Automatic agent discovery on startup
- No manual registration between agents
- Easy to add new agents to the network

---

## Quick Start

### For Railway Deployment (You Already Have Day 3 Running)

**See the "Quick Update from Day 3" section at the top!**

### For Local Testing (Optional)

```bash
# 1. Install dependencies
cd day-4
pip install -r requirements.txt

# 2. Edit your agent info in main.py (lines 108-116)
# Change MY_AGENT_USERNAME, MY_AGENT_NAME, etc.

# 3. Configure secrets
cp env_example.txt .env
# Edit .env with your OPENAI_API_KEY

# 4. Run locally
uvicorn main:app --reload

# 5. Visit
http://localhost:8000/docs
http://localhost:8000/agentfacts

# 6. Test with GUI (Optional)
# Open testing/agent_test_gui.html in your browser
# Or use the Python server:
python testing/serve_gui.py
# Then visit http://localhost:8080/agent_test_gui.html
```

---

## Testing A2A Communication

### Test 1: Check Your Agent Info

```bash
curl http://localhost:8000/
```

**Expected response:**

```json
{
  "message": "Personal Agent Twin API with A2A - Day 4",
  "agent_id": "personal-agent-twin",
  "agent_name": "Personal Agent Twin",
  "a2a_enabled": true,
  "known_agents": []
}
```

### Test 2: Send a Direct Message (No Routing)

```bash
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "text": "What is 2+2?",
      "type": "text"
    },
    "role": "user",
    "conversation_id": "test123"
  }'
```

**Expected:** Your agent responds directly (no `@agent-id` mention, so processes locally)

### Test 3: Register Another Agent

First, register another agent to enable routing:

```bash
curl -X POST "http://localhost:8000/agents/register?agent_id=test-agent&agent_url=http://example.com/a2a"
```

**Expected response:**

```json
{
  "message": "Agent 'test-agent' registered successfully",
  "agent_id": "test-agent",
  "agent_url": "http://example.com/a2a",
  "total_known_agents": 1
}
```

### Test 4: Route Message to Another Agent

```bash
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "text": "@test-agent Can you help me with this task?",
      "type": "text"
    },
    "role": "user",
    "conversation_id": "test456"
  }'
```

**What happens:**

1. Your agent sees `@test-agent` mention
2. Extracts the target agent ID: `test-agent`
3. Looks up the agent's URL from registry
4. Forwards message: "Can you help me with this task?" (without the @mention)
5. Returns the other agent's response

**This is the key A2A feature!** You ask YOUR agent to message ANOTHER agent.

---

## How It Works

### 1. Message Format (NEST-style)

```json
{
  "content": {
    "text": "Your message here",
    "type": "text"
  },
  "role": "user",
  "conversation_id": "unique-id"
}
```

### 2. Agent Mentions with `@agent-id`

When you include `@agent-id` in the message:

- `@furniture-expert What sofa should I buy?`
- `@travel-agent Plan a trip to Paris`
- `@code-helper Debug my Python script`

The agent:

1. Extracts the agent ID (`furniture-expert`)
2. Removes the mention from the message
3. Routes to that agent's `/a2a` endpoint
4. Returns the response

### 3. Agent Registry

```python
# In-memory registry (simple approach)
KNOWN_AGENTS = {
    "furniture-expert": "http://furniture-agent.railway.app/a2a",
    "travel-agent": "http://travel-agent.railway.app/a2a",
}
```

**In production**, you'd use:

- Database (PostgreSQL, MongoDB)
- External registry service (like NANDA registry)
- Service discovery (Consul, Kubernetes)

---

## Code Deep Dive

### Key Components

#### 1. A2A Message Model

```python
class A2AMessage(BaseModel):
    content: Dict[str, Any]  # {"text": "message", "type": "text"}
    role: str = "user"
    conversation_id: str
```

#### 2. Parse Agent Mentions

```python
def extract_agent_mentions(text: str) -> list[str]:
    """Extract @agent-id mentions from text"""
    pattern = r'@([\w-]+)'
    mentions = re.findall(pattern, text)
    return mentions
```

#### 3. Send Message to Agent

```python
async def send_message_to_agent(agent_id: str, message: str, conversation_id: str) -> str:
    """Send a message to another agent via A2A"""
    agent_url = KNOWN_AGENTS[agent_id]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            agent_url,
            json={
                "content": {"text": message, "type": "text"},
                "role": "user",
                "conversation_id": conversation_id
            }
        )
        data = response.json()
        return data.get("content", {}).get("text", str(data))
```

#### 4. A2A Endpoint

```python
@app.post("/a2a")
async def a2a_endpoint(message: A2AMessage):
    """Handle A2A messages"""
    text_content = message.content.get("text", "")

    # Check if routing to another agent
    target_agent, clean_message = parse_a2a_request(text_content)

    if target_agent:
        # Route to another agent
        agent_response = await send_message_to_agent(target_agent, clean_message, ...)
        return {"content": {"text": agent_response, ...}}
    else:
        # Process locally with CrewAI agent
        result = crew.kickoff()
        return {"content": {"text": result.raw, ...}}
```

---

## Deploy to Railway

### If You Already Deployed Day 3

**Great!** See the "Quick Update from Day 3" section at the top.

Just run:

```bash
cd day-4
railway link  # Links to your existing project
railway up    # Deploys new code
```

Add the new environment variables in Railway Dashboard, and you're done!

### If This is Your First Deployment

1. **Edit Your Agent Info** (in `main.py`, lines 108-116)

   ```python
   MY_AGENT_USERNAME = "your-username"      # Change this
   MY_AGENT_NAME = "Your Agent Name"        # Change this
   MY_AGENT_DESCRIPTION = "What your agent does"  # Change this
   MY_AGENT_PROVIDER = "Your Name"          # Change this
   MY_AGENT_PROVIDER_URL = "https://your-site.com"  # Change this
   ```

2. **Deploy**

   ```bash
   cd day-4
   railway login    # First time only
   railway link     # Create or link to project
   railway up       # Deploy
   ```

3. **Add Environment Variables** (in Railway Dashboard → Variables)

   ```
   OPENAI_API_KEY=your-key     # This is the only secret!
   ```

4. **Add Volume for Memory** (in Railway Dashboard → Settings → Volumes)
   - Mount Path: `/root/.local/share/crewai`
   - Size: 1 GB

5. **Get URL**

   ```bash
   railway domain
   ```

6. **Test**

   ```bash
   # Test AgentFacts
   curl https://YOUR_URL.up.railway.app/agentfacts

   # Test direct query (use /query for YOUR agent)
   curl -X POST https://YOUR_URL.up.railway.app/query \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is 2+2?"
     }'

   # Test A2A routing (requires @agent-id)
   curl -X POST https://YOUR_URL.up.railway.app/a2a \
     -H "Content-Type: application/json" \
     -d '{
       "content": {
         "text": "@classmate-agent Can you help me?",
         "type": "text"
       },
       "role": "user",
       "conversation_id": "test123"
     }'
   ```

### Register Your Agent in the Central Registry (IMPORTANT!)

**After deployment**, register your agent so other agents can discover it!

**Option A: Web Interface** (Easiest)

1. Go to `https://nest.projectnanda.org`
2. Click **"Add Agent"**
3. Fill in the form:
   - **Username**: Your `MY_AGENT_USERNAME` (e.g., `maria-agent`)
   - **Name**: Your `MY_AGENT_NAME` (e.g., `Maria's Agent`)
   - **URL**: Your Railway URL (e.g., `https://your-agent.up.railway.app`)
   - **Description**: What your agent does
4. Click **"Register Agent"**

**Option B: Using curl**

```bash
curl -X POST https://nest.projectnanda.org/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "your-agent-username",
    "name": "Your Agent Name",
    "endpoint": "https://YOUR_URL.up.railway.app",
    "description": "What your agent specializes in"
  }'
```

**What happens after registration?**

- Your agent appears in the central registry
- Other agents can discover and message your agent
- Your agent automatically discovers other registered agents on startup
- No manual agent registration needed anymore!

**Check if registration worked:**

```bash
# See all registered agents
curl https://nest.projectnanda.org/api/agents
```

---

## Smart Agent Search

### What is the `/search` Endpoint?

The `/search` endpoint automatically finds and routes to the best agent for your query. Instead of manually specifying `@agent-id`, you describe what you want to do, and the system:

1. **Fetches all agents** from the agentfacts database (`https://v0-agent-facts-database.vercel.app/api/agentfacts`)
2. **Uses an LLM** to analyze your query and match it to agent capabilities
3. **Selects the best agent** based on description, label, and skills
4. **Routes your message** to that agent automatically
5. **Returns the response** from the selected agent

### Example Usage

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I need to translate this text to Spanish",
    "conversation_id": "conv-123"
  }'
```

**What happens:**

- System analyzes: "translate text to Spanish"
- LLM matches to "Translation Agent" from the database
- Message is routed to the Translation Agent
- You get the translation response

### Request Format

```json
{
  "query": "your natural language request",
  "conversation_id": "unique-conversation-id",
  "user_id": "optional-user-id"
}
```

### Response Format

```json
{
  "selected_agent": {
    "id": "nanda:agent-id",
    "label": "Agent Name",
    "description": "What the agent does",
    "endpoint": "http://agent-url/a2a"
  },
  "agent_response": "Response from the selected agent",
  "timestamp": "2026-01-26T10:30:00",
  "processing_time": 2.5
}
```

### How Agent Selection Works

The LLM analyzes:

- **Query intent**: What the user wants to accomplish
- **Agent descriptions**: What each agent specializes in
- **Agent skills**: Capabilities listed in agentfacts
- **Best match**: Selects the single most suitable agent

If no suitable agent is found, the endpoint returns a 404 error.

### Benefits

- **No manual agent discovery** - Just describe what you need
- **Intelligent matching** - LLM understands context and intent
- **Automatic routing** - No need to know agent IDs or endpoints
- **Works with any agent** - As long as it's in the agentfacts database

## AgentFacts: Agent Discovery

### What is AgentFacts?

AgentFacts is like a "business card" for your agent. It tells other agents:

- Who you are (`agent_name`, `label`)
- What you can do (`skills`)
- How to reach you (`endpoints`)
- Performance metrics (`telemetry`)

### View Your AgentFacts

```bash
curl https://YOUR_URL.up.railway.app/agentfacts
```

You'll see JSON with all your agent's info - auto-generated from your config!

### Share with Classmates

Share this URL with classmates:

```
https://YOUR_URL.up.railway.app/agentfacts
```

They can discover your agent's capabilities and connect to it!

---

## Connecting with Classmates

### Automatic Agent Discovery

**Good news:** With the central registry, agents automatically discover each other! No manual registration needed.

### Scenario: Two Students Want to Connect

**You deployed:**

- Agent Username: `maria-agent`
- URL: `https://maria-agent.railway.app`
- **Registered in central registry**

**Classmate deployed:**

- Agent Username: `john-agent`
- URL: `https://john-agent.railway.app`
- **Registered in central registry**

### What Happens Automatically

When both agents are registered in the central registry:

1. **On startup**, each agent fetches the registry
2. **Discovers all other agents** (including each other)
3. **Ready to communicate** immediately!

You'll see this in startup logs:

```
Fetching agents from registry: https://nest.projectnanda.org/api/agents
Fetched 5 agents from registry
   Registered: @john-agent -> https://john-agent.railway.app/a2a
   Registered: @sarah-agent -> https://sarah-agent.railway.app/a2a
   Registered: @mike-agent -> https://mike-agent.railway.app/a2a
Known Agents: 3
```

### Verify Discovery

Check which agents are registered:

```bash
# View all registered agents
curl https://nest.projectnanda.org/api/agents

# Check what agents YOUR agent knows
curl https://maria-agent.railway.app/agents
```

### Send Messages!

**You message John's agent (via your agent):**

```bash
# You send to YOUR agent, asking it to message John's agent
curl -X POST https://maria-agent.railway.app/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "text": "@john-agent Can you help me with this research task?",
      "type": "text"
    },
    "role": "user",
    "conversation_id": "collab-1"
  }'
```

**What happens:**

1. You send to YOUR agent (maria-agent)
2. Your agent sees `@john-agent` and routes the message
3. Your agent forwards to John's `/a2a` endpoint
4. John's agent processes: "Can you help me with this research task?"
5. John's agent responds
6. Your agent returns John's response to you

**Result:** Your agent acts as a router/proxy to John's agent!

### Test 5: Smart Agent Search (NEW!)

Instead of manually specifying `@agent-id`, use the `/search` endpoint to automatically find the best agent:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "send an email",
    "conversation_id": "search-123"
  }'
```

**What happens:**

1. Fetches all agents from the agentfacts database
2. Uses LLM to analyze your query and select the best matching agent
3. Automatically routes your message to that agent
4. Returns the agent's response

**Response:**

```json
{
  "selected_agent": {
    "id": "nanda:...",
    "label": "Email Agent",
    "description": "Handles email operations",
    "endpoint": "http://email-agent.railway.app/a2a"
  },
  "agent_response": "I can help you send an email...",
  "timestamp": "2026-01-26T...",
  "processing_time": 2.5
}
```

**Benefits:**

- No need to know agent IDs beforehand
- LLM intelligently matches your intent to agent capabilities
- Works with the central agentfacts database
- Automatic endpoint discovery

### What if I don't include @agent-id?

**You'll get an error!** This is by design.

```bash
# This will FAIL
curl -X POST https://maria-agent.railway.app/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "text": "What is 2+2?",
      "type": "text"
    },
    "role": "user",
    "conversation_id": "test"
  }'
```

**Response:**

```json
{
  "detail": "ERROR: /a2a endpoint requires @agent-id for routing.\n\nYour message: 'What is 2+2?'\n\nThis endpoint is ONLY for agent-to-agent communication.\nYou must include @agent-id to route to another agent.\n\nFor direct queries to THIS agent, use POST /query instead."
}
```

**Why?**

- `/a2a` is ONLY for agent-to-agent routing
- For direct queries, use `/query` endpoint instead
- No silent fallbacks - be explicit!

### Logging

All A2A messages are logged to `logs/a2a_messages.log`:

```
2025-01-24 10:30:15 | INFO | INCOMING | conversation_id=test123 | message=@john-agent Can you help?
2025-01-24 10:30:15 | INFO | ROUTING | conversation_id=test123 | target=john-agent | message=Can you help?
2025-01-24 10:30:16 | INFO | SUCCESS | conversation_id=test123 | target=john-agent | response_length=245
```

**Error logs:**

```
2025-01-24 10:31:00 | ERROR | NO_TARGET | conversation_id=test456 | message=What is 2+2?
```

Check your logs to debug A2A routing!

---

## Use Cases

### 1. Multi-Agent Research Team

```
Researcher Agent → "@data-analyst Analyze this dataset"
                → "@writer Create a summary report"
                → "@visualizer Make charts"
```

### 2. Customer Support Network

```
Support Agent → "@billing-expert Handle refund request"
              → "@tech-support Debug connection issue"
```

### 3. Educational Assistant Network

```
Student Agent → "@math-tutor Help with calculus"
              → "@writing-coach Review my essay"
              → "@career-advisor Career guidance"
```

---

## Testing GUI

A standalone dark-themed web GUI is available for testing all endpoints locally.

### Quick Start

1. **Start your agent:**

   ```bash
   uvicorn main:app --reload
   ```

2. **Open the GUI:**
   Open `testing/agent_test_gui.html` directly in your browser

### Features

The GUI provides tabs for:

- **Health Check** - Verify agent is running
- **Query Agent** - Send direct queries to your agent
- **Search & Route** - Smart agent search (uses `/search` endpoint)
- **A2A Communication** - Manual agent routing with `@agent-id`
- **List Agents** - View all known agents
- **Agent Facts** - View your agent's metadata
- **Register Agent** - Add new agents manually

### Usage

1. Configure the Base URL (default: `http://localhost:8000`)
2. Select a tab for the endpoint you want to test
3. Fill in the form fields
4. Click the button to send the request
5. View the formatted JSON response

The GUI is completely separate from the agent - it's just an HTML file that makes HTTP requests.

## Troubleshooting

### Problem: AgentFacts shows wrong URL

**Symptom:** Endpoints show `http://localhost:8000` instead of Railway URL

**Solution:** Railway sets `PUBLIC_URL` automatically via `RAILWAY_PUBLIC_DOMAIN`. This happens after first deployment. If it's still wrong after deployment, check Railway logs to see if the domain is set.

### Problem: Agent not found when routing

**Symptom:** `Agent 'xyz' not found`

**Solution:** Register the agent first:

```bash
curl -X POST "https://your-url/agents/register?agent_id=xyz&agent_url=https://their-url/a2a"
```

### Problem: Deployment fails

**Symptom:** Railway build fails

**Solutions:**

- Check Railway logs: `railway logs`
- Verify all environment variables are set (especially `OPENAI_API_KEY`)
- Make sure `railway.json` exists in day-4 folder

### Problem: Memory not persisting

**Symptom:** Agent forgets previous conversations after restart

**Solution:** Add Railway Volume (from Day 3):

- Railway Dashboard → Settings → Volumes
- Mount Path: `/root/.local/share/crewai`
- Size: 1 GB

### Problem: Getting "requires @agent-id" error

**Symptom:** `/a2a` endpoint returns error about missing @agent-id

**This is correct behavior!** The `/a2a` endpoint is ONLY for agent-to-agent routing.

**Solutions:**

1. If you want to query YOUR agent directly, use `/query` instead:
   ```bash
   curl -X POST https://your-url/query -d '{"question":"your question"}'
   ```
2. If you want to route to another agent, include @agent-id:
   ```bash
   curl -X POST https://your-url/a2a -d '{... "text":"@other-agent your message" ...}'
   ```

### Problem: Can't connect to classmate's agent

**Symptom:** Timeout or error when messaging another agent

**Solutions:**

1. Check their agent is deployed: `curl https://their-url/health`
2. Verify their `/a2a` endpoint exists: `curl https://their-url/agentfacts`
3. Make sure you registered them correctly
4. Check your logs: `logs/a2a_messages.log` for error details
5. Check they're using the right agent-id

---

## Resources

- [NEST Repository](https://github.com/projnanda/NEST) - The inspiration for this implementation
- [Google A2A Protocol](https://github.com/a2aproject/A2A) - Full A2A specification
- [NANDA Project](https://github.com/projnanda) - Networked AI Agents

---

## Day 4 Checklist

**Deployment:**

- [ ] Edited agent info in `main.py` (lines 108-116)
- [ ] Updated code: `railway link` → `railway up`
- [ ] Got my public URL: `railway domain`
- [ ] Verified deployment: visited `/health` endpoint

**Testing:**

- [ ] Tested AgentFacts: `curl https://my-url/agentfacts`
- [ ] Tested A2A endpoint: sent a message to `/a2a`
- [ ] Tested Search endpoint: `curl -X POST .../search -d '{"query":"send an email"}'`
- [ ] Verified my agent responds correctly
- [ ] Used the testing GUI to test all endpoints
- [ ] Ran test suite: `python test_a2a.py`

**Collaboration:**

- [ ] Shared my AgentFacts URL with a classmate
- [ ] Got a classmate's AgentFacts URL
- [ ] Registered their agent using `/agents/register`
- [ ] Sent a message to their agent using `@their-agent-id`
- [ ] Received a response from their agent!

**Bonus:**

- [ ] Customized my AgentFacts description
- [ ] Added more skills to my agent
- [ ] Connected with multiple classmates

---

## Next Steps

### Day 5: Coordination Protocol + Agent Battle

- Implement advanced coordination protocols
- Connect to NANDA registry
- Optimize your agent for the Agent Battle
- Compete using the Agent Smart Score evaluation system

---

**Congratulations!** Your agent can now communicate with other agents using the A2A protocol!
