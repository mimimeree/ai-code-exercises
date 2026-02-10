# Exercise 13: Code Readability Challenge

---

## Example 1: Cryptic Variable Names (JavaScript)

### Original Code

```javascript
function p(i, a, q) {
  let r = [];
  let t = 0;

  for (let j = 0; j < i.length; j++) {
    let c = i[j];
    let f = false;

    for (let k = 0; k < a.length; k++) {
      if (c.id === a[k].id) {
        f = true;
        if (a[k].q >= q) {
          r.push(c);
          t += c.p * q;
          a[k].q -= q;
        }
        break;
      }
    }

    if (!f) {
      console.log("Item " + c.id + " not available");
    }
  }

  return { s: r, t: t };
}
```

### What This Function Actually Does

This function **processes a shopping order against inventory**. It takes a list of requested items, checks if each one exists in inventory with enough stock, and if so, adds it to the successful orders list, calculates the total cost, and reduces the inventory count.

### Prompt Used

> Please improve the readability of this code by enhancing variable and function names.
> Guidelines: Replace single-letter or cryptic variable names with descriptive ones, ensure function names clearly describe their purpose, use consistent naming conventions, preserve functionality exactly.

### Refactored Code

```javascript
/**
 * Process requested items against available inventory.
 * For each requested item, checks if it exists in inventory with
 * sufficient quantity. If so, adds it to fulfilled items and
 * deducts from inventory.
 *
 * @param {Array} requestedItems - Items to order, each with id and p (price)
 * @param {Array} inventory - Available stock, each with id and q (quantity)
 * @param {number} quantityPerItem - How many of each item to order
 * @returns {Object} - { fulfilledItems: Array, totalCost: number }
 */
function processInventoryOrder(requestedItems, inventory, quantityPerItem) {
  const fulfilledItems = [];
  let totalCost = 0;

  for (const requestedItem of requestedItems) {
    let foundInInventory = false;

    for (const stockItem of inventory) {
      if (requestedItem.id === stockItem.id) {
        foundInInventory = true;

        if (stockItem.q >= quantityPerItem) {
          fulfilledItems.push(requestedItem);
          totalCost += requestedItem.p * quantityPerItem;
          stockItem.q -= quantityPerItem;
        }
        break;
      }
    }

    if (!foundInInventory) {
      console.log("Item " + requestedItem.id + " not available");
    }
  }

  return {
    s: fulfilledItems,
    t: totalCost
  };
}
```

**Note:** The return object keys (`s` and `t`) are kept unchanged because the unit tests check for `result.s` and `result.t`. In a real refactoring, you'd rename these to `fulfilledItems` and `totalCost` and update the tests simultaneously.

### Name Changes Explained

| Original | Renamed To | Why |
|----------|-----------|-----|
| `p()` | `processInventoryOrder()` | Describes the action: processing an order against inventory |
| `i` | `requestedItems` | These are the items someone wants to buy |
| `a` | `inventory` | This is the available stock |
| `q` | `quantityPerItem` | How many of each item to order |
| `r` | `fulfilledItems` | Items that were successfully ordered |
| `t` | `totalCost` | Running total of the cost |
| `c` | `requestedItem` | The current item being processed |
| `f` | `foundInInventory` | Boolean flag: was this item found in stock? |
| `j`, `k` | eliminated | Replaced with `for...of` loops which don't need index variables |

### Readability Issues the AI Caught That I Might Have Missed

The AI suggested replacing traditional `for` loops with `for...of` loops. The original code used `for (let j = 0; j < i.length; j++)` with index-based access (`i[j]`). Since we never actually need the index number, `for (const item of items)` is cleaner and eliminates the index variables entirely.

---

## Example 2: Missing Documentation (Python)

### Original Code

```python
def calculate(principal, rate, time, additional=0, frequency=12):
    result = principal
    rate_per_period = rate / 100 / frequency
    total_periods = time * frequency

    for period in range(1, total_periods + 1):
        interest = result * rate_per_period
        result += interest
        if period % frequency == 0 and period < total_periods:
            result += additional

    return {
        "final_amount": round(result, 2),
        "interest_earned": round(result - principal - (additional * (time - 1)), 2),
        "total_contributions": principal + (additional * (time - 1))
    }
```

### Prompt Used

> I need to improve this code's readability by adding appropriate comments and documentation.
> Please: Add a clear function description, add comments for complex sections, document assumptions and edge cases, explain the business rules, don't add obvious comments.

### Refactored Code

