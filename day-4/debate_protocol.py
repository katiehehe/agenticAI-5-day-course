"""
Day 4: Debate Protocol - Multi-Agent Coordination
==================================================

This implements a debate-style coordination where agents argue
different perspectives and a judge makes the final decision.
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
# Create Debate Agents
# ==============================================================================

advocate = Agent(
    role="Advocate",
    goal="Present strong arguments in favor of the proposition",
    backstory="""
    You are a skilled debater who builds compelling cases.
    You present evidence, logic, and persuasive arguments
    to support your position. You anticipate counterarguments
    and address them proactively.
    """,
    llm=llm,
    verbose=True,
)

opponent = Agent(
    role="Opponent",
    goal="Present strong arguments against the proposition",
    backstory="""
    You are a critical thinker who challenges ideas.
    You identify weaknesses, present counterevidence,
    and build strong arguments against the proposition.
    You're respectful but firm in your opposition.
    """,
    llm=llm,
    verbose=True,
)

judge = Agent(
    role="Judge",
    goal="Evaluate both sides objectively and reach a fair conclusion",
    backstory="""
    You are an impartial judge who weighs evidence carefully.
    You listen to both sides, evaluate their arguments,
    and reach a balanced, well-reasoned conclusion.
    You explain your reasoning clearly.
    """,
    llm=llm,
    verbose=True,
)

# ==============================================================================
# Debate Coordination Function
# ==============================================================================

def run_debate(topic: str):
    """
    Run a debate on a given topic
    
    Args:
        topic: The debate topic/question
        
    Returns:
        The judge's final verdict
    """
    
    print("\n" + "="*70)
    print(f"🎭 DEBATE: {topic}")
    print("="*70 + "\n")
    
    # Opening statement - FOR
    opening_for = Task(
        description=f"""
        Present your opening argument FOR the following proposition:
        "{topic}"
        
        Build a strong case with evidence and reasoning.
        Be persuasive and anticipate counterarguments.
        """,
        expected_output="A compelling argument in favor (2-3 paragraphs)",
        agent=advocate,
    )
    
    # Opening statement - AGAINST
    opening_against = Task(
        description=f"""
        Present your opening argument AGAINST the following proposition:
        "{topic}"
        
        Challenge the proposition with evidence and reasoning.
        Be critical and identify potential weaknesses.
        """,
        expected_output="A strong counterargument (2-3 paragraphs)",
        agent=opponent,
    )
    
    # Rebuttal - FOR
    rebuttal_for = Task(
        description="""
        Review the opposition's argument and present your rebuttal.
        Address their points directly and reinforce your position.
        """,
        expected_output="A strong rebuttal (1-2 paragraphs)",
        agent=advocate,
        context=[opening_against],  # Access opponent's argument
    )
    
    # Rebuttal - AGAINST
    rebuttal_against = Task(
        description="""
        Review the advocate's argument and present your rebuttal.
        Challenge their points and strengthen your opposition.
        """,
        expected_output="A strong counter-rebuttal (1-2 paragraphs)",
        agent=opponent,
        context=[opening_for],  # Access advocate's argument
    )
    
    # Judge's verdict
    verdict = Task(
        description=f"""
        You have heard arguments on both sides of: "{topic}"
        
        Review all arguments and rebuttals carefully.
        Evaluate the strength of evidence and reasoning.
        Reach a fair, balanced conclusion.
        
        Explain:
        1. Key points from each side
        2. Which arguments were most convincing
        3. Your final verdict and why
        """,
        expected_output="A detailed, objective verdict (3-4 paragraphs)",
        agent=judge,
        context=[opening_for, opening_against, rebuttal_for, rebuttal_against],
    )
    
    # Create and run crew
    crew = Crew(
        agents=[advocate, opponent, judge],
        tasks=[opening_for, opening_against, rebuttal_for, rebuttal_against, verdict],
        process=Process.sequential,
        verbose=True,
    )
    
    result = crew.kickoff()
    
    print("\n" + "="*70)
    print("⚖️  FINAL VERDICT")
    print("="*70)
    print(result)
    print("="*70 + "\n")
    
    return result

# ==============================================================================
# Main Execution
# ==============================================================================

if __name__ == "__main__":
    # Example debate topics
    topics = [
        "Artificial Intelligence will have a net positive impact on humanity",
        "Remote work is better than office work for productivity",
        "Social media has done more harm than good",
    ]
    
    # Run debate on first topic (you can change this!)
    print("\n🎭 DEBATE PROTOCOL DEMONSTRATION\n")
    print("This demonstrates multi-agent coordination through debate.\n")
    
    # Choose a topic
    topic = topics[0]  # Change index to try different topics
    
    # Or create your own:
    # topic = input("Enter debate topic: ")
    
    result = run_debate(topic)

# ==============================================================================
# Tips for Students
# ==============================================================================
"""
EXPERIMENT WITH:

1. Different topics:
   - Change the topic to test different scenarios
   - Try topics you're passionate about
   
2. Number of rounds:
   - Add more rebuttal rounds
   - Add closing statements
   
3. Multiple judges:
   - Have 3 judges vote
   - Use consensus to reach verdict
   
4. Scoring system:
   - Add a scoring agent
   - Rate arguments on logic, evidence, persuasiveness
   
5. Real-world data:
   - Add web search tools to agents
   - Let them cite real sources

COORDINATION INSIGHTS:

- Tasks can access other tasks via 'context'
- Sequential process ensures proper order
- Each agent has a specialized role
- Judge synthesizes all perspectives
"""

