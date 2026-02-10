# Exercise 10: Using AI to Help with Testing

## Code Under Test: Python Task Priority Scoring Algorithm (`task_priority.py`)

---

## Part 1: Understanding What to Test

### Exercise 1.1: Behavior Analysis

#### Conversation with AI — What does `calculateTaskScore` do?

**AI asked:** What do you think this function does? Describe it in your own words before we analyze it.

**My answer:** It takes a task and calculates a number that represents how important the task is right now. It looks at the task's priority level, when it's due, whether it's done or not, if it has any special tags, and how recently it was updated. Higher number = more important task.

**AI feedback:** That's accurate. You've identified all five scoring factors. One thing to add: the function returns an integer score, and the score *can be negative* — this happens when a completed task's -50 penalty pushes the total below zero.

**AI asked:** What edge cases do you think should be tested?

**My answer:** I'd test:
- A task with no due date
- A task that's overdue
- A completed task
- A task with multiple special tags (do they stack?)
- An empty tags list

**AI feedback:** Good list. Here are additional edge cases you might have missed:
- A task due *exactly* today (boundary between "due today" and "due tomorrow")
- A task due exactly 2 days from now (boundary of the ≤2 day check)
- A task due exactly 7 days from now (boundary of the ≤7 day check)
- A task updated exactly 24 hours ago (boundary of the recency check)
- A task with a tag that's similar but not matching, like "Critical" (capitalized) vs "critical" (lowercase)
- What happens if `task.priority` is somehow not in the priority_weights dictionary?

#### Test Cases Identified (minimum 5)

| # | Test Case | What It Verifies | Priority |
|---|-----------|-----------------|----------|
| 1 | Each priority level produces the correct base score | Core functionality — the foundation everything else builds on | HIGH |
| 2 | Overdue task gets +35 bonus | Due date factor for past-due tasks | HIGH |
| 3 | Task due today gets +20 bonus | Due date boundary — exactly 0 days | HIGH |
| 4 | DONE status applies -50 penalty | Status penalty is large enough to push tasks down | HIGH |
| 5 | Task with "blocker" tag gets +8 boost | Tag matching works | MEDIUM |
| 6 | Multiple special tags don't stack (still +8, not +16) | Non-obvious behavior of `any()` | MEDIUM |
| 7 | Task with no due date gets no bonus | Null/None handling | MEDIUM |
| 8 | Case-sensitive tag matching ("Critical" ≠ "critical") | Potential gotcha | MEDIUM |
| 9 | Task updated today gets +5 recency boost | Recency factor | LOW |
| 10 | All factors combine correctly for a complex task | Integration of all factors | HIGH |

### Exercise 1.2: Test Planning

#### Testing Plan for All Three Functions

**Function 1: `calculate_task_score(task)`**

This is the core function — everything depends on it being correct. Testing strategy: test each scoring factor in isolation, then test combinations.

| Category | Tests Needed | Type |
|----------|-------------|------|
| Base priority scores | 4 tests (one per priority level) | Unit |
| Due date bonuses | 6 tests (overdue, today, ≤2 days, ≤7 days, >7 days, no due date) | Unit |
| Status penalties | 4 tests (TODO, IN_PROGRESS, REVIEW, DONE) | Unit |
| Tag boosts | 4 tests (no tags, normal tags, one special tag, multiple special tags) | Unit |
| Recency boost | 2 tests (updated today, updated days ago) | Unit |
| Combination | 2 tests (best case score, worst case score) | Unit |
| Edge cases | 3 tests (boundary dates, case sensitivity, unknown priority) | Unit |

**Function 2: `sort_tasks_by_importance(tasks)`**

Depends on `calculate_task_score` being correct. Testing strategy: use tasks with clearly different scores so the expected order is unambiguous.

| Category | Tests Needed | Type |
|----------|-------------|------|
| Basic sorting | 1 test — tasks with different priorities sort correctly | Unit |
| Stable ordering | 1 test — tasks with equal scores maintain original order | Unit |
| Empty list | 1 test — returns empty list without error | Unit |
| Single item | 1 test — returns the same item | Unit |
| Mixed factors | 1 test — tasks with competing factors (high priority but done vs low priority but overdue) | Integration |

