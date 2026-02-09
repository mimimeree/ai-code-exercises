# Exercise 3: Algorithm Deconstruction Challenge

## Algorithm Chosen: Task Priority Sorting Algorithm (`task_priority.py`)

---

## 1. Algorithm Overview

The Task Priority Sorting algorithm assigns a numerical **importance score** to each task based on multiple weighted factors, then sorts all tasks from highest score to lowest. This allows the application to answer the question: "What should I work on next?"

The algorithm lives in `task_priority.py` and consists of three functions:
- `calculate_task_score(task)` — Calculates a score for a single task
- `sort_tasks_by_importance(tasks)` — Sorts a list of tasks by their scores
- `get_top_priority_tasks(tasks, limit)` — Returns only the top N most important tasks

---

## 2. Step-by-Step Algorithm Breakdown

### Section 1: Base Priority Score (Lines 8-16)

```python
priority_weights = {
    TaskPriority.LOW: 1,
    TaskPriority.MEDIUM: 2,
    TaskPriority.HIGH: 4,
    TaskPriority.URGENT: 6
}
score = priority_weights.get(task.priority, 0) * 10
```

**What it does:** Creates a starting score based on the task's priority level.

**Key insight:** The weights are **non-linear** — the gap between MEDIUM (2) and HIGH (4) is larger than LOW (1) to MEDIUM (2). This means the algorithm deliberately makes HIGH and URGENT tasks feel disproportionately more important. After multiplying by 10:

| Priority | Weight | Base Score |
|----------|--------|------------|
| LOW      | 1      | 10         |
| MEDIUM   | 2      | 20         |
| HIGH     | 4      | 40         |
| URGENT   | 6      | 60         |

**Python concept — `.get()` with default:** `priority_weights.get(task.priority, 0)` looks up the priority in the dictionary. If the priority somehow doesn't exist, it returns `0` instead of crashing. This is **defensive programming**.

### Section 2: Due Date Factor (Lines 19-28)

```python
if task.due_date:
    days_until_due = (task.due_date - datetime.now()).days
    if days_until_due < 0:       # Overdue tasks → +35
        score += 35
    elif days_until_due == 0:    # Due today → +20
        score += 20
    elif days_until_due <= 2:    # Due in next 2 days → +15
        score += 15
    elif days_until_due <= 7:    # Due in next week → +10
        score += 10
```

**What it does:** Adds bonus points based on how close the deadline is. The closer (or more overdue) a task is, the bigger the bonus.

**Key insight:** Overdue tasks get the **highest** bonus (+35) — even more than tasks due today (+20). This ensures overdue tasks rise to the top immediately. Tasks with no due date or due dates more than a week away get no bonus at all.

**Python concept — datetime subtraction:** `(task.due_date - datetime.now()).days` subtracts two dates and gets the number of days between them. Negative numbers mean the date has passed (overdue).

### Section 3: Status Penalties (Lines 31-34)

```python
if task.status == TaskStatus.DONE:
    score -= 50
elif task.status == TaskStatus.REVIEW:
    score -= 15
```

**What it does:** Reduces the score for tasks that are completed or in review.

**Key insight:** The -50 for DONE tasks is deliberately large enough to push almost any completed task below active tasks. Even an URGENT task (base 60) that's done would score only 10. The -15 for REVIEW tasks is a lighter penalty — they're still important but less actionable than TODO or IN_PROGRESS tasks.

### Section 4: Tag Boost (Lines 37-38)

```python
if any(tag in ["blocker", "critical", "urgent"] for tag in task.tags):
    score += 8
```

**What it does:** Gives a +8 bonus if the task has any high-urgency tags.

**Python concept — `any()` with generator expression:** This reads as: "Is ANY tag in the task's tag list found in the list ['blocker', 'critical', 'urgent']?" It loops through all tags and returns `True` as soon as it finds a match. This is more efficient than checking every tag — it stops as soon as it finds one.

**Key insight:** The +8 bonus is relatively small compared to priority weights. A LOW priority task with a "blocker" tag (10 + 8 = 18) still scores less than a plain MEDIUM task (20). Tags provide a tiebreaker, not a major shift.

### Section 5: Recency Boost (Lines 41-43)

```python
days_since_update = (datetime.now() - task.updated_at).days
if days_since_update < 1:
    score += 5
```

**What it does:** Gives a small +5 bonus to tasks that were updated today.

**Key insight:** This is the smallest factor (+5), acting as a subtle tiebreaker. It keeps recently-touched tasks slightly more visible, reflecting the idea that tasks you're actively working on deserve a bit more attention.

### Section 6: Sorting (Lines 47-52)

```python
def sort_tasks_by_importance(tasks):
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    return sorted_tasks
```

**What it does:** Calculates scores for all tasks, pairs each score with its task, sorts by score (highest first), then extracts just the tasks.

**Python concept — tuples:** `(calculate_task_score(task), task)` creates a **tuple** — a pair of values grouped together. Here it pairs each task with its score.

**Python concept — `_` underscore variable:** In `for _, task in sorted(...)`, the `_` means "I don't need this value." It's the score, which we only needed for sorting. We just want the task objects back.

**Python concept — `lambda`:** `key=lambda x: x[0]` is a tiny anonymous function that tells `sorted()` to compare items by their first element (the score). Think of it as telling Python: "When comparing, only look at element [0] of each tuple."

