# Exercise 4: Code Documentation

## Code Chosen: Task Priority Sorting Algorithm (`task_priority.py`)

---

## 1. Original Code (Undocumented / Minimally Documented)

```python
from datetime import datetime
from models import TaskStatus, TaskPriority

def calculate_task_score(task):
    """Calculate a priority score for a task based on multiple factors."""
    priority_weights = {
        TaskPriority.LOW: 1,
        TaskPriority.MEDIUM: 2,
        TaskPriority.HIGH: 4,
        TaskPriority.URGENT: 6
    }

    score = priority_weights.get(task.priority, 0) * 10

    if task.due_date:
        days_until_due = (task.due_date - datetime.now()).days
        if days_until_due < 0:
            score += 35
        elif days_until_due == 0:
            score += 20
        elif days_until_due <= 2:
            score += 15
        elif days_until_due <= 7:
            score += 10

    if task.status == TaskStatus.DONE:
        score -= 50
    elif task.status == TaskStatus.REVIEW:
        score -= 15

    if any(tag in ["blocker", "critical", "urgent"] for tag in task.tags):
        score += 8

    days_since_update = (datetime.now() - task.updated_at).days
    if days_since_update < 1:
        score += 5

    return score

def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    return sorted_tasks

def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks."""
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]
```

The original code has only minimal one-line docstrings and basic inline comments. There is no parameter documentation, no return type information, no example usage, and no explanation of edge cases.

---

## 2. Prompt 1 Output: Comprehensive Function Documentation (Python Docstrings)

