# 🏆 Day 5: Final Submit + Agent Battle

**Goal:** Polish your agent and compete in the NANDA Agent Battle!

## 📚 What You'll Learn

- Agent optimization strategies
- Performance tuning and testing
- Battle format and evaluation criteria
- Advanced tool integration
- Competitive agent design
- Real-time problem solving

## 🎯 Today's Objectives

- [ ] Optimize your agent for speed and accuracy
- [ ] Add advanced tools (web search, specialized APIs)
- [ ] Test across diverse topics
- [ ] Ensure consistent API format
- [ ] Submit to NANDA for battle
- [ ] Compete in the Agent Battle!
- [ ] Celebrate and share learnings

## 🎮 The Agent Battle

### Battle Format

Your agent will compete in multiple rounds:

1. **Trivia Round**: General knowledge questions
   - History, science, geography
   - Pop culture, sports, entertainment
   - Technology and current events

2. **Research Round**: Questions requiring web search
   - Current news and events
   - Real-time data (weather, stocks, etc.)
   - Latest developments in various fields

3. **Analysis Round**: Complex reasoning tasks
   - Problem-solving
   - Multi-step reasoning
   - Strategic thinking

4. **Speed Round**: Quick-fire questions
   - Test response time
   - Accuracy under pressure
   - Simple but fast

5. **Niche Round**: Specialized knowledge
   - Art and culture
   - Stock market and finance
   - Science and technology
   - History and politics

### Evaluation Criteria

Your agent will be scored on:

**Accuracy (40%)**
- Correctness of answers
- Factual accuracy
- Completeness

**Speed (20%)**
- Response time
- API latency
- Efficiency

**Reasoning (20%)**
- Quality of explanations
- Logic and coherence
- Depth of analysis

**Robustness (20%)**
- Handling edge cases
- Error recovery
- Consistency across topics

## 🚀 Optimization Strategies

### 1. Model Selection

```python
# Fast and affordable
llm = LLM(model="openai/gpt-4o-mini", temperature=0.3)

# More capable (slower, costlier)
llm = LLM(model="openai/gpt-4o", temperature=0.3)

# Balance of speed and quality
llm = LLM(model="openai/gpt-4o-mini", temperature=0.5)
```

**Recommendation**: Use `gpt-4o-mini` with temperature 0.3-0.5 for best speed/accuracy balance.

### 2. Essential Tools

```python
from crewai_tools import (
    SerperDevTool,      # Web search
    WebsiteSearchTool,   # Website scraping
    FileReadTool,        # Read files
    # Add more as needed
)

# Configure tools
search_tool = SerperDevTool(
    api_key=os.getenv("SERPER_API_KEY")
)

# Add to agent
agent = Agent(
    role="Battle Agent",
    tools=[search_tool],
    # ...
)
```

**Essential Tools for Battle:**
- Web search (Serper, Brave, or Google)
- Calculator for math
- Current date/time tool
- Optional: Weather, stock data, news APIs

### 3. Memory Configuration

```python
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,  # Enable for context
    # But be mindful of speed!
)
```

**Trade-off**: Memory improves context but slows responses. Test both!

### 4. Response Optimization

```python
# Concise responses for speed
task = Task(
    description=f"""
    Answer this question concisely: {question}
    
    Provide:
    - Direct answer first
    - Brief explanation (1-2 sentences)
    - Sources if using tools
    
    Be accurate and fast!
    """,
    expected_output="Concise accurate answer",
    agent=agent,
)
```

### 5. Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_query(question: str):
    """Cache responses for identical questions"""
    # Your agent query logic here
    pass
```

## 🛠️ Building Your Battle Agent

### Complete Battle-Ready Agent

```python
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import os

load_dotenv()

# Optimized LLM
llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.4,  # Balance creativity and consistency
)

# Essential tools
search_tool = SerperDevTool()

# Battle agent
battle_agent = Agent(
    role="NANDA Battle Champion",
    goal="Answer questions accurately and quickly across all topics",
    
    backstory="""
    You are an elite AI agent competing in the NANDA Agent Battle.
    
    Your strengths:
    - Broad knowledge across topics
    - Quick, accurate responses
    - Effective tool usage
    - Clear, concise communication
    
    Your strategy:
    - Answer directly and confidently
    - Use tools when needed for current data
    - Be fast but accurate
    - Explain reasoning briefly
    
    Topics you excel at:
    - General trivia and knowledge
    - Current events and news
    - Science and technology
    - History and culture
    - Problem-solving and analysis
    
    You always strive for accuracy over speed, but keep responses concise.
    """,
    
    tools=[search_tool],
    llm=llm,
    verbose=False,  # Faster in production
)

def answer_battle_question(question: str) -> str:
    """
    Answer a battle question
    
    Args:
        question: The battle question
        
    Returns:
        Concise, accurate answer
    """
    task = Task(
        description=f"""
        Answer this battle question: {question}
        
        Requirements:
        1. Provide accurate answer
        2. Keep it concise (2-3 sentences)
        3. Use tools if you need current data
        4. Cite sources if applicable
        """,
        expected_output="Concise accurate answer with brief explanation",
        agent=battle_agent,
    )
    
    crew = Crew(
        agents=[battle_agent],
        tasks=[task],
        verbose=False,
    )
    
    result = crew.kickoff()
    return str(result)
