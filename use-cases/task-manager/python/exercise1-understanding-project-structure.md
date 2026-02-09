# Exercise 1: Understanding Project Structure

## Task Manager Python Codebase Analysis

---

## 1. Initial Understanding (Before AI Assistance)

Before analyzing the codebase in detail, here is what I could observe from the directory structure and file names alone:

### What the Application Does

The project appears to be a command-line Task Manager application — a to-do list that users interact with by typing commands in a terminal. It lets users create, update, delete, and track tasks.

### Technologies Identified

- **Python 3** (primary language examined)
- **Standard library modules only**: json, os, datetime, uuid, enum, argparse
- Also available in JavaScript and Java versions

### Folder Structure Pattern

The codebase follows a **layered architecture pattern**, where each file has a single responsibility and they build on top of each other: models → storage → app → CLI.

---

## 2. Final Understanding (After AI-Assisted Analysis)

### Project Structure Breakdown

| File | Role | Key Concepts |
|------|------|-------------|
| **models.py** | Defines what a Task is — its properties and behaviors. Like a blueprint or template. | Classes, Enums (fixed categories like LOW/MEDIUM/HIGH), `__init__` constructor, methods |
| **storage.py** | Saves and loads tasks to/from a JSON file. Handles data persistence so tasks survive between sessions. | JSON encoding/decoding, file I/O, dictionary storage, custom encoder/decoder classes |
| **app.py** | The brain of the application. Contains all the operations: create, list, update, delete tasks, and statistics. | Application logic, TaskManager class, filtering, date parsing, tag management |
| **cli.py** | The user interface. Reads commands from the terminal and passes them to app.py. This is where the program starts. | argparse (command parsing), `__name__ == '__main__'` entry point, formatting output |

### Entry Points

- **Primary entry point:** `cli.py`, line 163 — `if __name__ == "__main__": main()`. This is the line Python executes first when you run the program.
- **Application logic entry point:** `app.py` — The TaskManager class is the central coordinator. cli.py creates a TaskManager instance, which in turn creates TaskStorage, which loads saved tasks.

### Architectural Pattern

The project uses a layered architecture where each layer only communicates with the layer directly below it:

1. **CLI Layer (cli.py)** — User interaction and display formatting
2. **Application Layer (app.py)** — Business logic and operations
3. **Storage Layer (storage.py)** — Data persistence (saving/loading)
4. **Model Layer (models.py)** — Data structures and definitions

---

## 3. Misconceptions Corrected

- **Initially assumed the project might use external packages or a database.** In reality, it uses only Python's built-in standard library and stores data in a simple JSON file — no database, no pip install required.

- **Thought app.py might be the entry point.** The actual entry point is cli.py (the `if __name__ == "__main__"` block). app.py is the logic layer, but cli.py is what you actually run.

- **Didn't realize there were 3 language versions.** The same Task Manager exists in Python, JavaScript, and Java — the architecture is almost identical across all three.

---

## 4. Key Components and Responsibilities

### Task (models.py)
The core data object. Each task has an auto-generated ID, title, description, priority (LOW/MEDIUM/HIGH/URGENT), status (TODO/IN_PROGRESS/REVIEW/DONE), creation and update timestamps, an optional due date, and tags. It also has methods like `mark_as_done()` and `is_overdue()`.

### TaskStorage (storage.py)
Manages persistence using a JSON file. Provides CRUD operations (Create, Read, Update, Delete) and filtering methods. Includes custom JSON encoder/decoder to handle Python objects like datetime and Enum values that JSON doesn't natively support.

### TaskManager (app.py)
The central business logic class. Wraps TaskStorage with higher-level operations like creating tasks with validation, filtering by status/priority/overdue, managing tags, and generating statistics.

### CLI Interface (cli.py)
Uses Python's argparse module to define commands (create, list, status, priority, due, tag, untag, show, delete, stats). Formats task output with visual symbols for status and priority. This is the only file the user directly interacts with.

---

## 5. Questions to Ask the Team

1. Is there a reason JSON was chosen over a database like SQLite for storage? Are there plans to scale this?
2. Is the Task Manager intended to be used by a single user, or will it need multi-user support?
3. Why does the project exist in three languages — is each version used in production, or is it for educational purposes?
4. Are there any plans to add a web or GUI interface on top of the CLI?
5. What testing strategy is in place? I don't see test files — is testing planned?

---

## 6. Exploration Exercise Completed

To verify my understanding, I traced a complete operation through all four layers. When a user types a command like `python cli.py create "Buy groceries" -p 3`, the flow is:

1. **cli.py** parses the command using argparse, extracting the title and priority
2. **cli.py** calls `task_manager.create_task()` in **app.py**
3. **app.py** converts the priority number to a TaskPriority enum, creates a Task object using the blueprint in **models.py**
4. **app.py** passes the task to **storage.py** which saves it to tasks.json
5. **cli.py** prints the confirmation message with the new task ID

This confirmed that the layered architecture flows in one direction: CLI → App → Storage → Models, which matches my understanding of the project structure.