```python
from datetime import datetime
from models import Task, TaskStatus, TaskPriority


def calculate_task_score(task):
    """
    Calculate a weighted importance score for a task based on multiple factors.

    Uses a multi-factor scoring model that considers the task's priority level,
    due date proximity, current status, tags, and recency of updates. The resulting
    score determines the task's position when sorted by importance.

    Scoring breakdown:
        - Base priority:   10-60 points (LOW=10, MEDIUM=20, HIGH=40, URGENT=60)
        - Due date bonus:  0-35 points (overdue=35, today=20, ≤2 days=15, ≤7 days=10)
        - Status penalty:  0 to -50 points (DONE=-50, REVIEW=-15)
        - Tag boost:       0 or 8 points (if tagged "blocker", "critical", or "urgent")
        - Recency boost:   0 or 5 points (if updated within the last day)

    Args:
        task (Task): A Task object with the following required attributes:
            - priority (TaskPriority): The task's priority level (LOW, MEDIUM, HIGH, URGENT)
            - due_date (datetime | None): Optional deadline for the task
            - status (TaskStatus): Current status (TODO, IN_PROGRESS, REVIEW, DONE)
            - tags (list[str]): List of string tags assigned to the task
            - updated_at (datetime): Timestamp of the last update to the task

    Returns:
        int: A numerical importance score. Higher values indicate greater importance.
            Typical range is -40 (completed low-priority task) to 108 (overdue urgent
            blocker updated today). Scores can be negative for completed tasks.

    Example:
        >>> from models import Task, TaskPriority, TaskStatus
        >>> task = Task("Fix critical bug", priority=TaskPriority.URGENT)
        >>> task.tags = ["blocker"]
        >>> score = calculate_task_score(task)
        >>> # Base (60) + tag boost (8) + recency (5) = 73
        >>> score >= 70
        True

    Notes:
        - Priority weights are non-linear: the gap between MEDIUM (2) and HIGH (4)
          is larger than LOW (1) to MEDIUM (2), deliberately emphasizing higher priorities.
        - The -50 penalty for DONE status is large enough to push most completed tasks
          below any active task, regardless of original priority.
        - Multiple matching tags (e.g., both "blocker" and "critical") do NOT stack;
          the bonus is always +8 regardless of how many special tags match.
        - The recency check uses `.days` which returns whole days, so a task updated
          23 hours ago may or may not qualify depending on calendar day boundaries.
        - Tasks with no due_date receive no due date bonus (treated as 0 points).
    """
    # --- Factor 1: Base priority score ---
    # Non-linear weights: HIGH and URGENT are disproportionately more important
    priority_weights = {
        TaskPriority.LOW: 1,       # 1 × 10 = 10 points
        TaskPriority.MEDIUM: 2,    # 2 × 10 = 20 points
        TaskPriority.HIGH: 4,      # 4 × 10 = 40 points
        TaskPriority.URGENT: 6     # 6 × 10 = 60 points
    }
    score = priority_weights.get(task.priority, 0) * 10

    # --- Factor 2: Due date urgency bonus ---
    # Closer deadlines and overdue tasks receive higher bonuses
    if task.due_date:
        days_until_due = (task.due_date - datetime.now()).days
        if days_until_due < 0:        # Overdue: maximum urgency bonus
            score += 35
        elif days_until_due == 0:     # Due today: high urgency
            score += 20
        elif days_until_due <= 2:     # Due within 2 days: moderate urgency
            score += 15
        elif days_until_due <= 7:     # Due within a week: mild urgency
            score += 10
        # Tasks due more than 7 days out receive no bonus

    # --- Factor 3: Status penalty ---
    # Completed tasks are pushed down; review tasks receive a lighter penalty
    if task.status == TaskStatus.DONE:
        score -= 50    # Large penalty ensures done tasks sink to bottom
    elif task.status == TaskStatus.REVIEW:
        score -= 15    # Lighter penalty: still relevant but less actionable

    # --- Factor 4: Critical tag boost ---
    # Checks if ANY tag matches the high-urgency keywords (does not stack)
    if any(tag in ["blocker", "critical", "urgent"] for tag in task.tags):
        score += 8

    # --- Factor 5: Recency boost ---
    # Tasks touched today get a small tiebreaker bonus
    days_since_update = (datetime.now() - task.updated_at).days
    if days_since_update < 1:
        score += 5

    return score


def sort_tasks_by_importance(tasks):
    """
    Sort a list of tasks by their calculated importance score in descending order.

    Calculates a score for each task using calculate_task_score(), then returns
    the tasks ordered from highest score (most important) to lowest.

    Args:
        tasks (list[Task]): A list of Task objects to sort. Can be empty.

    Returns:
        list[Task]: A new list of Task objects sorted by importance score
            (highest first). The original list is not modified.

    Example:
        >>> tasks = [low_priority_task, urgent_task, medium_task]
        >>> sorted_tasks = sort_tasks_by_importance(tasks)
        >>> sorted_tasks[0].priority == TaskPriority.URGENT
        True

    Notes:
        - Each task's score is calculated once (not recalculated during sorting),
          making this efficient for large lists.
        - Tasks with identical scores maintain their original relative order
          (this is a stable sort, which is Python's default behavior).
        - Returns an empty list if the input list is empty.
    """
    # Pair each task with its pre-calculated score as a tuple: (score, task)
    task_scores = [(calculate_task_score(task), task) for task in tasks]

    # Sort by score (first element of tuple) in descending order,
    # then extract just the task objects from the sorted pairs
    sorted_tasks = [
        task for _, task
        in sorted(task_scores, key=lambda x: x[0], reverse=True)
    ]

    return sorted_tasks


def get_top_priority_tasks(tasks, limit=5):
    """
    Return the top N most important tasks from the given list.

    Sorts all tasks by importance score and returns only the first `limit` tasks.
    Useful for displaying a focused "what to do next" list.

    Args:
        tasks (list[Task]): A list of Task objects to evaluate. Can be empty.
        limit (int, optional): Maximum number of tasks to return. Defaults to 5.
            If limit exceeds the number of tasks, all tasks are returned.

    Returns:
        list[Task]: A list of up to `limit` Task objects, sorted by importance
            score (highest first).

    Example:
        >>> all_tasks = get_all_tasks()  # Returns 50 tasks
        >>> top_tasks = get_top_priority_tasks(all_tasks, limit=3)
        >>> len(top_tasks) <= 3
        True

    Notes:
        - This sorts the entire list before slicing, so performance is O(n log n)
          regardless of the limit value. For very large task lists with small limits,
          a heap-based approach would be more efficient.
        - A limit of 0 returns an empty list.
        - Negative limit values will return an empty list (Python slice behavior).
    """
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]
```

