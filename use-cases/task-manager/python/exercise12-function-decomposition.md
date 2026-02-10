# Exercise 12: Function Decomposition Challenge

## Function Chosen: Report Generation Function (Python)

---

## 1. The Original Function

```python
def generate_sales_report(sales_data, report_type='summary', date_range=None,
                         filters=None, grouping=None, include_charts=False,
                         output_format='pdf'):
    # ~170 lines of mixed validation, filtering, calculation,
    # grouping, forecasting, charting, and output formatting
    ...
```

This function is **~170 lines long** with **7 parameters**. It's a prime candidate for decomposition.

---

## 2. Prompt 1: Responsibility Analysis

### Prompt Used

> I have a complex function that I'd like to refactor by breaking it down into smaller functions.
>
> [Pasted the full generate_sales_report function]
>
> Please:
> 1. Identify the distinct responsibilities/concerns in this function
> 2. Suggest a decomposition strategy with smaller functions
> 3. Show which parts of the original code would move to each new function
> 4. Provide a refactored version with the main function delegating to the smaller functions

### Responsibilities Identified

The AI identified **8 distinct responsibilities** packed into one function:

| # | Responsibility | Lines (approx) | Description |
|---|---------------|-----------------|-------------|
| 1 | **Input validation** | 1–10 | Checking that parameters are valid types and values |
| 2 | **Date range filtering** | 11–25 | Parsing dates and filtering sales within the range |
| 3 | **Additional filtering** | 26–32 | Applying key-value filters to narrow the data |
| 4 | **Basic metrics calculation** | 33–38 | Computing totals, averages, min, max |
| 5 | **Data grouping** | 39–55 | Grouping sales by product/category/region and calculating group stats |
| 6 | **Detailed transaction processing** | 56–70 | Adding calculated fields like profit and margin to each transaction |
| 7 | **Forecast generation** | 71–115 | Calculating monthly trends, growth rates, and projections |
| 8 | **Chart data preparation** | 116–140 | Structuring data for time-series and pie charts |
| 9 | **Output formatting** | 141–150 | Routing to PDF/HTML/Excel/JSON generators |

**Why this is a problem:** If you need to change how forecasts are calculated, you have to scroll through 170 lines to find the relevant 40 lines, mentally filtering out everything else. If you want to test the grouping logic, you can't — it's buried inside a function that also validates, filters, calculates, forecasts, and formats.

### The "Parameter Bloat" Red Flag

The function takes **7 parameters**:

```python
def generate_sales_report(sales_data, report_type, date_range, filters,
                         grouping, include_charts, output_format)
```

This is a warning sign. When a function needs this many parameters, it's usually because it's doing too many different things — each parameter controls a different responsibility.

---

## 3. Prompt 2: Single-Responsibility Extraction

### Prompt Used

> I'd like to extract a single responsibility from this complex function.
>
> Specifically, I want to extract the logic that handles: **forecast generation**
>
> [Pasted the function]

### Extracting the Forecast Logic

The forecast section is the most complex chunk (~45 lines). Here's what it does, step by step:

1. Groups all sales by month
2. Sorts months chronologically
3. Calculates the growth rate between each consecutive month
4. Averages those growth rates
5. Projects the next 3 months using that average growth rate

#### Extracted Function

