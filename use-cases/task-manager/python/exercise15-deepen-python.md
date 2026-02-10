# Exercise 15: Applying AI to Deepen Programming Language Understanding

---

## Activity 1: Idiomatic Code Transformation

### Code Selected

The `sort_tasks_by_importance` and `get_top_priority_tasks` functions from our `task_priority.py` (Exercise 3/10):

```python
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

### Prompt Used

> I'm learning to write more idiomatic Python. Here's my current code:
>
> [pasted the two functions above]
>
> Could you:
> 1. Suggest ways to make this more idiomatic
> 2. Explain why these changes follow language best practices
> 3. Point out any language features I'm not taking advantage of
> 4. Show me both my version and an improved version side by side

### AI Suggestions

#### Issue 1: Unnecessary intermediate step in `sort_tasks_by_importance`

**My version** creates a list of (score, task) tuples, sorts them, then extracts just the tasks:

```python
task_scores = [(calculate_task_score(task), task) for task in tasks]
sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
return sorted_tasks
```

**Idiomatic version** uses `sorted()` with a `key` function directly:

```python
def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    return sorted(tasks, key=calculate_task_score, reverse=True)
```

**Why this is better:** Python's `sorted()` already has a `key` parameter designed for exactly this. Instead of manually creating tuples, sorting, then extracting — you just tell `sorted()` "use this function to get the comparison value." It's one line instead of three, and the intent is clearer: "sort tasks, using `calculate_task_score` as the sorting key, highest first."

**Python feature I wasn't using:** You can pass a function name (without parentheses) as the `key` argument. `key=calculate_task_score` means "for each task, call `calculate_task_score(task)` and sort by the result." No lambda needed.

#### Issue 2: Unnecessary variable in `get_top_priority_tasks`

**My version:**
```python
def get_top_priority_tasks(tasks, limit=5):
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]
```

**Idiomatic version:**
```python
def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks."""
    return sort_tasks_by_importance(tasks)[:limit]
```

**Why:** When a variable is only used once immediately after assignment, it's often clearer to inline it. `sorted_tasks` doesn't add any information that the function call doesn't already convey.

#### Issue 3: Type hints would make the code more Pythonic

**Idiomatic version with type hints:**
```python
from typing import List

def sort_tasks_by_importance(tasks: List[Task]) -> List[Task]:
    """Sort tasks by calculated importance score (highest first)."""
    return sorted(tasks, key=calculate_task_score, reverse=True)

def get_top_priority_tasks(tasks: List[Task], limit: int = 5) -> List[Task]:
    """Return the top N priority tasks."""
    return sort_tasks_by_importance(tasks)[:limit]
```

**Why type hints matter:** They tell anyone reading the code exactly what goes in and what comes out, without reading the implementation. They also enable editors and tools to catch bugs before you run the code. Modern Python (3.5+) supports them, and they're considered best practice.

### Side-by-Side Comparison

```python
# ─── BEFORE (my version) ─────────────────────────────
def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    return sorted_tasks

def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks."""
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]

# ─── AFTER (idiomatic Python) ─────────────────────────
from typing import List

def sort_tasks_by_importance(tasks: List[Task]) -> List[Task]:
    """Sort tasks by calculated importance score (highest first)."""
    return sorted(tasks, key=calculate_task_score, reverse=True)

def get_top_priority_tasks(tasks: List[Task], limit: int = 5) -> List[Task]:
    """Return the top N priority tasks."""
    return sort_tasks_by_importance(tasks)[:limit]
