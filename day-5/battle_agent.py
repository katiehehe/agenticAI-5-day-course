"""
Day 5: Battle-Ready Agent - Optimized for Competition
======================================================

This is your final agent optimized for the NANDA Agent Battle.
Fast, accurate, and equipped with essential tools!
"""

from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from dotenv import load_dotenv
import os
from datetime import datetime
from functools import lru_cache
import hashlib

load_dotenv()

# ==============================================================================
# Essential Tools for Battle
# ==============================================================================

@tool("web_search")
def web_search(query: str) -> str:
    """
    Search the web for current information.
    Use this for current events, news, or facts you're uncertain about.
    
    Args:
        query: Search query string
        
    Returns:
        Search results
    """
    # In production, use real search API:
    # - Serper: https://serper.dev
    # - Brave Search: https://brave.com/search/api/
    # - Google Custom Search
    
    # For demo/local testing:
    return f"[Web search for: {query}] - Add real search API key to use this tool!"

@tool("calculator")
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations.
    
    Args:
        expression: Math expression (e.g., "2 + 2", "sqrt(16)")
        
    Returns:
        Calculation result
    """
    try:
        # Safe eval for basic math
        import math
        allowed = {
            'sqrt': math.sqrt,
            'pow': math.pow,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'abs': abs,
            'round': round,
        }
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool("current_time")
def current_time() -> str:
    """
    Get the current date and time.
    
    Returns:
        Current date and time
    """
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC)"

# ==============================================================================
# Battle Agent Configuration
# ==============================================================================

# Optimized LLM settings
llm = LLM(
    model="openai/gpt-4o-mini",  # Fast and cost-effective
    temperature=0.4,              # Balanced: accurate but not too rigid
)

# Create battle-optimized agent
battle_agent = Agent(
    role="NANDA Battle Champion",
    
    goal="Answer questions accurately and efficiently across all topics",
    
    backstory="""
    You are an elite AI agent competing in the NANDA Agent Battle.
    
    Your expertise spans:
    - General knowledge and trivia (history, science, geography)
    - Current events and news
    - Technology and programming
    - Mathematics and problem-solving
    - Culture, art, and entertainment
    - Business and finance
    
    Your strengths:
    - Quick, accurate responses
    - Effective tool usage when needed
    - Clear, concise communication
    - Broad knowledge base
    
    Your strategy:
    1. Answer directly and confidently when you know
    2. Use web_search for current events or uncertain facts
    3. Use calculator for any mathematical operations
    4. Use current_time for date/time questions
    5. Keep responses concise (2-3 sentences typically)
    6. Cite sources when using tools
    
    Remember: Accuracy is more important than speed, but keep it snappy!
    """,
    
    tools=[web_search, calculator, current_time],
    llm=llm,
    verbose=False,  # Faster in production
)

# ==============================================================================
# Battle Query Function
# ==============================================================================

def answer_battle_question(question: str, use_cache: bool = True) -> dict:
    """
    Answer a battle question with optimization
    
    Args:
        question: The battle question
        use_cache: Whether to use caching (default True)
        
    Returns:
        Dict with answer, metadata, and timing
    """
    start_time = datetime.now()
    
    # Optional: Check cache
    if use_cache:
        cache_key = hashlib.md5(question.encode()).hexdigest()
        # Implement caching logic here if desired
    
    # Create optimized task
    task = Task(
        description=f"""
        Answer this question accurately and concisely: {question}
        
        Instructions:
        - Provide direct answer first
        - Add brief explanation (1-2 sentences)
        - Use tools if needed:
          * web_search for current events or uncertain facts
          * calculator for math
          * current_time for date/time
        - Cite source if using tools
        - Keep it concise!
        
        Format:
        [Direct Answer]
        [Brief explanation]
        [Source if applicable]
        """,
        expected_output="Concise accurate answer",
        agent=battle_agent,
    )
    
    # Execute
    crew = Crew(
        agents=[battle_agent],
        tasks=[task],
        verbose=False,
        memory=False,  # Disable for speed (enable if context helps)
    )
    
    result = crew.kickoff()
    
    # Calculate timing
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    return {
        "answer": str(result),
        "question": question,
        "timestamp": end_time.isoformat(),
        "processing_time": processing_time,
        "agent_id": "battle-champion"
    }

# ==============================================================================
# Testing & Benchmarking
# ==============================================================================

def benchmark_agent():
    """Test agent across different question types"""
    
    test_questions = {
        "Simple Trivia": [
            "What is the capital of Japan?",
            "Who wrote 1984?",
            "What is 2+2?",
        ],
        "Current Events": [
            "What year is it?",
            "What day is today?",
        ],
        "Math": [
            "What is the square root of 144?",
            "Calculate 25 * 4 + 10",
        ],
        "Knowledge": [
            "Explain photosynthesis briefly",
            "Who was the first president of the USA?",
            "What is the speed of light?",
        ],
    }
    
    print("\n" + "="*70)
    print("🏆 BATTLE AGENT BENCHMARK")
    print("="*70 + "\n")
    
    total_time = 0
    total_questions = 0
    
    for category, questions in test_questions.items():
        print(f"\n📊 Category: {category}")
        print("-" * 70)
        
        for question in questions:
            print(f"\n❓ Q: {question}")
            
            result = answer_battle_question(question)
            
            print(f"🤖 A: {result['answer']}")
            print(f"⏱️  Time: {result['processing_time']:.2f}s")
            
            total_time += result['processing_time']
            total_questions += 1
    
    avg_time = total_time / total_questions
    
    print("\n" + "="*70)
    print("📈 BENCHMARK RESULTS")
    print("="*70)
    print(f"Total Questions: {total_questions}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time: {avg_time:.2f}s per question")
    print("="*70 + "\n")

# ==============================================================================
# Main Execution
# ==============================================================================

if __name__ == "__main__":
    print("\n🏆 BATTLE AGENT - Ready for Competition!\n")
    
    # Choose mode
    mode = input("Choose mode:\n1. Interactive Q&A\n2. Run Benchmark\n\nEnter (1 or 2): ").strip()
    
    if mode == "2":
        # Run benchmark
        benchmark_agent()
    else:
        # Interactive mode
        print("\n" + "="*70)
        print("🎮 INTERACTIVE BATTLE MODE")
        print("="*70)
        print("\nAsk me anything! Type 'quit' to exit.\n")
        
        while True:
            question = input("❓ Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Good luck in the battle!\n")
                break
            
            if not question:
                continue
            
            print("\n🤔 Thinking...\n")
            result = answer_battle_question(question)
            
            print(f"🤖 Answer: {result['answer']}")
            print(f"⏱️  Time: {result['processing_time']:.2f}s\n")

# ==============================================================================
# Battle Tips
# ==============================================================================
"""
OPTIMIZATION TIPS:

1. Temperature (line 87):
   - Lower (0.2-0.4): More consistent, factual
   - Higher (0.5-0.7): More creative, varied

2. Tools:
   - Only add tools you actually use
   - Too many tools = slower selection
   - Test with and without each tool

3. Memory:
   - Disabled for speed (line 198)
   - Enable if context helps with follow-ups
   - Trade-off: accuracy vs speed

4. Response format:
   - Keep instructions clear but concise
   - "Concise" reminder helps agent be faster
   - Format guidance improves consistency

5. Caching:
   - Implement for repeated questions
   - Huge speed boost for common queries
   - Clear cache periodically

BATTLE STRATEGY:

1. Know your strengths:
   - Which topics do you excel at?
   - Which tools are most useful?

2. Monitor performance:
   - Track response times
   - Note accuracy on different types
   - Adjust based on results

3. Stay reliable:
   - Better to be consistently good
   - Than occasionally brilliant but often wrong

4. Learn from others:
   - See what winning agents do well
   - Adapt successful strategies
"""

