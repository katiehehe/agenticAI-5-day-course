# 🤝 Day 4: Team Coordination Protocol

**Goal:** Build multi-agent systems with coordination protocols for agent-to-agent communication

## 📚 What You'll Learn

- Agent-to-agent (A2A) communication protocols
- Google A2A protocol implementation
- Coordination strategies (debate, consensus, hierarchical)
- Multi-agent task decomposition
- Merging agent outputs
- Team-based problem solving

## 🎯 Today's Objectives

- [ ] Understand A2A communication patterns
- [ ] Implement Google A2A protocol
- [ ] Create multiple specialized agents
- [ ] Build coordination mechanisms
- [ ] Implement debate and consensus protocols
- [ ] Test multi-agent collaboration
- [ ] Integrate with other students' agents

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Multi-Agent Examples

```bash
# Debate protocol
python debate_protocol.py

# Hierarchical coordination
python hierarchical_protocol.py

# Google A2A example
python google_a2a.py
```

## 📖 Understanding Multi-Agent Systems

### Single Agent (Days 1-3)
```
Question → Agent → Answer
```

### Multi-Agent (Day 4)
```
Question → Agent 1 ┐
           Agent 2 ├→ Coordinator → Merged Answer
           Agent 3 ┘
```

## 🏗️ Coordination Patterns

### 1. Debate Protocol

Agents present different perspectives and debate:

```python
Question: "Should we use microservices?"

Agent 1 (Pro):  "Yes, better scalability..."
Agent 2 (Con):  "No, added complexity..."
Judge Agent:    "Evaluates both sides and decides..."
```

### 2. Consensus Protocol

Agents vote and reach agreement:

```python
Question: "What's the capital of France?"

Agent 1: "Paris"
Agent 2: "Paris"  
Agent 3: "Paris"
Result:  "Paris (unanimous)"
```

### 3. Hierarchical Protocol

Manager delegates to specialized workers:

```python
Manager:   "Break down this complex problem"
Worker 1:  "Handles research"
Worker 2:  "Handles analysis"
Worker 3:  "Handles synthesis"
Manager:   "Combines all outputs"
```

## 🌐 Google A2A Protocol

### What is A2A?

Agent-to-Agent (A2A) is Google's protocol for standardized agent communication.

### Key Concepts

1. **Message Format**: Standardized JSON messages
2. **Capabilities**: Agents declare what they can do
3. **Handshake**: Agents negotiate communication
4. **Tasks**: Structured task delegation

### Example A2A Message

```json
{
  "protocol": "a2a",
  "version": "1.0",
  "from": "agent-1",
  "to": "agent-2",
  "type": "request",
  "task": {
    "description": "Analyze this data",
    "input": {...},
    "deadline": "2026-01-20T15:00:00Z"
  }
}
```

## 📁 Project Structure

```
day-4/
├── debate_protocol.py         # Debate-style coordination
├── consensus_protocol.py      # Voting and consensus
├── hierarchical_protocol.py   # Manager-worker pattern
├── google_a2a.py             # Google A2A implementation
├── agent_registry.py         # Track available agents
├── coordinator.py            # Coordination logic
├── requirements.txt          # Dependencies
└── README.md                 # This file!
```

## 🔧 Implementation Examples

### Debate Protocol

```python
from crewai import Agent, Task, Crew, LLM

# Create opposing agents
pro_agent = Agent(
    role="Advocate",
    goal="Argue for the proposition",
    backstory="You present strong arguments in favor"
)

con_agent = Agent(
    role="Opponent",
    goal="Argue against the proposition",
    backstory="You present strong counter-arguments"
)

judge_agent = Agent(
    role="Judge",
    goal="Evaluate both sides and reach a conclusion",
    backstory="You weigh evidence objectively"
)

# Coordinate the debate
def run_debate(question):
    # Pro argues
    pro_task = Task(
        description=f"Argue FOR: {question}",
        agent=pro_agent,
        expected_output="Strong arguments in favor"
    )
    
    # Con argues
    con_task = Task(
        description=f"Argue AGAINST: {question}",
        agent=con_agent,
        expected_output="Strong counter-arguments"
    )
    
    # Judge evaluates
    judge_task = Task(
        description=f"Evaluate debate on: {question}",
        agent=judge_agent,
        expected_output="Final verdict",
        context=[pro_task, con_task]  # Access other tasks
    )
    
    crew = Crew(
        agents=[pro_agent, con_agent, judge_agent],
        tasks=[pro_task, con_task, judge_task],
        verbose=True
    )
    
    return crew.kickoff()
```

### Hierarchical Protocol