```

### 3 Key Learnings

1. **`sorted(items, key=function)` eliminates manual tuple-building.** Instead of creating (score, item) pairs, sorting, and extracting, you pass the scoring function directly as the `key` argument. Python handles the rest. This is one of the most common Python idioms for custom sorting.

2. **Functions are first-class objects in Python.** `key=calculate_task_score` passes the function itself (without calling it). Python will call it on each item internally. This is different from `key=calculate_task_score(task)` which would call it immediately and pass the *result*. Understanding this distinction unlocks many idiomatic Python patterns.

3. **Type hints are documentation that tools can check.** `def sort_tasks_by_importance(tasks: List[Task]) -> List[Task]` tells you at a glance: takes a list of Tasks, returns a list of Tasks. They don't change how the code runs, but they make it dramatically easier to understand and catch errors early.

---

## Activity 2: Code Quality Detective

### Code Selected

The original `discount` function from Exercise 13, *before* refactoring:

```python
def discount(cart,promos,user):
    d=0;tot=0
    for i in cart:tot+=i['price']*i['quantity']
    for p in promos:
        if p['type']=='percent' and (p['min_purchase'] is None or tot>=p['min_purchase']):val=tot*p['value']/100;d=max(d,val)
        elif p['type']=='fixed' and (p['min_purchase'] is None or tot>=p['min_purchase']):val=min(p['value'],tot);d=max(d,val)
        elif p['type']=='shipping' and tot>=p['min_purchase']:user['free_shipping']=True
    if user['status']=='vip':vd=tot*0.05;d=max(d,vd)
    elif user['status']=='member' and user['months']>6:vd=tot*0.02;d=max(d,vd)
    return {'original':tot,'discount':d,'final':tot-d,'free_shipping':user.get('free_shipping',False)}
```

### Prompt Used

> I'm a junior developer working with Python. Could you review this code for quality improvements:
>
> [pasted the discount function]
>
> Please:
> 1. Identify any code smells or quality issues
> 2. Suggest specific improvements
> 3. Explain why these improvements matter in Python
> 4. Rate the code's readability, performance, and maintainability

### AI Quality Review

#### Code Smells Identified

| # | Code Smell | Example | Severity |
|---|-----------|---------|----------|
| 1 | **Cryptic variable names** | `d`, `tot`, `i`, `p`, `val`, `vd` | 🔴 Critical |
| 2 | **Multiple statements per line** | `d=0;tot=0` and entire if-blocks on one line | 🔴 Critical |
| 3 | **No spacing around operators** | `cart,promos,user` and `d=0;tot=0` | 🟡 Major |
| 4 | **Magic numbers** | `0.05`, `0.02`, `6` with no explanation | 🟡 Major |
| 5 | **Side effect on input** | `user['free_shipping']=True` modifies caller's dict | 🟡 Major |
| 6 | **No docstring** | No indication of what the function does | 🟡 Major |
| 7 | **No input validation** | Empty cart, None promos would crash | 🟢 Minor |
| 8 | **No type hints** | Parameters could be anything | 🟢 Minor |
| 9 | **Business rules hidden** | "Highest discount wins" not documented | 🟡 Major |
| 10 | **God function** | One function does cart total, promo calc, loyalty calc, shipping check | 🟡 Major |

#### AI's Ratings

| Dimension | Rating | Explanation |
|-----------|--------|-------------|
| **Readability** | 2/10 | Virtually unreadable. Cryptic names, crammed formatting, hidden logic. A new developer would need 15+ minutes to understand what this does. |
| **Performance** | 7/10 | The logic itself is fine — it loops through cart and promos once each. No performance issues at this scale. |
| **Maintainability** | 2/10 | Changing the VIP discount rate means finding `0.05` in a dense line. Adding a new promo type means adding to an already unreadable if/elif chain. High risk of introducing bugs. |

### Quality Checklist (for future code reviews)

Based on the issues found, here's a checklist I can apply to any code I write or review:

- [ ] **Are all variables descriptively named?** (No single-letter names except in trivial loops)
- [ ] **One statement per line?** (Never use semicolons to combine statements)
- [ ] **Consistent spacing?** (Spaces around `=`, after commas, around operators — PEP 8)
- [ ] **Magic numbers replaced with named constants?** (Any literal other than 0 or 1)
- [ ] **Does the function modify its inputs?** (Flag any side effects as potential issues)
- [ ] **Is there a docstring?** (Every function needs at minimum a one-line description)
- [ ] **Is the function doing too many things?** (If you need "and" to describe it, consider splitting)
- [ ] **Are business rules documented?** (Non-obvious logic like "highest discount wins" should be commented)
- [ ] **Are edge cases handled?** (Empty inputs, None values, missing keys)
- [ ] **Would a new developer understand this in under 60 seconds?** (The ultimate readability test)

### 3 Key Learnings

1. **PEP 8 isn't just style — it's communication.** The Python community agreed on formatting rules (spaces around operators, one statement per line, consistent naming) because consistent code is faster to read. Breaking PEP 8 doesn't cause errors, but it causes confusion, which causes bugs.

2. **Side effects are a design smell.** When `discount()` silently modifies the `user` dictionary, the caller has no idea their data was changed. This is a common source of bugs. Functions should either return new data or clearly document that they modify inputs.

3. **Code quality and performance are different axes.** The code was 7/10 for performance but 2/10 for readability and maintainability. Working code that nobody can understand is a liability — the next bug fix might introduce two more bugs because the developer couldn't follow the logic.

---

## Activity 3: Understanding a Language Feature — List Comprehensions

### Feature Chosen

**List comprehensions** in Python. I've been seeing them in AI suggestions throughout these exercises (`[task for _, task in sorted(...)]`, `[s for s in filtered if ...]`) but haven't deeply understood how they work or when to use them.

### Prompt Used

> I want to improve my understanding of list comprehensions in Python.
>
> 1. Could you explain this feature with simple examples?
> 2. Show me 3 practical use cases where this would be valuable
> 3. Provide a small project idea that would help me practice this feature
> 4. What common mistakes should I avoid when using this feature?

### AI Explanation

#### What Are List Comprehensions?

A list comprehension is a concise way to create a list by transforming and/or filtering another collection. The basic pattern:

```python
new_list = [expression for item in iterable if condition]
```

This is equivalent to:

```python
new_list = []
for item in iterable:
    if condition:
        new_list.append(expression)