**Function 3: `get_top_priority_tasks(tasks, limit)`**

Depends on `sort_tasks_by_importance`. Testing strategy: verify it returns the correct number of correctly-ordered tasks.

| Category | Tests Needed | Type |
|----------|-------------|------|
| Basic top-N | 1 test — returns correct number of tasks | Unit |
| Limit > list length | 1 test — returns all tasks when limit is bigger | Unit |
| Default limit | 1 test — default of 5 works | Unit |
| Empty list | 1 test — returns empty list | Unit |
| Limit of 0 | 1 test — returns empty list | Edge case |

**Test Dependencies:**
- `sort_tasks_by_importance` tests depend on `calculate_task_score` working correctly
- `get_top_priority_tasks` tests depend on `sort_tasks_by_importance` working correctly
- Therefore: test `calculate_task_score` first, then `sort_tasks_by_importance`, then `get_top_priority_tasks`

---

## Part 2: Improving a Single Test

### Exercise 2.1: Writing and Improving a First Test

#### My Initial Simple Test

```python
import unittest
from models import Task, TaskPriority

class TestCalculateTaskScore(unittest.TestCase):
    def test_basic_priority(self):
        task = Task("Test task", priority=TaskPriority.HIGH)
        score = calculate_task_score(task)
        self.assertTrue(score > 0)
```

#### AI's Questions About My Test

**AI asked:** What specifically is your test trying to verify?

**My answer:** That a HIGH priority task gets a positive score.

**AI feedback:** Your test checks that the score is positive, but it doesn't check that it's the *correct* positive number. A LOW priority task would also pass this test (score = 10 + 5 = 15, which is > 0). Your test can't distinguish between a correctly working function and one that returns the wrong score. This is called a **weak assertion** — it's too easy to pass.

**AI asked:** Is your test checking behavior or implementation details?

**My answer:** Behavior, I think — I'm checking that the output is positive.

**AI feedback:** You're on the right track thinking about behavior, but "is positive" isn't the behavior we care about. The behavior is: "a HIGH priority task with no other factors gets a base score of 40, plus a recency boost of 5 if just created = 45." A stronger assertion would verify the actual expected value.

**AI asked:** How would you make the assertion more precise?

**My answer:** Check for the exact expected score instead of just checking it's positive.

#### My Improved Test

```python
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from models import Task, TaskPriority, TaskStatus
from task_priority import calculate_task_score


class TestCalculateTaskScore(unittest.TestCase):

    @patch('task_priority.datetime')
    def test_high_priority_base_score(self, mock_datetime):
        """A HIGH priority task with no due date, default status, no special
        tags, and updated today should score: base(40) + recency(5) = 45."""
        now = datetime(2026, 2, 10, 12, 0, 0)
        mock_datetime.now.return_value = now

        task = Task("Fix login page", priority=TaskPriority.HIGH)
        task.updated_at = now  # Updated "today" for consistent recency

        score = calculate_task_score(task)

        self.assertEqual(score, 45)  # 40 base + 5 recency
```

#### What Changed and Why

| Aspect | Before | After | Why It's Better |
|--------|--------|-------|-----------------|
| Assertion | `assertTrue(score > 0)` | `assertEqual(score, 45)` | Verifies the exact expected value, not just positivity |
| Time control | None (uses real `datetime.now()`) | Mocked `datetime.now()` | Makes the test **deterministic** — it produces the same result every time, regardless of when you run it |
| Test name | `test_basic_priority` | `test_high_priority_base_score` | Describes exactly what's being tested |
| Docstring | None | Full explanation of expected calculation | Another developer can understand the test without reading the function |

**Python concept — mocking:** `@patch('task_priority.datetime')` replaces the real `datetime` with a fake one inside the function being tested. This means `datetime.now()` always returns the same value we control, making the test predictable. Without mocking, the recency boost might or might not apply depending on *when* you run the test.