```python
def generate_forecast(sales_data, num_months=3):
    """
    Calculate sales trends and project future sales.

    Groups historical sales by month, calculates month-over-month
    growth rates, and projects future sales using the average growth rate.

    Args:
        sales_data: List of sale dictionaries, each with 'date' and 'amount'
        num_months: Number of months to forecast (default: 3)

    Returns:
        Dictionary with monthly_sales, growth_rates, average_growth_rate,
        and projected_sales
    """
    # Group sales by month
    monthly_sales = {}
    for sale in sales_data:
        sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
        month_key = f"{sale_date.year}-{sale_date.month:02d}"

        if month_key not in monthly_sales:
            monthly_sales[month_key] = 0
        monthly_sales[month_key] += sale['amount']

    # Calculate growth rates between consecutive months
    sorted_months = sorted(monthly_sales.keys())
    growth_rates = {}

    for i in range(1, len(sorted_months)):
        prev_month = sorted_months[i - 1]
        curr_month = sorted_months[i]
        prev_amount = monthly_sales[prev_month]
        curr_amount = monthly_sales[curr_month]

        if prev_amount > 0:
            rate = ((curr_amount - prev_amount) / prev_amount) * 100
            growth_rates[curr_month] = rate

    # Average growth rate
    avg_growth_rate = (
        sum(growth_rates.values()) / len(growth_rates)
        if growth_rates else 0
    )

    # Project future months
    projected_sales = {}
    if sorted_months:
        last_amount = monthly_sales[sorted_months[-1]]
        year, month = map(int, sorted_months[-1].split('-'))

        for _ in range(num_months):
            month += 1
            if month > 12:
                month = 1
                year += 1
            forecast_month = f"{year}-{month:02d}"
            last_amount = last_amount * (1 + avg_growth_rate / 100)
            projected_sales[forecast_month] = last_amount

    return {
        'monthly_sales': monthly_sales,
        'growth_rates': growth_rates,
        'average_growth_rate': avg_growth_rate,
        'projected_sales': projected_sales
    }
```

#### How the Original Function Changes

**Before:**
```python
# 45 lines of forecast logic inline
if report_type == 'forecast':
    monthly_sales = {}
    for sale in sales_data:
        # ... 40+ more lines ...
    report_data['forecast'] = { ... }
```

**After:**
```python
if report_type == 'forecast':
    report_data['forecast'] = generate_forecast(sales_data)
```

45 lines replaced by 1. The logic is preserved, but now it's:
- **Testable** — you can test `generate_forecast()` with sample data without touching the rest of the report
- **Reusable** — if another part of the app needs forecasting, it can call this function directly
- **Readable** — the main function now says "generate forecast" instead of showing you how

---

## 4. Prompt 3: Conditional Logic Simplification

### Prompt Used

> This function contains complex conditional logic that I want to simplify.
>
> [Pasted the function, highlighting the output format routing and report type branching]

### Conditionals Identified

The function has two layers of conditional branching:

**Layer 1 — Report type determines what data to include:**
```python
if report_type == 'detailed':
    # ... add transaction details
if report_type == 'forecast':
    # ... generate projections
```

**Layer 2 — Output format determines how to render:**
```python
if output_format == 'json':
    return report_data
elif output_format == 'html':
    return _generate_html_report(report_data)
elif output_format == 'excel':
    return _generate_excel_report(report_data)
elif output_format == 'pdf':
    return _generate_pdf_report(report_data)
```

### AI-Suggested Simplification: Dictionary Dispatch

Instead of a chain of `if/elif` statements, use a dictionary that maps format names to functions:

```python
def format_report(report_data, output_format, include_charts):
    """Route report data to the appropriate output formatter."""
    formatters = {
        'json': lambda data, charts: data,  # JSON just returns the data as-is
        'html': _generate_html_report,
        'excel': _generate_excel_report,
        'pdf': _generate_pdf_report,
    }

    formatter = formatters.get(output_format)
    if not formatter:
        raise ValueError(f"Unsupported output format: {output_format}")

    return formatter(report_data, include_charts)
```

**Python concept — dictionary dispatch:** Instead of checking conditions one by one (`if this, elif that, elif other`), you store the mapping in a dictionary and look up the right action directly. This is cleaner, easier to extend (just add a new key-value pair), and eliminates the risk of forgetting an `elif`.

**Adding a new format is one line:**
```python
# Before: Add another elif branch, risk forgetting it
# After:
formatters['csv'] = _generate_csv_report
```

---

## 5. Full Refactored Version