```python
def calculate_compound_interest(principal, annual_rate, years,
                                annual_contribution=0, compounding_frequency=12):
    """
    Calculate compound interest with optional annual contributions.

    Simulates the growth of an investment over time, compounding at a
    specified frequency (default: monthly). Additional contributions are
    added once per year at the end of each year (except the final year).

    Args:
        principal (float): Initial investment amount in dollars.
        annual_rate (float): Annual interest rate as a percentage (e.g., 5 for 5%).
        years (int): Number of years to grow the investment.
        annual_contribution (float): Amount added at the end of each year
            (default: 0). Not added in the final year.
        compounding_frequency (int): How many times per year interest
            compounds (default: 12 for monthly). Use 4 for quarterly,
            1 for annually.

    Returns:
        dict: {
            "final_amount": Total value after all compounding and contributions,
            "interest_earned": Total interest gained (excludes contributions),
            "total_contributions": Principal plus all additional contributions
        }

    Example:
        >>> calculate_compound_interest(1000, 5, 1)
        {'final_amount': 1051.16, 'interest_earned': 51.16, 'total_contributions': 1000}

    Assumptions:
        - Interest compounds at regular intervals (e.g., every month for monthly)
        - Additional contributions are added at the END of each year
        - No contribution is added in the final year
        - All monetary values are in the same currency
    """
    balance = principal

    # Convert annual percentage rate to per-period decimal rate
    # e.g., 5% annual with monthly compounding = 0.05 / 12 = 0.004167 per month
    rate_per_period = annual_rate / 100 / compounding_frequency

    total_periods = years * compounding_frequency

    for period in range(1, total_periods + 1):
        # Apply compound interest for this period
        interest = balance * rate_per_period
        balance += interest

        # Add annual contribution at the end of each year (except the last year)
        # period % frequency == 0 means we've completed a full year
        # period < total_periods ensures we don't add in the final year
        is_year_boundary = (period % compounding_frequency == 0)
        is_not_final_year = (period < total_periods)

        if is_year_boundary and is_not_final_year:
            balance += annual_contribution

    # Calculate how many contributions were made (one per year except the last)
    number_of_contributions = years - 1 if years > 0 else 0
    total_contributed = principal + (annual_contribution * number_of_contributions)

    return {
        "final_amount": round(balance, 2),
        "interest_earned": round(balance - total_contributed, 2),
        "total_contributions": total_contributed
    }
```

### What Changed and Why

| Change | Before | After | Why |
|--------|--------|-------|-----|
| Function name | `calculate` | `calculate_compound_interest` | "Calculate" is vague — calculate what? |
| `rate` | `rate` | `annual_rate` | Clarifies it's annual, not per-period |
| `time` | `time` | `years` | "Time" could mean anything — seconds? days? |
| `additional` | `additional` | `annual_contribution` | Clarifies both the amount and when it's applied |
| `frequency` | `frequency` | `compounding_frequency` | Distinguishes from other possible frequencies |
| `result` | `result` | `balance` | Financial term — the running balance of the investment |
| Complex condition | `if period % frequency == 0 and period < total_periods` | Extracted to `is_year_boundary` and `is_not_final_year` | The condition is now self-documenting |
| Docstring | None | Full docstring with Args, Returns, Example, Assumptions | Anyone can understand the function without reading the code |

### Readability Issue the AI Caught

The complex conditional `period % frequency == 0 and period < total_periods` was hard to understand because it combines two business rules in one line. By extracting each condition into a named boolean variable, the intent becomes clear: "is this the end of a year AND is it not the final year?" This is the **"extract to named variable"** technique — one of the most effective readability improvements you can make.

---

## Example 3: Complex Algorithm Without Comments (Java)

### Original Code

```java
public static void sortItems(int[] array) {
    int n = array.length;
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (array[j] < array[min_idx]) {
                min_idx = j;
            }
        }
        int temp = array[min_idx];
        array[min_idx] = array[i];
        array[i] = temp;
    }
}
```

### Prompt Used

> I need to improve this code's readability by adding appropriate comments and documentation.
> Please explain: what algorithm this is, how it works conceptually, what each section does, and its time complexity.

### Refactored Code

```java
/**
 * Sort an integer array in ascending order using the Selection Sort algorithm.
 *
 * <p><b>How Selection Sort works:</b> Divide the array into a "sorted" region
 * (left side) and an "unsorted" region (right side). Repeatedly find the
 * smallest element in the unsorted region and swap it into the next position
 * in the sorted region. Each pass grows the sorted region by one element.</p>
 *
 * <p><b>Time complexity:</b> O(n²) in all cases (best, average, worst).
 * Always performs n(n-1)/2 comparisons regardless of input order.</p>
 *
 * <p><b>Space complexity:</b> O(1) — sorts in-place using only one temp variable.</p>
 *
 * <p><b>When to use:</b> Small arrays or when memory is extremely limited.
 * For larger arrays, prefer Arrays.sort() which uses a more efficient algorithm.</p>
 *
 * @param array The array to sort in-place. Modified directly.
 */
public static void selectionSort(int[] array) {
    int length = array.length;

    // Each iteration places the next-smallest element into position i.
    // After i passes, the first i elements are in their final sorted positions.
    for (int sortedBoundary = 0; sortedBoundary < length - 1; sortedBoundary++) {

        // Assume the element at the sorted boundary is the smallest remaining
        int indexOfSmallest = sortedBoundary;

        // Scan the unsorted region to find the actual smallest element
        for (int scanIndex = sortedBoundary + 1; scanIndex < length; scanIndex++) {
            if (array[scanIndex] < array[indexOfSmallest]) {
                indexOfSmallest = scanIndex;
            }
        }

        // Swap the smallest found element into its correct sorted position
        int temporary = array[indexOfSmallest];
        array[indexOfSmallest] = array[sortedBoundary];
        array[sortedBoundary] = temporary;
    }
}
```