### Exercise 2.2: Testing Due Date Calculations

#### My Rough Test Idea (Pseudocode)

```
Create a task that's overdue by 1 day
Calculate its score
Check that the score includes the +35 overdue bonus
```

#### AI's Principles for Testing Due Dates

A good test for time-dependent code should:
1. **Control the current time** — Mock `datetime.now()` so the test doesn't depend on when it runs
2. **Set due dates relative to the mocked "now"** — This makes the intent clear
3. **Test boundary conditions** — What happens at exactly 0 days? Exactly 2 days? Exactly 7 days?
4. **Verify the exact bonus amount** — Not just "bigger" or "smaller"

#### AI's Example Test (with explanations)

```python
@patch('task_priority.datetime')
def test_overdue_task_gets_maximum_due_date_bonus(self, mock_datetime):
    """An overdue task should receive a +35 due date bonus on top of its
    base priority score. This is the largest due date bonus, reflecting
    that overdue tasks need the most urgent attention."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Overdue report", priority=TaskPriority.MEDIUM)
    task.due_date = now - timedelta(days=1)  # Due yesterday
    task.updated_at = now  # Updated today (controls recency factor)

    score = calculate_task_score(task)

    # Expected: base(20) + overdue(35) + recency(5) = 60
    self.assertEqual(score, 60)
```

**Why this is better than my pseudocode:**
- It controls the current time (mocking)
- It sets `updated_at` explicitly so the recency factor is predictable
- The comment shows the full calculation breakdown
- The test name describes the *behavior* being tested, not the *input*

#### My Comprehensive Due Date Tests

```python
@patch('task_priority.datetime')
def test_due_date_overdue_gets_35_bonus(self, mock_datetime):
    """Overdue tasks get the maximum due date bonus of +35."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Overdue", priority=TaskPriority.MEDIUM)
    task.due_date = now - timedelta(days=3)
    task.updated_at = now

    self.assertEqual(calculate_task_score(task), 60)  # 20 + 35 + 5

@patch('task_priority.datetime')
def test_due_date_today_gets_20_bonus(self, mock_datetime):
    """Tasks due today get +20 bonus."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Due today", priority=TaskPriority.MEDIUM)
    task.due_date = now  # Due right now → 0 days
    task.updated_at = now

    self.assertEqual(calculate_task_score(task), 45)  # 20 + 20 + 5

@patch('task_priority.datetime')
def test_due_date_within_2_days_gets_15_bonus(self, mock_datetime):
    """Tasks due within 2 days get +15 bonus."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Due soon", priority=TaskPriority.MEDIUM)
    task.due_date = now + timedelta(days=2)
    task.updated_at = now

    self.assertEqual(calculate_task_score(task), 40)  # 20 + 15 + 5

@patch('task_priority.datetime')
def test_due_date_within_7_days_gets_10_bonus(self, mock_datetime):
    """Tasks due within a week get +10 bonus."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Due this week", priority=TaskPriority.MEDIUM)
    task.due_date = now + timedelta(days=5)
    task.updated_at = now

    self.assertEqual(calculate_task_score(task), 35)  # 20 + 10 + 5

@patch('task_priority.datetime')
def test_due_date_beyond_7_days_gets_no_bonus(self, mock_datetime):
    """Tasks due more than 7 days away get no due date bonus."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Due far away", priority=TaskPriority.MEDIUM)
    task.due_date = now + timedelta(days=30)
    task.updated_at = now

    self.assertEqual(calculate_task_score(task), 25)  # 20 + 0 + 5

@patch('task_priority.datetime')
def test_no_due_date_gets_no_bonus(self, mock_datetime):
    """Tasks with no due date get no due date bonus."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("No deadline", priority=TaskPriority.MEDIUM)
    task.due_date = None
    task.updated_at = now

    self.assertEqual(calculate_task_score(task), 25)  # 20 + 0 + 5
```

---

## Part 3: Test-Driven Development Practice

### Exercise 3.1: TDD for a New Feature

**Feature:** Tasks assigned to the current user should get a score boost of +12.