---

## 3. Prompt 2 Output: Intent and Logic Explanation

### High-Level Intent

This module solves a common productivity problem: **"What should I work on next?"**

Rather than simply sorting by priority level (which ignores deadlines, completion status, and context), it uses a **weighted multi-factor scoring model** that considers five different aspects of each task. The result is a single number that represents how much attention each task deserves right now. Tasks are then sorted by this score, producing an actionable, prioritized list.

### Step-by-Step Logic Breakdown

#### `calculate_task_score(task)`

1. **Establish base importance from priority** — The function starts by mapping each priority level to a non-linear weight (1, 2, 4, 6) and multiplying by 10. The non-linearity is intentional: the jump from MEDIUM to HIGH (20 → 40) is larger than LOW to MEDIUM (10 → 20). This ensures that HIGH and URGENT tasks are treated as significantly more important, not just marginally so.

2. **Apply deadline urgency** — If the task has a due date, it calculates how many days remain. Overdue tasks get the largest bonus (+35), reflecting the principle that past-due work needs immediate attention. The bonuses decrease as the deadline moves further away. Tasks with no due date get no bonus — they compete purely on other factors.

3. **Penalize completed or in-review tasks** — Done tasks receive a -50 penalty, which is large enough to push even an URGENT task (base 60) down to 10 — below most active tasks. Review tasks get a lighter -15 penalty, acknowledging they're less actionable but still relevant.

4. **Boost for critical tags** — The `any()` function checks if any of the task's tags match high-urgency keywords. This is a binary check: you either get +8 or you don't. Multiple matching tags don't stack.

5. **Reward recency** — Tasks updated within the last day get a small +5 boost. This is the weakest factor, serving as a subtle tiebreaker that keeps actively-worked tasks slightly more visible.

6. **Return the total** — All factors are added together into a single integer score.

#### `sort_tasks_by_importance(tasks)`

1. **Pre-calculate scores** — Creates a list of (score, task) tuples. Calculating scores once up front avoids redundant computation during sorting.

2. **Sort and extract** — Python's `sorted()` function sorts the tuples by score (via the `key=lambda` parameter) in descending order. The list comprehension then strips out the scores, returning just the task objects.

#### `get_top_priority_tasks(tasks, limit=5)`

1. **Sort everything** — Calls `sort_tasks_by_importance()` to get the full sorted list.

2. **Slice to limit** — Uses Python's slice notation `[:limit]` to return only the top N tasks.

### Assumptions in the Implementation

- **Tasks always have `priority`, `status`, `tags`, and `updated_at` attributes** — The code does not validate that these exist. A Task object missing any of these would cause an AttributeError.
- **`due_date` can be None** — This is explicitly handled with the `if task.due_date` check.
- **Tags are plain strings** — Matching is case-sensitive. A tag of "Blocker" would NOT match "blocker".
- **`datetime.now()` is called multiple times** — If the function runs near midnight, the due date calculation and recency calculation could use slightly different "now" values. In practice this is negligible.

### Edge Cases

1. **Task with no due date, no special tags, default status (TODO), and not recently updated** — Score is purely the base priority score (10, 20, 40, or 60).

2. **Completed URGENT task vs. active LOW task** — URGENT DONE = 60 - 50 = 10. LOW TODO with no modifiers = 10. They tie! If the LOW task was updated today, it would score 15 and actually rank higher.

3. **Empty task list** — Both `sort_tasks_by_importance([])` and `get_top_priority_tasks([])` return `[]` without errors.

4. **Limit greater than list length** — `get_top_priority_tasks(tasks, limit=100)` when there are only 5 tasks returns all 5. Python's slice handles this gracefully.

### Suggested Improvements

1. **Cache `datetime.now()` at the start of `calculate_task_score`** — Calling `datetime.now()` once and reusing it ensures consistent calculations within a single scoring pass:
   ```python
   now = datetime.now()
   days_until_due = (task.due_date - now).days
   days_since_update = (now - task.updated_at).days
   ```

