# Loop Engineering with LangGraph

Loop engineering is a way to make an agent improve its own work: it creates an
output, evaluates it against the goal, uses feedback to revise it, and repeats
until it meets a quality threshold or reaches a retry limit.

This folder contains a runnable example in
[`loop_engineering_agent.py`](./loop_engineering_agent.py). The agent writes a
response to a goal, asks an LLM evaluator for a structured score and feedback,
and revises the response when the score is below `QUALITY_THRESHOLD`.

## The loop

```text
START -> draft -> evaluate -- good enough or out of attempts? -> END
                         ^                                  |
                         +------------- revise <------------+
```

The LangGraph state carries the goal, current draft, evaluator feedback,
attempt count, iteration history, and best-scoring draft. The graph uses:

- **Goal:** the input prompt.
- **Action:** `draft` creates an initial response; `revise` improves it.
- **Evaluation:** `evaluate` scores the draft from 1 to 5 and explains what to
  improve.
- **Feedback:** `revise` receives the evaluator's feedback and the previous
  draft.
- **Stop condition:** stop at a score of 4 or higher, or after 3 drafts. Keeping
  the limit makes the loop bounded even if the target is never reached.

The example preserves the best-scoring draft, so its final answer is still
useful if the retry limit is reached before the threshold.

## Run it

The repository's root `requirements.txt` already includes the dependencies used
by this example. Set `OPENAI_API_KEY` in the repository-root `.env` file, then
run from the repository root:

```powershell
python .\Loop-Engineering\loop_engineering_agent.py
python .\Loop-Engineering\loop_engineering_agent.py "Explain recursion with a short Python example"
```

The first command uses a beginner-friendly loop-engineering goal. Each attempt
prints the draft, its score, and the feedback that drives the next revision.