```python
from datetime import datetime


# ─── Validation ───────────────────────────────────────────────

def validate_report_params(sales_data, report_type, output_format, date_range):
    """Validate all input parameters before processing."""
    if not sales_data or not isinstance(sales_data, list):
        raise ValueError("Sales data must be a non-empty list")
    if report_type not in ('summary', 'detailed', 'forecast'):
        raise ValueError("Report type must be 'summary', 'detailed', or 'forecast'")
    if output_format not in ('pdf', 'excel', 'html', 'json'):
        raise ValueError("Output format must be 'pdf', 'excel', 'html', or 'json'")
    if date_range:
        if 'start' not in date_range or 'end' not in date_range:
            raise ValueError("Date range must include 'start' and 'end' dates")


# ─── Filtering ────────────────────────────────────────────────

def filter_by_date_range(sales_data, date_range):
    """Filter sales to only include those within the given date range."""
    if not date_range:
        return sales_data

    start = datetime.strptime(date_range['start'], '%Y-%m-%d')
    end = datetime.strptime(date_range['end'], '%Y-%m-%d')

    if start > end:
        raise ValueError("Start date cannot be after end date")

    return [
        sale for sale in sales_data
        if start <= datetime.strptime(sale['date'], '%Y-%m-%d') <= end
    ]


def apply_filters(sales_data, filters):
    """Apply key-value filters to narrow down sales data."""
    if not filters:
        return sales_data

    filtered = sales_data
    for key, value in filters.items():
        if isinstance(value, list):
            filtered = [s for s in filtered if s.get(key) in value]
        else:
            filtered = [s for s in filtered if s.get(key) == value]

    return filtered


# ─── Metrics ──────────────────────────────────────────────────

def calculate_summary_metrics(sales_data):
    """Calculate basic summary metrics from sales data."""
    total = sum(sale['amount'] for sale in sales_data)
    max_sale = max(sales_data, key=lambda x: x['amount'])
    min_sale = min(sales_data, key=lambda x: x['amount'])

    return {
        'total_sales': total,
        'transaction_count': len(sales_data),
        'average_sale': total / len(sales_data),
        'max_sale': {
            'amount': max_sale['amount'],
            'date': max_sale['date'],
            'details': max_sale
        },
        'min_sale': {
            'amount': min_sale['amount'],
            'date': min_sale['date'],
            'details': min_sale
        }
    }


# ─── Grouping ─────────────────────────────────────────────────

def group_sales_data(sales_data, grouping, total_sales):
    """Group sales by a specified field and calculate group statistics."""
    if not grouping:
        return None

    groups = {}
    for sale in sales_data:
        key = sale.get(grouping, 'Unknown')
        if key not in groups:
            groups[key] = {'count': 0, 'total': 0, 'items': []}

        groups[key]['count'] += 1
        groups[key]['total'] += sale['amount']
        groups[key]['items'].append(sale)

    # Add calculated fields
    for key in groups:
        groups[key]['average'] = groups[key]['total'] / groups[key]['count']
        groups[key]['percentage'] = (groups[key]['total'] / total_sales) * 100

    return {'by': grouping, 'groups': groups}


# ─── Detailed Transactions ────────────────────────────────────

def enrich_transactions(sales_data):
    """Add calculated fields (profit, margin) to each transaction."""
    transactions = []
    for sale in sales_data:
        transaction = {k: v for k, v in sale.items()}

        if 'tax' in sale and 'amount' in sale:
            transaction['pre_tax'] = sale['amount'] - sale['tax']
        if 'cost' in sale and 'amount' in sale:
            transaction['profit'] = sale['amount'] - sale['cost']
            transaction['margin'] = (transaction['profit'] / sale['amount']) * 100

        transactions.append(transaction)

    return transactions


# ─── Forecasting ──────────────────────────────────────────────

def generate_forecast(sales_data, num_months=3):
    """Calculate monthly trends and project future sales."""
    monthly_sales = {}
    for sale in sales_data:
        sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
        month_key = f"{sale_date.year}-{sale_date.month:02d}"
        monthly_sales[month_key] = monthly_sales.get(month_key, 0) + sale['amount']

    sorted_months = sorted(monthly_sales.keys())
    growth_rates = {}

    for i in range(1, len(sorted_months)):
        prev = monthly_sales[sorted_months[i - 1]]
        curr = monthly_sales[sorted_months[i]]
        if prev > 0:
            growth_rates[sorted_months[i]] = ((curr - prev) / prev) * 100

    avg_growth = sum(growth_rates.values()) / len(growth_rates) if growth_rates else 0

    projected = {}
    if sorted_months:
        last_amount = monthly_sales[sorted_months[-1]]
        year, month = map(int, sorted_months[-1].split('-'))

        for _ in range(num_months):
            month += 1
            if month > 12:
                month = 1
                year += 1
            last_amount *= (1 + avg_growth / 100)
            projected[f"{year}-{month:02d}"] = last_amount

    return {
        'monthly_sales': monthly_sales,
        'growth_rates': growth_rates,
        'average_growth_rate': avg_growth,
        'projected_sales': projected
    }


# ─── Charts ───────────────────────────────────────────────────

def prepare_chart_data(sales_data, grouping, grouped_data):
    """Prepare data structures for chart rendering."""
    charts = {}

    # Sales over time
    date_sales = {}
    for sale in sales_data:
        date_sales[sale['date']] = date_sales.get(sale['date'], 0) + sale['amount']

    charts['sales_over_time'] = {
        'labels': sorted(date_sales.keys()),
        'data': [date_sales[d] for d in sorted(date_sales.keys())]
    }

    # Pie chart for grouping
    if grouping and grouped_data:
        groups = grouped_data['groups']
        charts[f'sales_by_{grouping}'] = {
            'labels': list(groups.keys()),
            'data': [g['total'] for g in groups.values()]
        }

    return charts


# ─── Output Formatting ────────────────────────────────────────

def format_report(report_data, output_format, include_charts):
    """Route report data to the appropriate output formatter."""
    formatters = {
        'json': lambda data, charts: data,
        'html': _generate_html_report,
        'excel': _generate_excel_report,
        'pdf': _generate_pdf_report,
    }
    return formatters[output_format](report_data, include_charts)


# ─── Main Function (Orchestrator) ─────────────────────────────

def generate_sales_report(sales_data, report_type='summary', date_range=None,
                         filters=None, grouping=None, include_charts=False,
                         output_format='pdf'):
    """
    Generate a sales report by orchestrating validation, filtering,
    calculation, and formatting steps.
    """
    # Step 1: Validate inputs
    validate_report_params(sales_data, report_type, output_format, date_range)

    # Step 2: Filter data
    data = filter_by_date_range(sales_data, date_range)
    data = apply_filters(data, filters)

    # Step 3: Handle empty results
    if not data:
        if output_format == 'json':
            return {"message": "No data matches the specified criteria", "data": []}
        return _generate_empty_report(report_type, output_format)

    # Step 4: Calculate metrics
    summary = calculate_summary_metrics(data)

    # Step 5: Build report
    report_data = {
        'report_type': report_type,
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_range': date_range,
        'filters': filters,
        'summary': summary,
    }

    # Step 6: Add optional sections
    grouped_data = group_sales_data(data, grouping, summary['total_sales'])
    if grouped_data:
        report_data['grouping'] = grouped_data

    if report_type == 'detailed':
        report_data['transactions'] = enrich_transactions(data)

    if report_type == 'forecast':
        report_data['forecast'] = generate_forecast(data)

    if include_charts:
        report_data['charts'] = prepare_chart_data(data, grouping, grouped_data)

    # Step 7: Format and return
    return format_report(report_data, output_format, include_charts)
```