```python
# Manager coordinates specialized workers
manager = Agent(
    role="Project Manager",
    goal="Coordinate team to solve complex problems",
    backstory="You delegate and synthesize"
)

researcher = Agent(
    role="Researcher",
    goal="Gather information",
    backstory="You find relevant facts"
)

analyst = Agent(
    role="Analyst",
    goal="Analyze data",
    backstory="You interpret information"
)

writer = Agent(
    role="Writer",
    goal="Create final output",
    backstory="You synthesize into clear answers"
)

def hierarchical_solve(question):
    # Research task
    research_task = Task(
        description=f"Research: {question}",
        agent=researcher,
        expected_output="Key facts and data"
    )
    
    # Analysis task
    analysis_task = Task(
        description="Analyze the research findings",
        agent=analyst,
        expected_output="Insights and patterns",
        context=[research_task]
    )
    
    # Writing task
    writing_task = Task(
        description="Write comprehensive answer",
        agent=writer,
        expected_output="Final polished answer",
        context=[research_task, analysis_task]
    )
    
    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential,  # One after another
        verbose=True
    )
    
    return crew.kickoff()
```

## 🌐 A2A Communication with Other Agents

### Calling Another Student's Agent

```python
import requests

def call_external_agent(url: str, question: str):
    """Call another team's deployed agent"""
    response = requests.post(
        f"{url}/query",
        json={"question": question},
        timeout=30
    )
    return response.json()

# Example: Get answers from multiple agents
agents = [
    "https://team1-agent.render.com",
    "https://team2-agent.render.com",
    "https://team3-agent.render.com"
]

def multi_agent_query(question, agent_urls):
    """Query multiple agents and merge responses"""
    responses = []
    
    for url in agent_urls:
        try:
            result = call_external_agent(url, question)
            responses.append({
                "agent": url,
                "answer": result["answer"]
            })
        except Exception as e:
            print(f"Error with {url}: {e}")
    
    # Merge responses (you decide how!)
    return merge_responses(responses)
```

## 🧪 Experiments to Try

### 1. Debate on Controversial Topics

```python
topics = [
    "Is AI beneficial or dangerous?",
    "Should we colonize Mars?",
    "Is remote work better than office work?"
]
```

### 2. Consensus Building

```python
# Get multiple agents to agree
question = "What's 2+2?"
# Should reach consensus quickly!

question = "What's the best programming language?"
# Harder to reach consensus!
```

### 3. Complex Task Decomposition

```python
# Break down a hard problem
question = "Write a business plan for a new startup"

# Manager delegates:
# - Market researcher
# - Financial analyst
# - Marketing strategist
# - Writer
```

### 4. Cross-Team Collaboration

```python
# Team up with classmates!
# Each team's agent contributes expertise:
# - Your agent: Technology
# - Team 2's agent: Business
# - Team 3's agent: Design
```

## 📊 Evaluation Strategies

### Voting

```python
def majority_vote(responses):
    """Simple majority voting"""
    from collections import Counter
    votes = Counter(responses)
    return votes.most_common(1)[0][0]
```

### Weighted Consensus

```python
def weighted_consensus(responses, weights):
    """Weight agents by confidence/expertise"""
    weighted_sum = sum(r * w for r, w in zip(responses, weights))
    return weighted_sum / sum(weights)
```

### Best Answer Selection

```python
def select_best_answer(responses, judge_agent):
    """Let a judge agent pick the best"""
    task = Task(
        description=f"Select best answer from: {responses}",
        agent=judge_agent,
        expected_output="Selected best answer with reasoning"
    )
    # ... run and return
```

## 🐛 Troubleshooting

**Agents disagreeing too much:**
- Add a judge/coordinator agent
- Use voting mechanisms
- Set clearer objectives

**Communication failing:**
- Check API endpoints are accessible
- Verify request/response formats
- Add timeout handling

**Too slow:**
- Run agents in parallel where possible
- Cache common queries
- Limit max_turns

**Coordination chaos:**
- Start with 2-3 agents
- Use hierarchical patterns
- Clear task delegation

## 📚 Resources

- [CrewAI Collaboration](https://docs.crewai.com/concepts/collaboration)
- [Google A2A Protocol](https://developers.google.com/a2a)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)
- [Consensus Algorithms](https://en.wikipedia.org/wiki/Consensus_(computer_science))

## ✅ Day 4 Checklist

Before moving to Day 5, make sure you:
- [ ] Implemented at least one coordination protocol
- [ ] Created 3+ specialized agents
- [ ] Successfully merged multi-agent outputs
- [ ] Tested agent-to-agent communication
- [ ] Collaborated with another team (optional)
- [ ] Understand Google A2A basics
- [ ] Can explain different coordination patterns

## 🎯 Next Steps

Ready for Day 5? Head to `../day-5/` to prepare for the Agent Battle!

---

**Pro Tip:** The best multi-agent systems have clear roles and communication protocols. Think of it like a well-organized team!