```

#### Simple Examples (Building Up)

**1. Transform every item:**
```python
# Double every number
numbers = [1, 2, 3, 4, 5]

# Loop version
doubled = []
for n in numbers:
    doubled.append(n * 2)

# Comprehension version
doubled = [n * 2 for n in numbers]

# Result: [2, 4, 6, 8, 10]
```

**2. Filter items:**
```python
# Keep only even numbers
numbers = [1, 2, 3, 4, 5, 6, 7, 8]

# Loop version
evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)

# Comprehension version
evens = [n for n in numbers if n % 2 == 0]

# Result: [2, 4, 6, 8]
```

**3. Transform AND filter:**
```python
# Get the uppercase names of people over 18
people = [
    {'name': 'Alice', 'age': 25},
    {'name': 'Bob', 'age': 17},
    {'name': 'Carol', 'age': 30},
    {'name': 'Dave', 'age': 15}
]

# Loop version
adult_names = []
for person in people:
    if person['age'] >= 18:
        adult_names.append(person['name'].upper())

# Comprehension version
adult_names = [person['name'].upper() for person in people if person['age'] >= 18]

# Result: ['ALICE', 'CAROL']
```

#### 3 Practical Use Cases

**Use Case 1: Extracting data from dictionaries**

This comes up constantly when working with APIs or databases:

```python
# Extract just the emails from a list of users
users = [
    {'name': 'Alice', 'email': 'alice@test.com', 'active': True},
    {'name': 'Bob', 'email': 'bob@test.com', 'active': False},
    {'name': 'Carol', 'email': 'carol@test.com', 'active': True},
]

# Get emails of active users only
active_emails = [user['email'] for user in users if user['active']]
# Result: ['alice@test.com', 'carol@test.com']
```

**Use Case 2: Data cleaning and transformation**

```python
# Clean up a list of user-entered strings
raw_tags = ['  Python ', 'JAVASCRIPT', '  react  ', '', 'CSS', '  ']

# Strip whitespace, lowercase, and remove empty strings
clean_tags = [tag.strip().lower() for tag in raw_tags if tag.strip()]
# Result: ['python', 'javascript', 'react', 'css']
```

**Use Case 3: Creating test data**

```python
from datetime import datetime, timedelta

# Create 7 days of sample dates
today = datetime.now()
week_of_dates = [today + timedelta(days=i) for i in range(7)]