**Python concept — `reverse=True`:** By default, `sorted()` goes low to high. `reverse=True` flips it so the highest scores come first.

---

## 3. Concrete Example Walkthrough

### Scenario: Scoring Four Tasks

| Task | Priority | Due Date | Status | Tags | Updated |
|------|----------|----------|--------|------|---------|
| Task A | URGENT | Yesterday | TODO | ["blocker"] | Today |
| Task B | HIGH | Tomorrow | IN_PROGRESS | ["work"] | Today |
| Task C | MEDIUM | Next month | DONE | ["project"] | 3 days ago |
| Task D | LOW | Today | TODO | ["critical"] | Today |

**Task A Score Calculation:**
- Base: URGENT (6) × 10 = 60
- Due date: overdue → +35
- Status: TODO → +0
- Tags: "blocker" matches → +8
- Recency: updated today → +5
- **Total: 108**

**Task B Score Calculation:**
- Base: HIGH (4) × 10 = 40
- Due date: 1 day away (≤ 2) → +15
- Status: IN_PROGRESS → +0
- Tags: "work" doesn't match → +0
- Recency: updated today → +5
- **Total: 60**

**Task C Score Calculation:**
- Base: MEDIUM (2) × 10 = 20
- Due date: > 7 days away → +0
- Status: DONE → -50
- Tags: "project" doesn't match → +0
- Recency: 3 days ago → +0
- **Total: -30**

**Task D Score Calculation:**
- Base: LOW (1) × 10 = 10
- Due date: due today → +20
- Status: TODO → +0
- Tags: "critical" matches → +8
- Recency: updated today → +5
- **Total: 43**

**Final sorted order:** Task A (108) → Task B (60) → Task D (43) → Task C (-30)

**Insight from example:** Task D (LOW priority) ranked above Task C (MEDIUM priority) because Task C was DONE (-50 penalty was devastating) while Task D had a due-today bonus and a tag boost. This shows that the algorithm considers **multiple factors** — raw priority alone doesn't determine importance.

---

## 4. Core Technique: Weighted Multi-Factor Scoring

The algorithm uses a **weighted scoring model** — a common pattern in software for making decisions based on multiple criteria. Each factor contributes a different number of points:

```
Final Score = (Priority × 10) + Due Date Bonus - Status Penalty + Tag Boost + Recency Boost
```

The weights determine which factors matter most:

| Factor | Max Contribution | Relative Importance |
|--------|-----------------|-------------------|
| Priority | 60 points (URGENT) | Dominant factor |
| Due Date | 35 points (overdue) | Strong secondary factor |
| Status (penalty) | -50 points (DONE) | Can override everything |
| Tags | 8 points | Minor boost / tiebreaker |
| Recency | 5 points | Subtle tiebreaker |

This means priority and due dates drive most decisions, while tags and recency serve as tiebreakers between otherwise similar tasks.

---

## 5. Edge Cases and Non-Obvious Behaviors

1. **A DONE URGENT task scores lower than an active LOW task:** URGENT DONE = 60 - 50 = 10, while LOW TODO due today = 10 + 20 = 30. The completion penalty is intentionally strong enough to push done tasks below active ones.

2. **Tasks with no due date lose out:** A MEDIUM task with no due date scores 20, while a LOW task due today scores 30. This means setting due dates significantly influences task ordering.

3. **Multiple matching tags don't stack:** If a task has both "blocker" and "critical" tags, it still only gets +8, not +16. The `any()` function returns True/False — it doesn't count matches.

4. **The recency window is narrow:** Only tasks updated within the same calendar day get the +5 bonus (because `.days` returns whole days). A task updated 23 hours ago might or might not qualify depending on timing.

---

## 6. Reflection Questions

### How did the AI's explanation change my understanding?

Before the analysis, I assumed the algorithm would simply sort by priority level. The AI-assisted breakdown revealed it's actually a **multi-factor scoring system** where due dates can be more impactful than raw priority. The non-linear priority weights (1, 2, 4, 6 instead of 1, 2, 3, 4) were a subtle but important design choice I would have missed.

### What was still difficult after AI explanation?

The `lambda` function and tuple unpacking in the sorting function were the most abstract concepts. The syntax `key=lambda x: x[0]` and `for _, task in sorted(...)` required multiple re-reads to understand. These are Python-specific idioms that become natural with practice but are initially cryptic.

### How would I explain this to another junior developer?

"Imagine you're a teacher grading essays. You don't just look at one thing — you consider writing quality, originality, whether it was turned in on time, and length. Each factor gets different importance. This algorithm does the same thing for tasks: it looks at priority, deadline, status, tags, and how recently you touched it. Each factor adds or subtracts points, and the final number tells you what to work on first."

### How might I improve the algorithm?

1. **Add configurable weights:** Currently the weights are hardcoded. Allowing users to adjust them (e.g., "I care more about deadlines than priority") would make the system more flexible.
2. **Make the tag boost stackable:** Having both "blocker" and "critical" could give +16 instead of just +8.
3. **Add a dependency factor:** If Task B depends on Task A being done first, Task A should get a boost.
4. **Graduated overdue penalty:** A task 1 day overdue gets the same +35 as one 30 days overdue. A sliding scale based on how overdue it is would be more nuanced.
5. **Fix the recency edge case:** Use hours instead of whole days for more precise recency calculation.
