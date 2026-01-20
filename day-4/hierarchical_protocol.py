"""
Day 4: Hierarchical Protocol - Manager-Worker Pattern
======================================================

This implements a hierarchical coordination where a manager
delegates work to specialized workers and synthesizes results.
"""

from crewai import Agent, Task, Crew, LLM, Process
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# Initialize LLM
# ==============================================================================

llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.7,
)

# ==============================================================================
# Create Hierarchical Team
# ==============================================================================

manager = Agent(
    role="Project Manager",
    goal="Coordinate the team and synthesize results into final answer",
    backstory="""
    You are an experienced project manager who excels at delegation
    and synthesis. You break down complex problems, assign work to
    specialists, and combine their outputs into comprehensive solutions.
    """,
    llm=llm,
    verbose=True,
)

researcher = Agent(
    role="Research Specialist",
    goal="Gather relevant information and facts",
    backstory="""
    You are a thorough researcher who finds relevant information.
    You gather facts, data, and background information needed
    to answer questions comprehensively.
    """,
    llm=llm,
    verbose=True,
)

analyst = Agent(
    role="Data Analyst",
    goal="Analyze information and identify patterns",
    backstory="""
    You are an analytical thinker who interprets data.
    You find patterns, draw insights, and evaluate
    information critically.
    """,
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Content Writer",
    goal="Create clear, polished final output",
    backstory="""
    You are a skilled writer who creates clear, engaging content.
    You take complex information and present it in an
    accessible, well-structured way.
    """,
    llm=llm,
    verbose=True,
)

# ==============================================================================
# Hierarchical Coordination Function
# ==============================================================================

def hierarchical_solve(question: str):
    """
    Solve a complex question using hierarchical coordination
    
    Args:
        question: The question to answer
        
    Returns:
        Comprehensive answer from the team
    """
    
    print("\n" + "="*70)
    print(f"📊 HIERARCHICAL COORDINATION: {question}")
    print("="*70 + "\n")
    
    # Manager plans the work
    planning_task = Task(
        description=f"""
        Break down this question into research and analysis tasks:
        "{question}"
        
        Identify:
        1. What information needs to be researched
        2. What analysis needs to be done
        3. How to structure the final answer
        """,
        expected_output="A clear work plan with delegated tasks",
        agent=manager,
    )
    
    # Researcher gathers information
    research_task = Task(
        description=f"""
        Based on the work plan, research the following question:
        "{question}"
        
        Gather:
        - Key facts and data
        - Background information
        - Relevant examples
        - Important context
        """,
        expected_output="Comprehensive research findings (3-4 paragraphs)",
        agent=researcher,
        context=[planning_task],
    )
    
    # Analyst analyzes the research
    analysis_task = Task(
        description="""
        Analyze the research findings.
        
        Provide:
        - Key insights and patterns
        - Important conclusions
        - Connections between facts
        - Implications and significance
        """,
        expected_output="Detailed analysis (2-3 paragraphs)",
        agent=analyst,
        context=[research_task],
    )
    
    # Writer creates final output
    writing_task = Task(
        description=f"""
        Create a comprehensive answer to: "{question}"
        
        Synthesize:
        - Research findings
        - Analytical insights
        - Clear structure
        - Engaging presentation
        
        Make it clear, accurate, and well-organized.
        """,
        expected_output="Polished final answer (3-4 paragraphs)",
        agent=writer,
        context=[research_task, analysis_task],
    )
    
    # Manager reviews and finalizes
    final_review_task = Task(
        description="""
        Review the team's work and create the final output.
        
        Ensure:
        - Question is fully answered
        - Information is accurate
        - Structure is clear
        - Quality is high
        
        Add any final touches or synthesis needed.
        """,
        expected_output="Final reviewed and approved answer",
        agent=manager,
        context=[planning_task, research_task, analysis_task, writing_task],
    )
    
    # Create and run crew
    crew = Crew(
        agents=[manager, researcher, analyst, writer],
        tasks=[planning_task, research_task, analysis_task, writing_task, final_review_task],
        process=Process.sequential,
        verbose=True,
    )
    
    result = crew.kickoff()
    
    print("\n" + "="*70)
    print("✅ FINAL ANSWER")
    print("="*70)
    print(result)
    print("="*70 + "\n")
    
    return result

# ==============================================================================
# Main Execution
# ==============================================================================

if __name__ == "__main__":
    # Example complex questions
    questions = [
        "Explain how machine learning works and give examples of its applications",
        "What are the benefits and challenges of renewable energy?",
        "How has social media changed communication in the 21st century?",
    ]
    
    print("\n📊 HIERARCHICAL PROTOCOL DEMONSTRATION\n")
    print("This demonstrates multi-agent coordination using manager-worker pattern.\n")
    
    # Choose a question
    question = questions[0]  # Change index to try different questions
    
    # Or create your own:
    # question = input("Enter your question: ")
    
    result = hierarchical_solve(question)

# ==============================================================================
# Tips for Students
# ==============================================================================
"""
EXPERIMENT WITH:

1. Add more specialists:
   - Fact-checker
   - Critic/reviewer
   - Domain expert
   - Illustrator/visualizer
   
2. Parallel work:
   - Have multiple researchers work simultaneously
   - Use Process.parallel for independent tasks
   
3. Quality control:
   - Add a QA agent
   - Implement review rounds
   - Add scoring/validation
   
4. Dynamic delegation:
   - Manager decides which specialists to use
   - Adapt team based on question type
   
5. Real tools:
   - Add web search to researcher
   - Add calculators to analyst
   - Add formatting tools to writer

COORDINATION INSIGHTS:

- Manager coordinates through task context
- Sequential process ensures dependencies are met
- Each specialist focuses on their expertise
- Final synthesis combines all perspectives
- Clear delegation improves efficiency
"""