#### Step 1: Write a Failing Test (RED)

**AI asked:** What do you think the first test should be and why?

**My answer:** Test that a task assigned to the current user gets +12. This is the core behavior of the feature.

**AI feedback:** Good choice — start with the simplest, most direct test of the new behavior.

```python
@patch('task_priority.datetime')
def test_task_assigned_to_current_user_gets_12_boost(self, mock_datetime):
    """Tasks assigned to the current user should get a +12 score boost."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("My task", priority=TaskPriority.MEDIUM)
    task.assigned_to = "whitney"  # New attribute
    task.updated_at = now

    score = calculate_task_score(task, current_user="whitney")

    # Expected: base(20) + assigned_to_me(12) + recency(5) = 37
    self.assertEqual(score, 37)
```

**This test FAILS** because:
1. Task doesn't have an `assigned_to` attribute yet
2. `calculate_task_score` doesn't accept a `current_user` parameter yet
3. No assignment logic exists in the function

#### Step 2: Write Minimal Code to Pass (GREEN)

**AI asked:** What's the minimum code change to make this test pass?

**My answer:** Add a `current_user` parameter to the function and check if `task.assigned_to` matches it.

```python
def calculate_task_score(task, current_user=None):
    """Calculate a priority score for a task based on multiple factors."""
    # ... existing code ...

    # Boost score for tasks assigned to the current user
    if current_user and hasattr(task, 'assigned_to') and task.assigned_to == current_user:
        score += 12

    return score
```

**AI feedback:** Good — `hasattr()` is a safe way to check if the attribute exists, so existing code that doesn't set `assigned_to` won't break. The `current_user=None` default means all existing calls work without changes.

#### Step 3: Write the Next Test

**AI asked:** What test should you add next?

**My answer:** Test that a task NOT assigned to the current user doesn't get the boost.

```python
@patch('task_priority.datetime')
def test_task_assigned_to_different_user_gets_no_boost(self, mock_datetime):
    """Tasks assigned to a different user should NOT get the +12 boost."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Someone else's task", priority=TaskPriority.MEDIUM)
    task.assigned_to = "alice"
    task.updated_at = now

    score = calculate_task_score(task, current_user="whitney")

    # Expected: base(20) + recency(5) = 25, NO assignment boost
    self.assertEqual(score, 25)
```

#### Step 4: Additional Test — No current_user parameter

```python
@patch('task_priority.datetime')
def test_no_current_user_means_no_assignment_boost(self, mock_datetime):
    """When no current_user is provided, no assignment boost is given."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    task = Task("Assigned task", priority=TaskPriority.MEDIUM)
    task.assigned_to = "whitney"
    task.updated_at = now

    score = calculate_task_score(task)  # No current_user argument

    self.assertEqual(score, 25)  # No boost applied
```

### Exercise 3.2: TDD for Bug Fix

**Bug:** The "days since update" calculation using `.days` can be inaccurate at day boundaries.

#### Step 1: Write a Test That Reproduces the Bug

**AI asked:** What test would reproduce this bug?

