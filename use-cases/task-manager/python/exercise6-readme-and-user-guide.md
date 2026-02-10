# Exercise 6: README and User Guide Documentation

## Project Chosen: Task Manager (Python CLI Application)

---

## Prompt 1 Output: Comprehensive README

---

# TaskManager CLI

A lightweight command-line task management application built in Python. Create, organize, and track your tasks directly from the terminal — no external dependencies required.

## Features

- **Task Creation** — Create tasks with titles, descriptions, priorities, due dates, and tags
- **Priority Levels** — Organize tasks as LOW, MEDIUM, HIGH, or URGENT
- **Status Tracking** — Track tasks through TODO → IN_PROGRESS → REVIEW → DONE
- **Due Date Management** — Set and update deadlines, identify overdue tasks
- **Tag System** — Add and remove tags for flexible categorization
- **Filtering** — View tasks filtered by status, priority, or overdue status
- **Statistics** — Get an overview of task counts by status, priority, overdue, and recently completed
- **Persistent Storage** — Tasks are saved to a JSON file and survive between sessions

## Installation

### Prerequisites

- Python 3.7 or higher (no external packages required)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/task-manager.git
cd task-manager/python
```

2. Verify Python is installed:
```bash
python3 --version
```

That's it — no `pip install` needed. The project uses only Python's built-in standard library.

## Usage

### Creating Tasks

```bash
# Basic task
python -m cli create "Buy groceries"

# Task with priority (1=Low, 2=Medium, 3=High, 4=Urgent)
python -m cli create "Fix login bug" -p 4

# Task with due date
python -m cli create "Submit report" -u 2026-03-15

# Task with description, priority, due date, and tags
python -m cli create "Prepare presentation" -d "Q1 sales review" -p 3 -u 2026-02-20 -t "work,urgent"
```

### Listing Tasks

```bash
# List all tasks
python -m cli list

# Filter by status
python -m cli list -s todo
python -m cli list -s in_progress
python -m cli list -s done

# Filter by priority (1=Low, 2=Medium, 3=High, 4=Urgent)
python -m cli list -p 4

# Show only overdue tasks
python -m cli list -o
```

### Updating Tasks

```bash
# Update task status
python -m cli status <task_id> in_progress
python -m cli status <task_id> done

# Update task priority
python -m cli priority <task_id> 3

# Update due date
python -m cli due <task_id> 2026-04-01
```

### Managing Tags

```bash
# Add a tag
python -m cli tag <task_id> urgent

# Remove a tag
python -m cli untag <task_id> urgent
```

### Other Commands

```bash
# View task details
python -m cli show <task_id>

# Delete a task
python -m cli delete <task_id>

# View statistics
python -m cli stats
```

## Project Structure

```
python/
├── models.py    — Data definitions (Task, TaskPriority, TaskStatus enums)
├── storage.py   — JSON file persistence (save/load/CRUD operations)
├── app.py       — Business logic (TaskManager class)
└── cli.py       — Command-line interface (entry point)
```

### Architecture

The project follows a **layered architecture** where each file has a single responsibility:

```
User → cli.py → app.py → storage.py → models.py
       (input)   (logic)   (data)      (definitions)