2. **Make tag matching case-insensitive** — Convert tags to lowercase before comparison:
   ```python
   if any(tag.lower() in ["blocker", "critical", "urgent"] for tag in task.tags):
   ```

3. **Make weights configurable** — Extract the priority weights and bonus values into a configuration dictionary or class, allowing users to customize the scoring formula without modifying code.

4. **Use a more efficient selection for `get_top_priority_tasks`** — For large task lists with small limits, Python's `heapq.nlargest()` would be O(n log k) instead of O(n log n):
   ```python
   import heapq
   top = heapq.nlargest(limit, tasks, key=calculate_task_score)
   ```

5. **Add graduated overdue severity** — Currently a task 1 day overdue and 30 days overdue both get +35. A sliding scale would be more nuanced:
   ```python
   if days_until_due < 0:
       score += min(35 + abs(days_until_due), 50)  # Cap at 50
   ```

---

## 4. Final Combined Documentation Version

Below is the final version that combines the comprehensive docstrings from Prompt 1 with the inline commentary and improvement suggestions from Prompt 2.

```python
"""
Task Priority Scoring Module
=============================

Provides a weighted multi-factor scoring system for ranking tasks by importance.
Rather than sorting tasks by a single attribute (like priority level), this module
considers five factors: priority weight, due date proximity, task status, critical
tags, and update recency.

The scoring formula is:
    score = (priority_weight × 10)
          + due_date_bonus      (0 to +35)
          - status_penalty      (0 to -50)
          + tag_boost           (0 or +8)
          + recency_boost       (0 or +5)

Typical score range: -40 (completed LOW task) to 108 (overdue URGENT blocker,
updated today).

Functions:
    calculate_task_score(task) -> int
    sort_tasks_by_importance(tasks) -> list[Task]
    get_top_priority_tasks(tasks, limit=5) -> list[Task]

Potential improvements:
    - Make weights configurable via a settings dictionary
    - Add case-insensitive tag matching
    - Use heapq.nlargest() for more efficient top-N retrieval
    - Add graduated overdue severity scaling
"""

from datetime import datetime
from models import Task, TaskStatus, TaskPriority


def calculate_task_score(task):
    """
    Calculate a weighted importance score for a task based on multiple factors.

    Args:
        task (Task): A Task object with attributes: priority (TaskPriority),
            due_date (datetime | None), status (TaskStatus), tags (list[str]),
            and updated_at (datetime).

    Returns:
        int: Importance score. Higher = more important. Can be negative for
            completed tasks. Typical range: -40 to 108.

    Example:
        >>> task = Task("Fix bug", priority=TaskPriority.URGENT)
        >>> task.tags = ["blocker"]
        >>> calculate_task_score(task)  # Base(60) + tag(8) + recency(5) = 73

    Notes:
        - Priority weights are non-linear (1, 2, 4, 6) to emphasize HIGH/URGENT.
        - Multiple matching critical tags do NOT stack (always +8 or +0).
        - Tag matching is case-sensitive ("Blocker" ≠ "blocker").
        - DONE penalty (-50) is large enough to push most completed tasks below
          any active task.
    """
    # Capture current time once for consistency across all calculations
    now = datetime.now()

    # --- Factor 1: Base priority score (10-60 points) ---
    # Non-linear weights deliberately widen the gap for HIGH and URGENT
    priority_weights = {
        TaskPriority.LOW: 1,       # → 10 points
        TaskPriority.MEDIUM: 2,    # → 20 points
        TaskPriority.HIGH: 4,      # → 40 points
        TaskPriority.URGENT: 6     # → 60 points
    }
    score = priority_weights.get(task.priority, 0) * 10

    # --- Factor 2: Due date urgency bonus (0-35 points) ---
    # The closer the deadline (or further overdue), the larger the bonus
    if task.due_date:
        days_until_due = (task.due_date - now).days
        if days_until_due < 0:        # Overdue → maximum urgency
            score += 35
        elif days_until_due == 0:     # Due today
            score += 20
        elif days_until_due <= 2:     # Due within 2 days
            score += 15
        elif days_until_due <= 7:     # Due within a week
            score += 10
        # No bonus for tasks due more than 7 days out

    # --- Factor 3: Status penalty (0 to -50 points) ---
    # Pushes completed/review tasks below active ones in sort order
    if task.status == TaskStatus.DONE:
        score -= 50    # Heavy penalty ensures done tasks sink to bottom
    elif task.status == TaskStatus.REVIEW:
        score -= 15    # Lighter penalty: less actionable but still relevant

    # --- Factor 4: Critical tag boost (0 or +8 points) ---
    # Binary check: any() returns True on first match and stops
    if any(tag in ["blocker", "critical", "urgent"] for tag in task.tags):
        score += 8

    # --- Factor 5: Recency boost (0 or +5 points) ---
    # Subtle tiebreaker for tasks actively being worked on
    days_since_update = (now - task.updated_at).days
    if days_since_update < 1:
        score += 5

    return score


def sort_tasks_by_importance(tasks):
    """
    Sort tasks by calculated importance score, highest first.

    Pre-calculates all scores once for efficiency, then sorts using Python's
    stable TimSort algorithm. Tasks with identical scores maintain their
    original relative order.

    Args:
        tasks (list[Task]): List of Task objects. Can be empty.

    Returns:
        list[Task]: New sorted list (original is not modified).

    Example:
        >>> sorted_tasks = sort_tasks_by_importance(all_tasks)
        >>> sorted_tasks[0]  # Most important task
    """
    # Pre-calculate scores to avoid redundant computation during sort
    task_scores = [(calculate_task_score(task), task) for task in tasks]

    # Sort by score (descending) and extract just the task objects
    sorted_tasks = [
        task for _, task
        in sorted(task_scores, key=lambda x: x[0], reverse=True)
    ]

    return sorted_tasks


def get_top_priority_tasks(tasks, limit=5):
    """
    Return the top N most important tasks.

    Sorts all tasks by importance score and returns the first `limit` items.
    If fewer tasks exist than the limit, all tasks are returned.

    Args:
        tasks (list[Task]): List of Task objects. Can be empty.
        limit (int, optional): Maximum number of tasks to return. Defaults to 5.

    Returns:
        list[Task]: Up to `limit` tasks, sorted by importance (highest first).

    Example:
        >>> top_3 = get_top_priority_tasks(all_tasks, limit=3)
        >>> len(top_3) <= 3
        True

    Notes:
        - Sorts the entire list before slicing: O(n log n) performance.
        - For large lists with small limits, consider heapq.nlargest() for O(n log k).
    """
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]
```