# Create sample tasks for testing
priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
test_tasks = [
    {'title': f'Task {i}', 'priority': priorities[i % 4]}
    for i in range(10)
]
```

#### My Practice Implementation

**Project idea from AI:** Build a grade analyzer that takes a list of student scores and uses comprehensions to calculate statistics and filter results.

```python
def analyze_grades(students):
    """
    Analyze student grades using list comprehensions.
    
    Args:
        students: List of dicts with 'name', 'scores' (list of ints)
    
    Returns:
        Dict with analysis results
    """
    # Calculate average for each student
    averages = [
        {'name': s['name'], 'average': sum(s['scores']) / len(s['scores'])}
        for s in students
        if s['scores']  # Skip students with no scores
    ]

    # Find passing students (average >= 60)
    passing = [s['name'] for s in averages if s['average'] >= 60]

    # Find failing students
    failing = [s['name'] for s in averages if s['average'] < 60]

    # Get all individual scores flattened into one list
    all_scores = [score for s in students for score in s['scores']]

    # Find students who got at least one perfect score (100)
    perfect_scorers = [
        s['name'] for s in students
        if any(score == 100 for score in s['scores'])
    ]

    return {
        'averages': averages,
        'passing': passing,
        'failing': failing,
        'class_average': sum(all_scores) / len(all_scores) if all_scores else 0,
        'highest_score': max(all_scores) if all_scores else 0,
        'perfect_scorers': perfect_scorers,
    }


# Test it
students = [
    {'name': 'Alice', 'scores': [85, 92, 78, 100]},
    {'name': 'Bob', 'scores': [55, 62, 48, 70]},
    {'name': 'Carol', 'scores': [95, 100, 88, 92]},
    {'name': 'Dave', 'scores': [42, 38, 55, 45]},
    {'name': 'Eve', 'scores': [75, 80, 72, 68]},
]

result = analyze_grades(students)
print(f"Passing: {result['passing']}")        # ['Alice', 'Carol', 'Eve']
print(f"Failing: {result['failing']}")        # ['Bob', 'Dave']
print(f"Perfect scorers: {result['perfect_scorers']}")  # ['Alice', 'Carol']
print(f"Class average: {result['class_average']:.1f}")  # 72.4
```

#### Nested Comprehension (Advanced)

The line `all_scores = [score for s in students for score in s['scores']]` is a **nested comprehension** — equivalent to:

```python
all_scores = []
for s in students:
    for score in s['scores']:
        all_scores.append(score)
```

Read it left to right: "for each student, for each score in their scores, include that score."

#### Common Mistakes to Avoid

| Mistake | Example | Why It's Bad | Better |
|---------|---------|-------------|--------|
| **Too long / complex** | `[x.name for x in data if x.active and x.score > 50 and x.type in allowed_types and not x.deleted]` | Unreadable; defeats the purpose | Use a regular loop with comments |
| **Side effects inside comprehension** | `[print(x) for x in items]` | Comprehensions should create data, not perform actions | Use a regular `for` loop |
| **Nested too deeply** | `[[y for y in x if y > 0] for x in matrix if len(x) > 2]` | Hard to parse mentally | Break into steps with named variables |
| **Using when you don't need the list** | `[x for x in range(1000000)]` | Creates entire list in memory | Use a generator: `(x for x in range(1000000))` |

**Rule of thumb:** If a comprehension takes more than about 80 characters or needs more than one `if` clause, switch to a regular loop. Clarity beats cleverness.

### 3 Key Learnings

1. **List comprehensions replace the "empty list → loop → append" pattern.** Any time I write `result = []` followed by a `for` loop with `result.append(...)`, I should consider whether a comprehension is clearer. For simple cases, it always is.

2. **The `if` clause is a built-in filter.** `[x for x in items if condition]` is the Pythonic way to filter a list. No need for separate filter loops. This pattern appears constantly in real code — filtering active users, valid entries, matching tags, etc.

3. **Know when to stop.** The most common comprehension mistake is making them too complex. If I need more than one `if` clause, or if the expression part is a multi-step calculation, a regular loop with comments is better. The goal is readability, not fewest lines of code.

---

## Group Discussion Summary

### Common Themes Across Activities

1. **Python values readability above all else.** Every improvement — from idiomatic `sorted()` to PEP 8 formatting to clean comprehensions — prioritizes making code easier for humans to read. Python's philosophy ("There should be one obvious way to do it") shows up everywhere.

2. **Built-in functions are more powerful than we think.** `sorted(key=...)`, `any()`, `max()`, `sum()`, `enumerate()`, `.get()` — Python has a built-in function for almost every common pattern. Learning them replaces dozens of lines of manual loop code with single, clear expressions.

3. **The line between "idiomatic" and "clever" is important.** A one-line nested list comprehension might be technically idiomatic, but if it takes 30 seconds to parse mentally, a three-line loop is better. The test: would a teammate understand this in 5 seconds?
