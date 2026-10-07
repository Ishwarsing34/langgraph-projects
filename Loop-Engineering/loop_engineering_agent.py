"""A small LangGraph agent that improves a draft using evaluator feedback."""

import argparse
from collections.abc import Callable
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

MAX_ATTEMPTS = 3
QUALITY_THRESHOLD = 4
DEFAULT_GOAL = "Explain loop engineering to a beginner in a clear, practical way."


class Evaluation(BaseModel):
    """Structured quality feedback from the evaluator."""

    score: int = Field(ge=1, le=5, description="Overall quality score from 1 to 5.")
    feedback: str = Field(description="Specific feedback for the next improvement.")


class IterationRecord(TypedDict):
    attempt: int
    draft: str
    score: int
    feedback: str


class LoopState(TypedDict):
    goal: str
    draft: str
    feedback: str
    score: int
    attempts: int
    history: list[IterationRecord]
    best_draft: str
    best_score: int


def build_loop_graph(
    create_draft: Callable[[str], str],
    evaluate_draft: Callable[[str, str], Evaluation],
):
    """Build a bounded draft-evaluate-revise graph with injectable model calls."""

    def draft_node(state: LoopState) -> dict[str, object]:
        prompt = (
            f"Create a response that achieves this goal:\n{state['goal']}\n\n"
            "Make the response clear, useful, and complete."
        )
        return {"draft": create_draft(prompt), "attempts": state["attempts"] + 1}

    def evaluate_node(state: LoopState) -> dict[str, object]:
        result = evaluate_draft(state["goal"], state["draft"])
        record: IterationRecord = {
            "attempt": state["attempts"],
            "draft": state["draft"],
            "score": result.score,
            "feedback": result.feedback,
        }
        is_best = result.score >= state["best_score"]
        return {
            "score": result.score,
            "feedback": result.feedback,
            "history": [*state["history"], record],
            "best_draft": state["draft"] if is_best else state["best_draft"],
            "best_score": result.score if is_best else state["best_score"],
        }

    def revise_node(state: LoopState) -> dict[str, object]:
        prompt = (
            f"Goal:\n{state['goal']}\n\n"
            f"Current draft:\n{state['draft']}\n\n"
            f"Evaluator feedback:\n{state['feedback']}\n\n"
            "Revise the draft to address the feedback while still meeting the goal. "
            "Return only the improved draft."
        )
        return {"draft": create_draft(prompt), "attempts": state["attempts"] + 1}

    def choose_next_step(state: LoopState) -> Literal["revise", "__end__"]:
        if state["score"] >= QUALITY_THRESHOLD or state["attempts"] >= MAX_ATTEMPTS:
            return END
        return "revise"

    graph = StateGraph(LoopState)
    graph.add_node("draft", draft_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("revise", revise_node)
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "evaluate")
    graph.add_conditional_edges("evaluate", choose_next_step)
    graph.add_edge("revise", "evaluate")
    return graph.compile()


def run_agent(goal: str) -> LoopState:
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    evaluator = model.with_structured_output(Evaluation)

    def create_draft(prompt: str) -> str:
        response = model.invoke(
            [
                SystemMessage(
                    content="You are a helpful writer. Follow the user's goal exactly."
                ),
                HumanMessage(content=prompt),
            ]
        )
        return str(response.content)

    def evaluate_draft(goal_text: str, draft_text: str) -> Evaluation:
        return evaluator.invoke(
            [
                SystemMessage(
                    content=(
                        "Evaluate the draft against the goal. Score it from 1 to 5: "
                        "1 = misses the goal, 3 = partly successful, "
                        "5 = clear, accurate, and fully meets the goal. "
                        "Give concise, actionable feedback. Be consistent and honest."
                    )
                ),
                HumanMessage(
                    content=f"Goal:\n{goal_text}\n\nDraft to evaluate:\n{draft_text}"
                ),
            ]
        )

    app = build_loop_graph(create_draft, evaluate_draft)
    return app.invoke(
        {
            "goal": goal,
            "draft": "",
            "feedback": "",
            "score": 0,
            "attempts": 0,
            "history": [],
            "best_draft": "",
            "best_score": 0,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate, evaluate, and improve a response with LangGraph."
    )
    parser.add_argument(
        "goal",
        nargs="?",
        default=DEFAULT_GOAL,
        help="What the agent should produce (defaults to a loop-engineering explanation).",
    )
    args = parser.parse_args()

    result = run_agent(args.goal)
    for item in result["history"]:
        print(f"\n--- Attempt {item['attempt']} (score: {item['score']}/5) ---")
        print(item["draft"])
        print(f"Feedback: {item['feedback']}")

    print("\n=== Best result ===")
    print(result["best_draft"])
    if result["best_score"] >= QUALITY_THRESHOLD:
        print(f"\nQuality threshold reached: {result['best_score']}/5")
    else:
        print(
            f"\nStopped after {result['attempts']} attempts. "
            f"Best score: {result['best_score']}/5 "
            f"(target: {QUALITY_THRESHOLD}/5)."
        )


if __name__ == "__main__":
    main()
