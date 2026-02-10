"""
Background task functions for the blog API.

WHAT ARE BACKGROUND TASKS?
    Operations that run AFTER the response is sent to the client.
    The client doesn't wait — they get their response immediately,
    and the server does the extra work afterward.

    From the FastAPI docs: "This is useful for operations that need
    to happen after a request, but that the client doesn't really
    have to be waiting for the operation to complete."

WHEN TO USE THEM:
    ✅ Sending email notifications (slow network call)
    ✅ Writing to log files
    ✅ Updating analytics/counters
    ✅ Processing uploaded files
    ✅ Triggering webhooks

WHEN NOT TO USE THEM:
    ❌ Heavy computation (use Celery + Redis instead)
    ❌ Tasks that need retry logic
    ❌ Tasks that need progress tracking
    ❌ Tasks that must complete (background tasks can be lost on restart)

HOW THEY WORK:
    1. Your endpoint adds a task: background_tasks.add_task(func, arg1, arg2)
    2. FastAPI sends the response to the client
    3. AFTER the response is sent, FastAPI runs the task function
    4. The task runs in the same process (not a separate worker)

    It's like a restaurant: the waiter (endpoint) takes your order,
    brings your food (response), and THEN goes to restock the napkins
    (background task). You don't wait for the restocking.
"""

import time
from datetime import datetime
from typing import List


# In-memory notification log (in production, this would be a database or log service)
notification_log: List[dict] = []


def send_new_post_notification(post_title: str, author: str):
    """
    Simulate sending a notification when a new post is published.

    In a real app, this would:
    - Send an email to subscribers
    - Push to a notification service
    - Post to a Slack channel
    - Fire a webhook

    The time.sleep() simulates a slow network call (like sending an email).
    The key point: the API response has ALREADY been sent to the client
    by the time this function runs.
    """
    time.sleep(0.1)  # Simulate slow operation (email, webhook, etc.)

    notification_log.append({
        "event": "new_post",
        "message": f"New post '{post_title}' by {author}",
        "timestamp": datetime.utcnow().isoformat(),
    })


def send_new_comment_notification(post_title: str, comment_author: str):
    """Simulate notifying the post author about a new comment."""
    time.sleep(0.1)

    notification_log.append({
        "event": "new_comment",
        "message": f"{comment_author} commented on '{post_title}'",
        "timestamp": datetime.utcnow().isoformat(),
    })


def log_search_query(query: str, result_count: int):
    """
    Log search queries for analytics (background task).

    This is a perfect background task example: the user gets their
    search results immediately, and the analytics logging happens
    after. The user never waits for the log write.
    """
    notification_log.append({
        "event": "search",
        "message": f"Search for '{query}' returned {result_count} results",
        "timestamp": datetime.utcnow().isoformat(),
    })


def get_notification_log() -> List[dict]:
    """Return the notification log (for demonstration purposes)."""
    return notification_log