---

## 5. Reflection

### Which parts of the documentation were most challenging for the AI?

The **edge case documentation** required the most refinement. The initial AI output listed generic edge cases, but missed specific non-obvious behaviors like the fact that a completed URGENT task (score 10) ties with a plain LOW task (score 10), or that multiple matching tags don't stack. I had to prompt specifically for "non-obvious behaviors" and "scenarios where the algorithm produces counterintuitive results" to get these important details.

### What additional information did I need to provide in prompts?

Providing the **models.py file alongside task_priority.py** was essential. Without seeing the Task class definition and its attributes, the AI couldn't accurately document parameter types or identify which attributes might be None. Including the related code (not just the target function) produced significantly better documentation.

### How I would use this approach in my own projects

I would use **Prompt 1 first** when writing new functions to generate the docstring structure, then fill in the details myself. I would use **Prompt 2 after completing a feature** to get a fresh perspective on the logic — it often catches assumptions and edge cases that I overlooked while writing the code. The final combined version takes the formal structure from Prompt 1 and the practical insights from Prompt 2 to create documentation that's both technically complete and genuinely useful for other developers.

### Key difference between Prompt 1 and Prompt 2

**Prompt 1** produces formal, structured documentation that follows conventions (types, parameters, return values). It's what other developers see in their IDE when they hover over a function. **Prompt 2** produces understanding-oriented documentation — it explains *why* the code works this way, not just *what* it does. Both are valuable, but for different audiences: Prompt 1 helps someone *use* the function correctly, while Prompt 2 helps someone *maintain or modify* it.