---

## 6. Before vs. After Comparison

### Structure

| Aspect | Before | After |
|--------|--------|-------|
| Number of functions | 1 (+ 4 empty helpers) | 9 focused functions + 1 orchestrator |
| Longest function | ~170 lines | ~30 lines |
| Main function | Does everything | Delegates to specialists |
| Nesting depth | Up to 4 levels deep | Maximum 2 levels |
| Testability | Must test everything together | Each function testable in isolation |

### Reading the Main Function

**Before:** To understand what `generate_sales_report` does, you have to read 170 lines of mixed logic — validation tangled with filtering tangled with calculations tangled with formatting.

**After:** The main function reads like an outline:

```python
validate → filter → calculate metrics → build report → add sections → format
```

Each step is one function call with a clear name. You can understand the entire workflow without reading any implementation details.

### Testing

**Before:** To test forecast logic, you need to set up a full function call with valid parameters, date ranges, filters, and then extract the forecast section from the result.

**After:** To test forecast logic:
```python
def test_forecast_projects_three_months():
    sales = [
        {'date': '2025-01-15', 'amount': 100},
        {'date': '2025-02-15', 'amount': 120},
        {'date': '2025-03-15', 'amount': 144},
    ]
    result = generate_forecast(sales)
    assert len(result['projected_sales']) == 3
    assert result['average_growth_rate'] == 20.0  # 20% growth each month
```