**My answer:** Create a task updated 23 hours ago. The `.days` property returns 0 (because it's less than 24 hours), so it gets the recency boost. But a task updated 25 hours ago returns `.days = 1`, so it doesn't. The boundary is imprecise.

```python
@patch('task_priority.datetime')
def test_recency_boost_boundary_at_24_hours(self, mock_datetime):
    """A task updated exactly 23 hours ago should still get the recency
    boost, but a task updated 25 hours ago should not."""
    now = datetime(2026, 2, 10, 12, 0, 0)
    mock_datetime.now.return_value = now

    recent_task = Task("Recent", priority=TaskPriority.MEDIUM)
    recent_task.due_date = None
    recent_task.updated_at = now - timedelta(hours=23)

    old_task = Task("Old", priority=TaskPriority.MEDIUM)
    old_task.due_date = None
    old_task.updated_at = now - timedelta(hours=25)

    recent_score = calculate_task_score(recent_task)
    old_score = calculate_task_score(old_task)

    # Recent task should get recency boost, old task should not
    self.assertEqual(recent_score, 25)  # 20 + 5
    self.assertEqual(old_score, 20)     # 20 + 0
```

**AI feedback:** This test actually passes with the current code because `.days` on a timedelta of 23 hours returns 0, and `.days` on 25 hours returns 1. The `.days` property works correctly here. The actual edge case bug would be if someone expected "last 24 hours" but the code checks "same calendar day" — these are different things. With `.days`, a task updated at 11:59 PM yesterday and checked at 12:01 AM today shows `.days = 0` (less than 1), so it gets the boost — even though it was only 2 minutes ago. But a task updated at 12:01 AM yesterday and checked at 11:59 PM today shows `.days = 0` too — even though it was almost 48 hours ago.

#### Step 2: A Better Regression Test

```python
@patch('task_priority.datetime')
def test_recency_uses_hours_not_calendar_days(self, mock_datetime):
    """Verify the recency boost uses actual time elapsed, not calendar days.
    A task updated 20 hours ago should get the boost."""
    now = datetime(2026, 2, 10, 2, 0, 0)  # 2:00 AM
    mock_datetime.now.return_value = now

    # Task updated yesterday at 10 PM (4 hours ago by clock, but different calendar day)
    task = Task("Cross-day task", priority=TaskPriority.MEDIUM)
    task.due_date = None
    task.updated_at = datetime(2026, 2, 9, 22, 0, 0)  # Yesterday 10 PM

    score = calculate_task_score(task)

    # .days returns 0 for a 4-hour difference, so recency boost applies
    # This is correct behavior: 4 hours ago IS recent
    self.assertEqual(score, 25)  # 20 + 5
```

---

## Part 4: Integration Testing

### Exercise 4.1: Testing the Full Workflow

#### AI's Guidance on Integration Test Design

**AI asked:** What scenarios should an integration test verify for these three functions working together?

**My answer:** That when I give a list of mixed tasks to `get_top_priority_tasks`, the returned tasks are actually the most important ones, in the right order, and limited to the right count.

**AI feedback:** Good. Your integration test should: (1) create tasks that exercise multiple scoring factors, (2) verify the final output order reflects the combined scoring logic, and (3) confirm the limit is respected. Use tasks where the expected order is unambiguous.

#### Integration Test

```python
class TestTaskPriorityIntegration(unittest.TestCase):

    @patch('task_priority.datetime')
    def test_full_workflow_returns_correct_top_tasks_in_order(self, mock_datetime):
        """Integration test: create diverse tasks, sort them, and verify
        get_top_priority_tasks returns the correct top N in the right order.

        This tests all three functions working together:
        calculate_task_score → sort_tasks_by_importance → get_top_priority_tasks
        """
        now = datetime(2026, 2, 10, 12, 0, 0)
        mock_datetime.now.return_value = now

        # Task A: URGENT, overdue, blocker tag, updated today
        # Expected: base(60) + overdue(35) + tag(8) + recency(5) = 108
        task_a = Task("Critical server fix", priority=TaskPriority.URGENT)
        task_a.due_date = now - timedelta(days=2)
        task_a.tags = ["blocker"]
        task_a.updated_at = now

        # Task B: HIGH priority, due tomorrow, no special tags
        # Expected: base(40) + due_soon(15) + recency(5) = 60
        task_b = Task("Feature deadline", priority=TaskPriority.HIGH)
        task_b.due_date = now + timedelta(days=1)
        task_b.tags = ["work"]
        task_b.updated_at = now

        # Task C: LOW priority, overdue, updated today
        # Expected: base(10) + overdue(35) + recency(5) = 50
        task_c = Task("Overdue low task", priority=TaskPriority.LOW)
        task_c.due_date = now - timedelta(days=5)
        task_c.tags = []
        task_c.updated_at = now

        # Task D: MEDIUM priority, no due date, DONE status
        # Expected: base(20) + done(-50) + recency(5) = -25
        task_d = Task("Completed task", priority=TaskPriority.MEDIUM)
        task_d.status = TaskStatus.DONE
        task_d.tags = []
        task_d.updated_at = now

        # Task E: MEDIUM priority, due in 5 days, updated 3 days ago
        # Expected: base(20) + due_week(10) + recency(0) = 30
        task_e = Task("Routine task", priority=TaskPriority.MEDIUM)
        task_e.due_date = now + timedelta(days=5)
        task_e.tags = []
        task_e.updated_at = now - timedelta(days=3)

        # Shuffle the order — the functions should sort correctly regardless
        all_tasks = [task_d, task_b, task_e, task_a, task_c]

        # Test get_top_priority_tasks with limit=3
        top_3 = get_top_priority_tasks(all_tasks, limit=3)

        # Verify count
        self.assertEqual(len(top_3), 3)

        # Verify order: A (108) → B (60) → C (50)
        self.assertEqual(top_3[0].title, "Critical server fix")
        self.assertEqual(top_3[1].title, "Feature deadline")
        self.assertEqual(top_3[2].title, "Overdue low task")

        # Verify the completed task is NOT in top 3 (score = -25)
        top_titles = [t.title for t in top_3]
        self.assertNotIn("Completed task", top_titles)

        # Also verify the full sort order
        all_sorted = sort_tasks_by_importance(all_tasks)
        self.assertEqual(all_sorted[0].title, "Critical server fix")   # 108
        self.assertEqual(all_sorted[1].title, "Feature deadline")      # 60
        self.assertEqual(all_sorted[2].title, "Overdue low task")      # 50
        self.assertEqual(all_sorted[3].title, "Routine task")          # 30
        self.assertEqual(all_sorted[4].title, "Completed task")        # -25
```

#### Why This Test Is Valuable

This single test verifies that:
1. `calculate_task_score` correctly combines all five factors for each task
2. `sort_tasks_by_importance` puts tasks in the correct order based on those scores
3. `get_top_priority_tasks` respects the limit parameter
4. The completed task (negative score) is correctly pushed to the bottom
5. A LOW priority overdue task correctly outranks a MEDIUM task due in 5 days — proving that due date urgency can override raw priority level

---

## Part 5: Reflection

### What I learned about testing

**Testing is about verifying behavior, not just checking that code runs.** My first test (`assertTrue(score > 0)`) technically passed but proved almost nothing. A good test proves that the code does the *right thing*, not just *something*.

**Mocking is essential for time-dependent code.** Without mocking `datetime.now()`, tests that check recency or due dates would produce different results depending on when you run them. A test that passes on Monday but fails on Tuesday is worse than no test at all — it erodes trust in the test suite.

**The TDD workflow (Red → Green → Refactor) forces small, deliberate steps.** Writing the test first made me think about the *interface* before the *implementation*. When adding the `assigned_to` feature, I decided `calculate_task_score` should accept a `current_user` parameter — that design decision came from writing the test first, not from thinking about the implementation.

**Edge cases are where bugs live.** The most interesting tests weren't the "does HIGH priority score higher than LOW?" tests — those are obvious. The valuable tests were boundaries: what happens at exactly 0 days? What about case-sensitive tag matching? What if a task has no due date? These are the tests that catch real bugs.

**Integration tests catch different bugs than unit tests.** The unit tests verify each factor in isolation. The integration test catches ordering errors that only appear when multiple factors interact — like a LOW overdue task outranking a MEDIUM task due next week. Both types are needed.

### Testing concepts I now understand

- **Unit test:** Tests one function in isolation with controlled inputs
- **Integration test:** Tests multiple functions working together
- **Assertion:** The check that verifies the expected outcome (`assertEqual`, `assertGreater`, etc.)
- **Mocking:** Replacing a real dependency (like `datetime`) with a controllable fake
- **Test fixture:** Setup code that creates the objects needed for testing (`setUp` method)
- **TDD (Test-Driven Development):** Write a failing test → write minimal code to pass → refactor → repeat
- **Edge case:** An unusual or boundary input that might break the code
- **Deterministic test:** A test that always produces the same result regardless of when/where it runs
