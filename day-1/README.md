# Day 1: Agent Loop + AI Twin v0

Goal: Build a basic agent loop and create your first AI twin using CrewAI (no tools/memory)

## What You'll Learn

- How to set up a CrewAI agent from scratch
- Understanding the agent loop (perception → reasoning → action)
- Creating agents, tasks, and crews
- Managing API keys securely
- Pushing your project to GitHub

## Objectives

- [ ] Set up your development environment
- [ ] Create a personal AI twin agent
- [ ] Understand agent-task-crew relationships
- [ ] Run your first agent (max 5 turns)
- [ ] Customize the agent backstory
- [ ] Push your code to GitHub
- [ ] Create AgentFacts for your agent

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp env_example.txt .env
# Edit .env and add your OpenAI API key from https://platform.openai.com/api-keys
```

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Run Your Agent

Basic version (single question):
```bash
python3 main.py
```

Interactive version (chat interface):
```bash
python3 interactive.py
```

## Understanding the Code

### main.py - The Core Agent

This file demonstrates the fundamental building blocks:

1. **LLM Configuration** (Lines 20-26)
   - Sets up the "brain" of your agent
   - Uses OpenAI's GPT-4o-mini model
   - Temperature controls creativity

2. **Agent Creation** (Lines 37-60)
   - `role`: What is the agent's identity?
   - `goal`: What is the agent trying to achieve?
   - `backstory`: What does the agent know? This is crucial!

3. **Task Definition** (Lines 68-80)
   - Describes what the agent should do
   - Uses input variables (e.g., `{question}`)
   - Specifies expected output

4. **Crew Setup** (Lines 88-92)
   - Orchestrates agents and tasks
   - Can manage multiple agents working together

5. **Execution** (Lines 100-119)
   - Runs the crew with inputs
   - Displays results

### interactive.py - Bonus Interactive Version

This creates a chat interface where you can have a conversation with your agent twin.

## Your Mission: Personalize Your Agent

1. Edit the backstory in `main.py` (around line 43):

```python
backstory="""
You are the digital twin of [YOUR NAME].

Here's what you know about me:
- I'm studying [YOUR FIELD]
- I'm passionate about [YOUR INTERESTS]
- My favorite [SOMETHING] is [YOUR FAVORITE]
- I have experience with [YOUR SKILLS]
- I'm currently working on [YOUR PROJECTS]

Add as much detail as you want - the more specific, the better!
"""
```

2. Try different questions - What can your agent answer about you?

3. Test the limits - What happens when you ask something it doesn't know?

## Experiments to Try

1. **Change the temperature** (line 25 in main.py):
   - Low (0.1-0.3): More focused, consistent
   - Medium (0.5-0.7): Balanced
   - High (0.8-1.0): More creative, varied

2. **Modify the role and goal**: What happens if you create a "Coding Tutor" instead of a personal twin?

3. **Add more details**: Include your schedule, favorite places, projects you're working on

4. **Make it interactive**: Uncomment the bonus challenge code (lines 122-129)

## Publishing to GitHub

1. Initialize git (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Day 1: Personal AI Twin"
   ```

2. Create a GitHub repository at https://github.com/new

3. Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

4. Important: Make sure `.env` is in `.gitignore` (it already is!) - NEVER commit API keys!

## Key Concepts

### Agent Loop (Max 5 Turns)
An agent follows this cycle:
1. **Perceive**: Receive input (question)
2. **Reason**: Process with LLM
3. **Act**: Generate response
4. **Repeat**: Continue for up to 5 iterations if needed

### Why No Tools or Memory Yet?
- **Day 1**: Focus on core concepts
- **Day 2**: We'll add memory so agents remember conversations
- **Day 2**: We'll add tools so agents can search the web, access APIs, etc.

## Troubleshooting

**Error: "No API key found"**
- Make sure `.env` file exists (not `env_example.txt`)
- Check that your API key is correctly formatted

**Error: "Module not found"**
- Run `pip install -r requirements.txt`
- Make sure you're in the correct directory

**Agent gives wrong answers**
- Add more detail to the backstory
- Adjust the temperature
- Make sure your instructions are clear

## Resources

- [CrewAI Quickstart](https://docs.crewai.com/quickstart)
- [CrewAI Core Concepts](https://docs.crewai.com/core-concepts)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## Checklist

Before moving to Day 2, make sure you:
- [ ] Successfully ran both `main.py` and `interactive.py`
- [ ] Personalized the agent backstory
- [ ] Understand the Agent-Task-Crew relationship
- [ ] Pushed your code to GitHub
- [ ] Can explain what an agent loop is
- [ ] Created AgentFacts documentation for your agent

## Next Steps

Ready for Day 2? Head to `../day-2/` to add memory and MCP tools to your agent.