```

## 🧪 Testing Your Agent

### Test Across Categories

```python
# Trivia
questions = [
    "What is the capital of Japan?",
    "Who wrote Romeo and Juliet?",
    "What year did World War II end?",
]

# Current events (requires web search)
questions = [
    "What's the current weather in Boston?",
    "What's the latest news about AI?",
    "What's the price of Bitcoin today?",
]

# Analysis
questions = [
    "Compare renewable vs fossil fuel energy",
    "Explain how quantum computing works",
    "What are the pros and cons of remote work?",
]

# Speed test
import time
start = time.time()
answer = answer_battle_question("What is 2+2?")
elapsed = time.time() - start
print(f"Response time: {elapsed:.2f}s")
```

### Performance Benchmarks

**Target Metrics:**
- Simple questions: < 3 seconds
- Tool-required questions: < 8 seconds
- Complex analysis: < 15 seconds
- Accuracy: > 90% correct

## 📊 Battle Day Strategy

### Before the Battle

1. **Test your endpoint**
   ```bash
   curl https://your-agent.render.com/health
   curl -X POST https://your-agent.render.com/query \
     -d '{"question": "test"}'
   ```

2. **Check API keys** - All tools working?

3. **Monitor performance** - Response times acceptable?

4. **Pre-warm** - Send a test query to wake up your server

### During the Battle

1. **Monitor your logs** - Watch for errors
2. **Track performance** - Note which questions work well
3. **Stay calm** - Agents will make mistakes!
4. **Learn** - See what other agents do well

### After Each Round

1. **Quick fixes** - Can you improve between rounds?
2. **Adjust temperature** - Too creative or too rigid?
3. **Tool tuning** - Using the right tools?

## 🎨 Advanced Enhancements (If Time Permits)

### Multi-Model Strategy

```python
# Use different models for different question types
def get_best_model(question: str) -> str:
    if "calculate" in question.lower():
        return "gpt-4o-mini"  # Fast for simple math
    elif "analyze" in question.lower():
        return "gpt-4o"  # Better reasoning
    else:
        return "gpt-4o-mini"  # Default
```

### Confidence Scoring

```python
def answer_with_confidence(question: str):
    """Return answer with confidence score"""
    # Run multiple times, check consistency
    # Or ask agent to rate its confidence
    pass
```

### Ensemble Approach

```python
def ensemble_answer(question: str):
    """Get answers from multiple agents, vote"""
    answers = [
        agent1.answer(question),
        agent2.answer(question),
        agent3.answer(question),
    ]
    # Majority vote or judge picks best
    return best_answer
```

## 📝 Submission Requirements

### API Format (MANDATORY)

Your agent MUST implement:

```python
# POST /query
{
  "question": "What is the capital of France?"
}

# Response
{
  "answer": "The capital of France is Paris.",
  "agent_id": "your-agent-name",
  "timestamp": "2026-01-20T10:00:00Z",
  "confidence": 0.95  # optional
}
```

### Submission Checklist

- [ ] Deployed and accessible
- [ ] Health endpoint working
- [ ] Query endpoint returns correct format
- [ ] Tested across multiple question types
- [ ] Response times acceptable
- [ ] Error handling in place
- [ ] API keys secured
- [ ] Submitted to NANDA index

## 🏆 Competition Categories

### Main Battle
- Overall best agent
- Wins on total points across all rounds

### Special Awards
- **Fastest Agent**: Best average response time
- **Most Accurate**: Highest accuracy percentage
- **Best Reasoner**: Best explanations
- **Most Creative**: Unique or innovative approaches
- **Best Specialist**: Dominates a specific category
- **Most Improved**: Biggest improvement during course

## 🎉 After the Battle

### What to Do Next

1. **Share your agent**
   - Post on GitHub
   - Share with classmates
   - Write about your approach

2. **Keep learning**
   - What worked well?
   - What would you do differently?
   - What new tools to explore?

3. **Build on it**
   - Add more tools
   - Improve accuracy
   - Explore new use cases

4. **Connect**
   - Network with other participants
   - Join AI agent communities
   - Continue collaborating

## 📚 Resources for Continuous Learning

- [CrewAI Documentation](https://docs.crewai.com/)
- [LangChain Tools](https://python.langchain.com/docs/integrations/tools/)
- [NANDA Platform](https://nanda.ai)
- [AI Agent Communities](https://discord.gg/crewai)

## 💡 Final Tips

1. **Don't over-optimize** - Simple often wins
2. **Test on real questions** - Don't just guess
3. **Have fun!** - It's a learning experience
4. **Learn from others** - Best agents inspire ideas
5. **Be creative** - Unique approaches can win
6. **Stay humble** - Even top agents make mistakes
7. **Celebrate** - You built an AI agent from scratch!

## ✅ Day 5 Completion

Congratulations on completing the MIT IAP NANDA course!

You've learned:
- ✅ Agent fundamentals (Day 1)
- ✅ Memory and tools (Day 2)
- ✅ Deployment and APIs (Day 3)
- ✅ Multi-agent coordination (Day 4)
- ✅ Competition and optimization (Day 5)

**You're now an AI agent developer!** 🎉

---

## 🏅 Battle Leaderboard

*To be updated during the competition...*

1. TBD
2. TBD
3. TBD

---

**Good luck in the Agent Battle!** 🚀

*Built with ❤️ for MIT IAP 2026*