Clean, focused, and tests exactly one thing.

### Adding New Features

**Before:** Want to add a new report type like "comparison"? You'd add another 30-line `if` block inside the already-170-line function.

**After:** Create a new function `generate_comparison_data(data)` and add one line to the main function:
```python
if report_type == 'comparison':
    report_data['comparison'] = generate_comparison_data(data)
```

---

## 7. Key Concepts Learned

### The Orchestrator Pattern

The refactored main function doesn't *do* any work — it *coordinates* work done by specialists. This is sometimes called the "orchestrator" or "coordinator" pattern. It reads like a recipe: "first validate, then filter, then calculate, then format." Each step is delegated to a specialist function.

**Analogy:** A restaurant head chef doesn't cook every dish. They coordinate: "you prepare the salad, you grill the steak, you plate the dessert." The head chef's job is sequencing and quality control, not doing everything.

### Levels of Abstraction

The original function mixed **high-level decisions** ("should we include a forecast?") with **low-level details** ("parse the date string, extract year and month, format as YYYY-MM"). Good code keeps these at separate levels:

- **High level (orchestrator):** `generate_forecast(data)` — tells you *what* happens
- **Low level (specialist):** The loop that parses dates and calculates growth rates — tells you *how* it happens

When reading the orchestrator, you shouldn't need to think about date parsing. When debugging the forecast calculation, you shouldn't need to think about chart generation.

### List Comprehensions Replace Manual Loops

The refactored filtering uses Python list comprehensions:

```python
# Before: Manual loop with append
filtered_data = []
for sale in sales_data:
    sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
    if start_date <= sale_date <= end_date:
        filtered_data.append(sale)

# After: List comprehension
return [
    sale for sale in sales_data
    if start <= datetime.strptime(sale['date'], '%Y-%m-%d') <= end
]
```

A **list comprehension** is Python's concise syntax for "build a new list by filtering/transforming another list." The pattern is:
```python
[expression for item in iterable if condition]
```

It does the same thing as the loop-and-append pattern but in one readable line.

### `.get()` with Default Values

```python
monthly_sales[month_key] = monthly_sales.get(month_key, 0) + sale['amount']
```

This replaces the two-line "check if key exists, then update" pattern:
```python
if month_key not in monthly_sales:
    monthly_sales[month_key] = 0
monthly_sales[month_key] += sale['amount']
```

`.get(key, default)` returns the value if the key exists, or the default if it doesn't. Combined with `+`, it handles both cases in one line.

---

## 8. Reflection

### How did breaking down the function improve readability and maintainability?

The biggest improvement is that the main function now tells a **story** — validate, filter, calculate, build, format. Before, it was like reading a novel where every chapter was crammed into one paragraph. Now each chapter (function) has a title, a clear purpose, and can be read independently.

### What was the most challenging part?

Deciding **where to draw the boundaries** between functions. The grouping logic and the chart data preparation both need access to grouped data — so which one should calculate it? The answer was to have `group_sales_data` return the data, and have both the main function and `prepare_chart_data` use that return value. Getting the data flow right between extracted functions requires careful thought about what each function needs as input and what it produces as output.

### Which extracted function is most reusable?

**`generate_forecast()`** is the most reusable. It takes a simple input (list of sales with dates and amounts), performs a self-contained calculation, and returns a structured result. It could be used for forecasting any time-series data — not just sales reports. A dashboard, an API endpoint, or a scheduled email could all call this function independently.

**`calculate_summary_metrics()`** is a close second — any view that needs totals, averages, and extremes from sales data can use it.
