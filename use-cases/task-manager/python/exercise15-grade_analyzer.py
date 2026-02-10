"""
Exercise 15, Activity 3: List Comprehension Practice
Grade analyzer using list comprehensions.
"""


def analyze_grades(students):
    """
    Analyze student grades using list comprehensions.

    Args:
        students: List of dicts with 'name', 'scores' (list of ints)

    Returns:
        Dict with analysis results
    """
    # Calculate average for each student (skip students with no scores)
    averages = [
        {'name': s['name'], 'average': sum(s['scores']) / len(s['scores'])}
        for s in students
        if s['scores']
    ]

    # Find passing students (average >= 60)
    passing = [s['name'] for s in averages if s['average'] >= 60]

    # Find failing students
    failing = [s['name'] for s in averages if s['average'] < 60]

    # Flatten all scores into one list (nested comprehension)
    all_scores = [score for s in students for score in s['scores']]

    # Find students who got at least one perfect score
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


# ─── Test It ─────────────────────────────────────────────────

if __name__ == '__main__':
    students = [
        {'name': 'Alice', 'scores': [85, 92, 78, 100]},
        {'name': 'Bob', 'scores': [55, 62, 48, 70]},
        {'name': 'Carol', 'scores': [95, 100, 88, 92]},
        {'name': 'Dave', 'scores': [42, 38, 55, 45]},
        {'name': 'Eve', 'scores': [75, 80, 72, 68]},
    ]

    result = analyze_grades(students)

    print("=== Grade Analysis ===\n")

    print("Student Averages:")
    for s in result['averages']:
        status = "PASS" if s['average'] >= 60 else "FAIL"
        print(f"  {s['name']}: {s['average']:.1f} ({status})")

    print(f"\nPassing: {', '.join(result['passing'])}")
    print(f"Failing: {', '.join(result['failing'])}")
    print(f"Perfect scorers: {', '.join(result['perfect_scorers'])}")
    print(f"Class average: {result['class_average']:.1f}")
    print(f"Highest score: {result['highest_score']}")