```

- **cli.py** parses user commands and displays results
- **app.py** contains all business logic and validation
- **storage.py** handles reading/writing tasks to `tasks.json`
- **models.py** defines the Task class and Enum types

## Configuration

The application stores tasks in a `tasks.json` file in the current working directory. You can specify a custom storage path by modifying the `TaskManager` initialization in `cli.py`:

```python
task_manager = TaskManager(storage_path="custom/path/tasks.json")
```

### Status Values

| Status | CLI Value | Symbol | Description |
|--------|-----------|--------|-------------|
| To Do | `todo` | `[ ]` | Not yet started |
| In Progress | `in_progress` | `[>]` | Currently being worked on |
| Review | `review` | `[?]` | Awaiting review |
| Done | `done` | `[✓]` | Completed |

### Priority Values

| Priority | CLI Value | Symbol | Description |
|----------|-----------|--------|-------------|
| Low | `1` | `!` | Can wait |
| Medium | `2` | `!!` | Normal importance (default) |
| High | `3` | `!!!` | Should be done soon |
| Urgent | `4` | `!!!!` | Needs immediate attention |

## Troubleshooting

### "No module named 'models'" or similar import errors
Make sure you're running the CLI from inside the `python/` directory, or use `python -m cli` instead of `python cli.py`.

### Tasks disappearing between sessions
Check that `tasks.json` exists in your current directory. If you run the CLI from different directories, each directory will have its own `tasks.json` file.

### "Invalid date format" error
Due dates must be in `YYYY-MM-DD` format (e.g., `2026-03-15`). Other formats like `03/15/2026` or `March 15` are not supported.

### Task ID not found
Task IDs are long UUID strings (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`). You can use the first 8 characters shown in the list view, but the full ID is needed for commands. Use `python -m cli list` to see all task IDs.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes manually
5. Commit (`git commit -m "Add your feature"`)
6. Push to your branch (`git push origin feature/your-feature`)
7. Open a Pull Request

## License

This project is provided for educational purposes as part of the We Think Code AI-assisted development course.

## Acknowledgments

