# Exercise 2: Codebase Exploration Challenge

## Code Understanding Journal — Task Manager Application (Python)

---

## Part 1: Understanding Task Creation & Status Updates

**Prompt Strategy Used:** Prompt 1 — Understand how a specific feature works

### Main Components Involved

| File | Role in Task Creation | Role in Status Updates |
|------|----------------------|----------------------|
| **cli.py** | Parses the 'create' command, extracts title, description, priority, due date, and tags from user input | Parses the 'status' command, extracts task_id and the new status value from user input |
| **app.py** | Converts raw inputs into proper types (priority number → Enum, date string → datetime). Creates the Task object and passes it to storage. | Contains special logic: if status is 'done', calls mark_as_done() to record completion time. Otherwise does a standard update. |
| **models.py** | The Task `__init__` method runs: generates unique ID, sets status to TODO, records timestamps, stores all properties. | The `Task.update()` method changes any property. The `mark_as_done()` method sets status=DONE and records completed_at timestamp. |
| **storage.py** | `add_task()` stores the task in a dictionary keyed by ID. `save()` writes all tasks to tasks.json using a custom JSON encoder. | `update_task()` finds the task by ID, calls `task.update()`, then `save()`. For 'done' status, app.py calls `save()` directly. |

### Execution Flow: Task Creation

1. **User Input:** User types a create command (e.g., `create "Buy groceries" -p 3 -u 2026-03-01`)
2. **CLI Parsing (cli.py):** argparse extracts each argument. Tags are split by commas using a list comprehension.
3. **Validation & Conversion (app.py):** Priority integer is converted to a TaskPriority Enum. Date string is parsed with try/except for error handling.
4. **Object Creation (models.py):** A new Task instance is created with auto-generated UUID, status set to TODO, and current timestamps.
5. **Persistence (storage.py):** Task is added to the in-memory dictionary and saved to tasks.json using a custom encoder that converts Python objects to JSON-safe formats.
6. **Confirmation (cli.py):** The task ID is printed to the user as confirmation.

### How Data Is Stored and Retrieved

Tasks are stored in two places simultaneously: in memory as a Python dictionary (`self.tasks`) keyed by task ID, and on disk as a JSON file (`tasks.json`). Every change triggers a full rewrite of the JSON file via `save()`. When the program starts, `TaskStorage.__init__()` calls `load()` which reads the JSON file and reconstructs Task objects using a custom decoder.

The custom `TaskEncoder` converts Python-specific objects (Enum values, datetime objects) into JSON-compatible formats. The custom `TaskDecoder` reverses this process, converting stored data back into proper Python objects.

### Design Patterns Discovered

- **Layered Architecture:** Each file has a single responsibility and only communicates with adjacent layers (CLI → App → Storage → Models)
- **Special-case handling for 'done' status:** The code treats marking a task as done differently from other status changes, recording a completion timestamp. This is a deliberate design choice to enable features like "completed this week" statistics.
- **Defensive programming:** Input validation with try/except blocks, None checks before operations, and graceful error messages rather than crashes.

---

## Part 2: Deepening Understanding — Task Prioritization

**Prompt Strategy Used:** Prompt 2 — Deepen understanding through guided questioning (pair programmer approach)

### Initial Understanding vs. What I Discovered

| Initial Understanding | What I Actually Discovered |
|----------------------|---------------------------|
| Priorities are just labels attached to tasks | Priorities are Enum values with numeric backing (1-4), meaning they have a natural ordering that could be used for sorting |
| You can filter tasks by priority | Filtering is limited: you can only filter by ONE priority at a time, and cannot combine priority + status filters simultaneously |
| Priority is set once when creating a task | Priority can be changed at any time via `update_task_priority()`. The Enum ensures only valid values (1-4) are accepted. |
| Priority affects how tasks are displayed | The CLI uses exclamation marks (! to !!!!) to visually indicate priority. However, tasks are not sorted by priority — they appear in storage order. |

### Key Insights from Guided Questions

1. **Filtering limitation:** The `list_tasks()` method uses sequential if/elif checks. This means if you pass both a status and priority filter, only the status filter is applied. This is a design limitation, not a deliberate feature.

2. **No sorting capability:** Despite priorities having numeric values that enable comparison (LOW=1 < URGENT=4), the code never sorts tasks by priority. This would be a natural feature to add.

3. **Enum as validation:** Using an Enum instead of raw integers prevents invalid priorities. If you try `TaskPriority(99)`, Python raises a ValueError. This is a form of built-in input validation.

4. **Priority in statistics:** The `get_statistics()` method counts tasks per priority level, showing the distribution. This is useful for workload assessment.

5. **Default priority:** When no priority is specified during creation, it defaults to MEDIUM (2). This is set as a default parameter in `create_task()`.

### Misconceptions Clarified