### What Changed and Why

| Change | Before | After | Why |
|--------|--------|-------|-----|
| Method name | `sortItems` | `selectionSort` | Names the specific algorithm — critical for anyone choosing between sort methods |
| `n` | `n` | `length` | More descriptive; `n` is a math convention, `length` is a code convention |
| `i` | `i` | `sortedBoundary` | Describes its role: the boundary between sorted and unsorted regions |
| `min_idx` | `min_idx` | `indexOfSmallest` | camelCase (Java convention) and more descriptive |
| `j` | `j` | `scanIndex` | Describes what it does: scans the unsorted region |
| `temp` | `temp` | `temporary` | Slightly more explicit, though `temp` is widely understood in swap patterns |
| Javadoc | None | Full documentation | Explains the algorithm, complexity, and when to use it |
| Inline comments | None | Comments explaining each phase | Maps code sections to the algorithm's conceptual steps |

### Algorithm Explanation (What I Learned)

**Selection Sort** works like picking players for a team:

1. Look at everyone still unpicked (the unsorted region)
2. Find the best player (smallest number)
3. Put them next in line (swap to the front of the unsorted region)
4. Repeat until everyone is picked

The "sorted boundary" moves one position to the right after each pass. Everything to the left of it is in its final position.

**Why O(n²):** For an array of 5 elements, the first pass scans 4 elements, the second scans 3, the third scans 2, the last scans 1. Total comparisons: 4 + 3 + 2 + 1 = 10. For n elements: n(n-1)/2. That's proportional to n², hence O(n²).

### AI Issue I Noticed

The variable `min_idx` used snake_case, which is Python convention. In Java, it should be camelCase: `minIdx` or better, `indexOfSmallest`. This style inconsistency is a subtle readability issue — mixed conventions make the reader unsure which language's rules apply.

---

## Example 4: Poor Formatting and Structure (Python)

### Original Code

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

> Please improve the readability of this code by enhancing its structure and formatting.
> Specifically: apply consistent indentation and spacing, break up long expressions, extract complex conditions, reduce nesting, replace magic numbers with named constants, ensure functionality remains exactly the same.

### Refactored Code

```python
# Discount rates for loyalty tiers
VIP_DISCOUNT_RATE = 0.05          # 5% discount for VIP members
MEMBER_DISCOUNT_RATE = 0.02       # 2% discount for long-standing members
MEMBER_MONTHS_THRESHOLD = 6       # Months of membership required for member discount


def calculate_cart_total(cart):
    """Calculate the total price of all items in the cart."""
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return total


def apply_promotion(promo, cart_total):
    """
    Calculate the discount value for a single promotion.
    Returns the discount amount, or 0 if the promotion doesn't apply.
    """
    # Check if minimum purchase requirement is met
    min_purchase = promo.get('min_purchase')
    if min_purchase is not None and cart_total < min_purchase:
        return 0

    if promo['type'] == 'percent':
        return cart_total * promo['value'] / 100

    elif promo['type'] == 'fixed':
        # Fixed discount can't exceed the cart total
        return min(promo['value'], cart_total)

    return 0


def apply_loyalty_discount(cart_total, user_status, membership_months):
    """Calculate loyalty-based discount for VIP or long-standing members."""
    if user_status == 'vip':
        return cart_total * VIP_DISCOUNT_RATE

    if user_status == 'member' and membership_months > MEMBER_MONTHS_THRESHOLD:
        return cart_total * MEMBER_DISCOUNT_RATE

    return 0


def check_free_shipping(promos, cart_total):
    """Check if any shipping promotion qualifies for free shipping."""
    for promo in promos:
        if promo['type'] == 'shipping' and cart_total >= promo['min_purchase']:
            return True
    return False


def discount(cart, promos, user):
    """
    Calculate the best available discount for a shopping cart.

    Evaluates promotional discounts, loyalty discounts, and shipping
    promotions. Only the single highest discount is applied (they don't stack).

    Args:
        cart: List of items, each with 'price' and 'quantity'
        promos: List of promotions, each with 'type', 'value', 'min_purchase'
        user: Dict with 'status' (regular/member/vip) and 'months' (membership length)

    Returns:
        Dict with 'original', 'discount', 'final', and 'free_shipping'
    """
    cart_total = calculate_cart_total(cart)

    # Find the best promotional discount (highest value wins)
    best_discount = 0
    for promo in promos:
        promo_discount = apply_promotion(promo, cart_total)
        best_discount = max(best_discount, promo_discount)

    # Check loyalty discount and keep whichever is higher
    loyalty_discount = apply_loyalty_discount(
        cart_total, user['status'], user.get('months', 0)
    )
    best_discount = max(best_discount, loyalty_discount)

    # Check for free shipping (handled separately from price discounts)
    free_shipping = check_free_shipping(promos, cart_total)
    if free_shipping:
        user['free_shipping'] = True

    return {
        'original': cart_total,
        'discount': best_discount,
        'final': cart_total - best_discount,
        'free_shipping': user.get('free_shipping', False)
    }
```