- Built using Python's standard library (json, datetime, uuid, enum, argparse)
- Part of the [We Think Code](https://www.wethinkcode.co.za/) AI Code Exercises

---
---

## Prompt 2 Output: Step-by-Step Guide

---

# Step-by-Step Guide: Creating and Managing Tasks in TaskManager

This guide walks you through the complete workflow of creating a task, tracking its progress through different stages, and viewing your task statistics. It's written for beginners who are new to command-line tools.

## Prerequisites

- Python 3.7+ installed on your machine
- The TaskManager project downloaded to your computer
- A terminal/command prompt open
- Navigate to the `python/` directory of the project

## Step 1: Create Your First Task

Open your terminal and type:

```bash
python -m cli create "Build personal portfolio website"
```

You should see output like:
```
Created task with ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Save this ID** — you'll need it for future commands. The first 8 characters (`a1b2c3d4`) are shown in list views.

### Adding More Details

Create a more detailed task:

```bash
python -m cli create "Write blog post about Python" -d "Cover basics of variables and loops" -p 3 -u 2026-03-01 -t "writing,python"
```

This sets:
- `-d` → Description
- `-p 3` → HIGH priority
- `-u 2026-03-01` → Due date of March 1st, 2026
- `-t "writing,python"` → Two tags (comma-separated, no spaces after commas)

## Step 2: View Your Tasks

List all your tasks:

```bash
python -m cli list
```

You'll see output like:
```
[ ] a1b2c3d4 - !! Build personal portfolio website
  
  No due date | No tags
  Created: 2026-02-09 22:30
--------------------------------------------------
[ ] b5c6d7e8 - !!! Write blog post about Python
  Cover basics of variables and loops
  Due: 2026-03-01 | Tags: writing, python
  Created: 2026-02-09 22:31
--------------------------------------------------
```

**Reading the output:**
- `[ ]` = TODO status (not started)
- `!!` = MEDIUM priority, `!!!` = HIGH priority
- The 8-character string after the status is the shortened task ID

## Step 3: Start Working on a Task

When you begin working on a task, update its status to "in progress":

```bash
python -m cli status a1b2c3d4-e5f6-7890-abcd-ef1234567890 in_progress
```

You'll see:
```
Updated task status to in_progress
```

**Common mistake:** You need the **full task ID**, not just the 8-character short version shown in list output. Use `python -m cli list` and copy the full ID from there. Alternatively, use `python -m cli show` with the task ID to see full details.

## Step 4: Add Tags to Organize Your Work

Add a tag to categorize your task:

```bash
python -m cli tag a1b2c3d4-e5f6-7890-abcd-ef1234567890 portfolio
```

You'll see:
```
Added tag 'portfolio' to task
```

You can add multiple tags by running the command multiple times with different tag names.

## Step 5: Move a Task to Review

When you've finished the work and need someone to review it:

```bash
python -m cli status a1b2c3d4-e5f6-7890-abcd-ef1234567890 review
```

## Step 6: Complete a Task

Mark the task as done:

```bash
python -m cli status a1b2c3d4-e5f6-7890-abcd-ef1234567890 done
```

**What happens behind the scenes:** When you mark a task as "done," the system records a `completed_at` timestamp. This is different from other status changes — the code has special handling for the "done" status, which enables the statistics feature to count recently completed tasks.

## Step 7: Check Your Statistics

See an overview of all your tasks:

```bash
python -m cli stats
```

Output:
```
Total tasks: 2
By status:
  todo: 1
  in_progress: 0
  review: 0
  done: 1
By priority:
  1: 0
  2: 1
  3: 1
  4: 0
Overdue tasks: 0
Completed in last 7 days: 1
```

## Step 8: Filter Your Task List

As your task list grows, filtering becomes essential:

```bash
# See only tasks that aren't done yet
python -m cli list -s todo

# See only urgent tasks
python -m cli list -p 4

# See overdue tasks (past their due date and not completed)
python -m cli list -o
```

**Important note:** You can only apply one filter at a time. If you pass both `-s` and `-p`, only the status filter will be used.

## Troubleshooting

### "Failed to update task status. Task not found."
Double-check the task ID. It must be the full UUID, not the shortened 8-character version.

### Tags not appearing
Make sure there are no spaces after the commas when creating tasks with `-t`. Use `"work,urgent"` not `"work, urgent"`.

### Due date not accepted
The date must be in `YYYY-MM-DD` format. Example: `2026-03-15` (not `03-15-2026` or `March 15`).

### Task still showing after marking as done
Done tasks are not automatically hidden. Use `python -m cli list -s todo` to see only active tasks.

---
---

## Prompt 3 Output: FAQ Document

---

# TaskManager CLI — Frequently Asked Questions

## Getting Started

### What is TaskManager CLI?
TaskManager CLI is a command-line to-do list application written in Python. It lets you create, organize, and track tasks directly from your terminal without needing a web browser or graphical interface.

### Do I need to install any packages?
No. TaskManager uses only Python's built-in standard library (json, datetime, uuid, enum, argparse). If you have Python 3.7 or higher, you're ready to go.

### How do I run it for the first time?
Navigate to the `python/` directory in your terminal and run:
```bash
python -m cli create "My first task"
```
This creates your first task and automatically creates a `tasks.json` file to store your data.

### Where are my tasks stored?
Tasks are saved in a file called `tasks.json` in whatever directory you run the CLI from. This is a plain text file in JSON format — you can even open it in a text editor to see your raw data.

---

## Task Management

### How do I create a task?
```bash
python -m cli create "Task title" -d "Description" -p 3 -u 2026-03-15 -t "tag1,tag2"
```
Only the title is required. Description, priority, due date, and tags are all optional.

### What are the priority levels?
There are four priority levels: 1 (Low), 2 (Medium), 3 (High), and 4 (Urgent). If you don't specify a priority, it defaults to 2 (Medium).

### How do I move a task through the workflow?
Update the status as you progress:
```bash
python -m cli status <task_id> in_progress   # Started working
python -m cli status <task_id> review         # Ready for review
python -m cli status <task_id> done           # Completed
```

### Can I change a task's priority after creating it?
Yes:
```bash
python -m cli priority <task_id> 4
```
This changes the task to URGENT priority.

### Can I change a task's due date?
Yes:
```bash
python -m cli due <task_id> 2026-04-01
```

### How do I delete a task?
```bash
python -m cli delete <task_id>
```
Warning: This is permanent. There is no undo or recycle bin.

### What does "overdue" mean?
A task is overdue if its due date has passed AND it is not marked as done. Tasks with no due date can never be overdue.

---

## Tags and Filtering

### How do tags work?
Tags are labels you attach to tasks for categorization. A task can have multiple tags. Add them at creation with `-t "tag1,tag2"` or add them later:
```bash
python -m cli tag <task_id> tagname
```

### How do I remove a tag?
```bash
python -m cli untag <task_id> tagname
```

### Can I filter tasks by tag?
Not directly with the current CLI. You can filter by status (`-s`), priority (`-p`), or overdue status (`-o`), but tag-based filtering is not yet implemented. You could search the `tasks.json` file manually or use `grep` on the command line.

### Can I combine multiple filters?
No. The current version only supports one filter at a time. If you pass both a status and priority filter, only the status filter will be applied. This is a known limitation.

---

## Data and Storage

### What happens if I delete `tasks.json`?
All your tasks will be lost. There is no backup system built in. Consider copying `tasks.json` to a safe location periodically if your data is important.

### Can I edit `tasks.json` directly?
Technically yes — it's a plain JSON file. However, be careful with the format. If the JSON becomes malformed (e.g., a missing comma or bracket), the application will fail to load your tasks. Always make a backup before manually editing.

### Can I use a different storage location?
Not from the command line directly, but you can modify the code. In `cli.py`, the `TaskManager()` is created with a default path. You can change it to:
```python
task_manager = TaskManager(storage_path="/path/to/my/tasks.json")
```

### Is there a way to export my tasks?
There's no built-in export command, but since tasks are stored as a JSON file, you already have your data in a portable format. You can open `tasks.json` with any text editor or use it with other tools that accept JSON.

---

## Troubleshooting

### I get "ModuleNotFoundError" when running the CLI
Make sure you're running the command from inside the `python/` directory. The imports use relative paths (e.g., `from .models import Task`), which require you to be in the correct directory.

### My task ID doesn't work
Task IDs are full UUIDs like `a1b2c3d4-e5f6-7890-abcd-ef1234567890`. The list view only shows the first 8 characters. You need the full ID for all commands. Run `python -m cli list` and look for the complete ID, or open `tasks.json` to find it.

### The date format isn't accepted
Due dates must be in `YYYY-MM-DD` format (e.g., `2026-03-15`). Formats like `03/15/2026`, `March 15`, or `15-03-2026` will not work.

### I accidentally marked a task as done — can I undo it?
Yes, you can change the status back:
```bash
python -m cli status <task_id> in_progress
```
However, note that the `completed_at` timestamp will remain set from the original completion. This is a minor limitation — it won't affect functionality but the completion timestamp will be inaccurate.

### Tasks from a previous session are gone
You're probably running the CLI from a different directory. Each directory gets its own `tasks.json`. Navigate to the directory where you originally created the tasks.

---

## Reflection

### Which aspects of the project were most challenging to document?

The **task ID handling** was the trickiest to document clearly. The CLI shows a shortened 8-character ID in list output, but all commands require the full UUID. This is a common source of confusion for new users and needed careful explanation in multiple sections (README, guide, and FAQ) to make sure users understand the difference.

### How did I adjust prompts to get better results?

Including the **actual code structure and commands** in the prompt produced much better documentation than a vague description. Specifically, providing the argparse command definitions from `cli.py` allowed the AI to generate accurate usage examples with the correct flags and parameter names. Mentioning the target audience as "beginners" also shifted the tone from technical jargon to plain explanations.

### What I learned about document structure and organization

Different documentation types serve different purposes and should be structured accordingly. The README is a reference guide — users scan it to find what they need. The step-by-step guide is a narrative — users follow it from start to finish. The FAQ is reactive — users search it when they hit a specific problem. Good documentation provides all three because users have different needs at different times.

### How I would incorporate this into my development workflow

I would create the README at the start of a project (not the end) and update it as features are added. The step-by-step guide should be written after the first stable version is complete. The FAQ should be a living document that grows as real users ask real questions. Using AI to generate initial drafts saves significant time, but every section should be reviewed against the actual code behavior before publishing.