- Initially assumed priorities would affect task ordering in the list view — they do not. Tasks appear in insertion order.
- Thought you could combine filters (e.g., show all HIGH priority tasks that are IN_PROGRESS). The current architecture does not support combined filtering.

---

## Part 3: Mapping Data Flow — Task Completion

**Prompt Strategy Used:** Prompt 3 — Mapping data flow and state management

### Data Flow Diagram

When a user marks a task as complete by running `status <task_id> done`, the data flows through four layers:

```
User types: status abc12345 done
         │
         ▼
┌─────────────────────────────────┐
│ Layer 1: CLI (cli.py)           │
│ line 105-109                    │
│ Extracts task_id & status       │
│ Calls update_task_status()      │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Layer 2: App Logic (app.py)     │
│ line 40-49                      │
│ Converts "done" → Enum          │
│ SPECIAL CASE: calls             │
│ task.mark_as_done()             │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Layer 3: Model (models.py)      │
│ line 38-41                      │
│ mark_as_done() sets:            │
│   • status → DONE               │
│   • completed_at → now          │
│   • updated_at → now            │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Layer 4: Storage (storage.py)   │
│ line 60-64                      │
│ Serializes ALL tasks to JSON    │
│ Writes to tasks.json            │
└─────────────────────────────────┘
```

### State Changes During Task Completion

| Property | Before Completion | After Completion |
|----------|------------------|-----------------|
| `task.status` | TaskStatus.TODO / IN_PROGRESS / REVIEW | TaskStatus.DONE |
| `task.completed_at` | None | Current datetime (e.g., 2026-02-09 14:30:00) |
| `task.updated_at` | Previous update timestamp | Current datetime (same as completed_at) |
| `tasks.json` | Contains task with old status/timestamps | Entire file rewritten with updated values |

### Potential Points of Failure

1. **Invalid task ID:** If the task_id does not exist, `get_task()` returns None. The code handles this gracefully, returning False.

2. **File write failure:** If tasks.json cannot be written (disk full, permissions issue), `save()` catches the exception and prints an error. However, the in-memory data has already been changed, creating an inconsistency between memory and disk.

3. **No idempotency check:** Marking an already-done task as done again will overwrite the original `completed_at` timestamp. There is no guard against this.

4. **Full file rewrite:** Every `save()` rewrites the entire file. If the application crashes mid-write, all task data could be corrupted. A more robust approach would use atomic writes or a database.

---

## Part 4: Reflection and Presentation Notes

### High-Level Application Architecture

The Task Manager is a command-line to-do list application built with a four-layer architecture. The CLI layer handles user input/output, the Application layer contains business logic, the Storage layer manages data persistence via JSON, and the Model layer defines data structures. Each layer has a single responsibility and only communicates with the layer directly below it.

### How the Three Key Features Work

1. **Task Creation:** User input flows through CLI parsing → type validation/conversion in app → Task object instantiation with auto-generated ID → dictionary storage + JSON persistence.

2. **Task Prioritization:** Implemented using Python Enums (LOW=1 through URGENT=4). Priorities can be set at creation and changed later. Filtering by priority uses list comprehensions, but cannot be combined with other filters.

3. **Task Completion:** Has special handling compared to other status changes. Records a completion timestamp via `mark_as_done()`, enabling features like "completed in the last 7 days" statistics.

### Most Interesting Design Pattern

The special-case handling for task completion is the most interesting pattern. Rather than treating all status updates identically, the developers created a dedicated `mark_as_done()` method that captures additional metadata (completion timestamp). This forward-thinking design enables the statistics feature that counts recently completed tasks, demonstrating how a small design decision can unlock future capabilities.

### Most Challenging Aspect & How Prompts Helped

The most challenging aspect was understanding the data serialization in storage.py. The custom JSON encoder/decoder classes (`TaskEncoder` and `TaskDecoder`) convert between Python objects and JSON-compatible formats. This was confusing because it involves converting between different representations of the same data.

The data flow mapping prompt (Prompt 3) was most helpful here because it forced me to trace exactly what happens to each piece of data at every step. By following the complete path of a task from creation to storage to retrieval, the encoder/decoder logic became clear: it is simply a translation layer between Python's rich objects and JSON's limited data types.

### Which Prompt Strategy Worked Best

- **Prompt 1 (Feature Understanding):** Best for getting an initial overview of how components connect. Good starting point.
- **Prompt 2 (Guided Questions):** Best for uncovering hidden limitations and design decisions. The questions revealed the single-filter limitation and the lack of sorting.
- **Prompt 3 (Data Flow Mapping):** Best for understanding complex multi-step processes. Essential for identifying failure points and understanding state changes.

### Strategies for Approaching Unfamiliar Code

1. Start by reading file names and directory structure before diving into code
2. Form your own hypothesis about what the code does before asking AI
3. Trace one complete operation through all layers to build understanding
4. Use different prompt strategies for different needs: overview, deepening, or flow mapping
5. Document misconceptions — knowing what you got wrong is as valuable as knowing what you got right