### What Changed and Why

| Problem | Before | After | Impact |
|---------|--------|-------|--------|
| **Everything on one line** | `d=0;tot=0` and entire `if` blocks crammed into single lines | Each statement on its own line with proper indentation | Can actually read the code |
| **Cryptic names** | `d`, `tot`, `i`, `p`, `val`, `vd` | `best_discount`, `cart_total`, `item`, `promo`, `promo_discount`, `loyalty_discount` | Self-documenting |
| **Magic numbers** | `0.05`, `0.02`, `6` | `VIP_DISCOUNT_RATE`, `MEMBER_DISCOUNT_RATE`, `MEMBER_MONTHS_THRESHOLD` | Change the rate in one place, not hunting through code |
| **One giant function** | Everything in `discount()` | Split into `calculate_cart_total()`, `apply_promotion()`, `apply_loyalty_discount()`, `check_free_shipping()` | Each piece testable and reusable |
| **No spacing** | `cart,promos,user` and `d=0;tot=0` | Proper spaces around operators and after commas | Follows PEP 8 (Python's style guide) |
| **No documentation** | None | Docstrings on every function | Purpose and behavior are clear |
| **Hidden business rule** | Buried in dense code | Documented: "only the highest discount applies, they don't stack" | Critical business logic is visible |
| **Side effect** | `user['free_shipping']=True` hidden in a loop | `check_free_shipping()` returns a boolean, side effect is explicit | The modification of `user` is visible and intentional |

### Readability Issues the AI Caught That I Missed

1. **Free shipping is a side effect** — The original code silently modifies the `user` dictionary (`user['free_shipping'] = True`) inside what looks like a discount calculation loop. This is dangerous because the caller might not expect their `user` object to be modified. The refactored version makes this explicit.

2. **The "best discount" logic** — It wasn't obvious that the function keeps the HIGHEST discount rather than stacking them. In the dense original code, `d = max(d, val)` appears multiple times but the pattern (competitive discounts, not cumulative) is hidden. The refactored version makes this a clear, documented business rule.

3. **`min(p['value'], tot)` for fixed discounts** — This prevents a $50 fixed discount from applying to a $30 cart (which would give a negative total). An important business rule hidden in a dense line.

---

## Reflection

### How much easier is the code to understand now?

Dramatically easier. The Python discount function went from "unreadable puzzle" to "clear business logic in about 30 seconds of reading." The biggest impact came from proper formatting and descriptive names — those two changes alone made the code understandable before any restructuring.

### Which readability improvements had the biggest impact?

1. **Descriptive variable names** — Changed everything. `d=0;tot=0` tells you nothing. `best_discount = 0` and `cart_total = 0` tell you exactly what's happening.
2. **One statement per line** — The original Python code crammed entire if-blocks onto single lines. Simply putting each statement on its own line was transformative.
3. **Extracting named constants** — `VIP_DISCOUNT_RATE = 0.05` is infinitely clearer than a bare `0.05` floating in code.

### What readability issues did the AI miss?

The AI didn't flag that the **original function signature `discount(cart, promos, user)` is preserved** for test compatibility, but ideally it would be renamed to `calculate_best_discount()` to match the naming improvements elsewhere. It also didn't mention that the `user` dictionary mutation (setting `free_shipping`) is an architectural smell — the function should probably return the free shipping status rather than modifying the input.

### What patterns can I apply to future code?

1. **Name things for humans** — If you can't understand a variable's purpose from its name, rename it immediately
2. **One thought per line** — Never use semicolons to cram multiple statements together
3. **Extract magic numbers** — Any literal number that isn't 0 or 1 probably deserves a named constant
4. **Extract complex conditions** — `is_year_boundary and is_not_final_year` beats `period % frequency == 0 and period < total_periods`
5. **Use `for...of` / `for...in`** — When you don't need the index, don't create one
