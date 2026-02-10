# Exercise 11: Understanding What to Change with AI

---

## Exercise 1: Code Readability Improvement (Java)

### The Original Code

```java
class UserMgr {
    private List<U> u_list;
    private DBConn db;

    public UserMgr(DBConn d) {
        db = d;
        u_list = new ArrayList<>();
    }

    public boolean a(String un, String pw, String em) {
        if (un.length() < 3 || pw.length() < 8 || !em.contains("@")) {
            return false;
        }

        for (U user : u_list) {
            if (user.getUn().equals(un)) {
                return false;
            }
        }

        U nu = new U(un, pw, em);
        u_list.add(nu);
        boolean res = db.execute("INSERT INTO users VALUES ('" + un + "', '" + pw + "', '" + em + "')");
        return res;
    }

    public U f(String un) {
        for (U user : u_list) {
            if (user.getUn().equals(un)) {
                return user;
            }
        }
        return null;
    }
}

class U {
    private String un;
    private String pw;
    private String em;

    public U(String un, String pw, String em) {
        this.un = un;
        this.pw = pw;
        this.em = em;
    }

    public String getUn() { return un; }
    public String getPw() { return pw; }
    public String getEm() { return em; }
}
```

### Prompt Used

> I want to make this code more readable and maintainable. Please help me by:
> 1. Identifying parts that are difficult to understand
> 2. Suggesting better variable and function names
> 3. Recommending ways to break down complex sections
> 4. Pointing out any inconsistent style or formatting issues
>
> Language/Framework: Java
> Team coding standards: Standard Java conventions (camelCase for variables, PascalCase for classes, descriptive method names)

### AI Analysis: Problems Identified

#### Problem 1: Cryptic Names Everywhere

This is the biggest issue. Almost every name in the code is abbreviated to the point of being unreadable:

| Original Name | What It Actually Means | Suggested Name |
|---------------|----------------------|----------------|
| `UserMgr` | User Manager | `UserManager` |
| `U` | A User | `User` |
| `u_list` | List of users | `users` |
| `d` / `db` | Database connection | `database` or `databaseConnection` |
| `a()` | Add/register a user | `registerUser()` |
| `f()` | Find a user | `findUserByUsername()` |
| `un` | Username | `username` |
| `pw` | Password | `password` |
| `em` | Email | `email` |
| `nu` | New user | `newUser` |
| `res` | Result | `saveSuccessful` |
| `getUn()` | Get username | `getUsername()` |
| `getPw()` | Get password | `getPassword()` |
| `getEm()` | Get email | `getEmail()` |

**Why this matters:** When you come back to this code in 3 months (or a teammate reads it for the first time), `a(String un, String pw, String em)` gives zero indication of what the method does. `registerUser(String username, String password, String email)` is instantly clear. Good names are the cheapest form of documentation.

#### Problem 2: SQL Injection Vulnerability 🚨

```java
db.execute("INSERT INTO users VALUES ('" + un + "', '" + pw + "', '" + em + "')");
```

This is a **critical security flaw**. Building SQL queries by concatenating strings allows **SQL injection attacks**. If someone enters a username like `'; DROP TABLE users; --`, the database would execute that destructive command.

**What SQL injection means in plain language:** Imagine a form where you type your name, and the computer puts it into a sentence like "Hello, [name]!" If someone types `Bob! Now delete everything. Hello,` — the computer blindly follows those instructions because it can't tell the difference between your data and its own commands. That's SQL injection.

**The fix — parameterized queries:**

```java
db.execute("INSERT INTO users VALUES (?, ?, ?)", username, password, email);
```

The `?` marks are placeholders. The database treats anything put in those slots as *data*, never as *commands* — so malicious input is harmless.

#### Problem 3: Password Stored in Plain Text

The password is stored directly in the database as-is. In real applications, passwords must be **hashed** (transformed into an unreadable string) before storage. If someone steals the database, they get every user's actual password.

#### Problem 4: Mixed Responsibilities in `a()` (the register method)

The `a()` method does three different things:
1. Validates input (username length, password length, email format)
2. Checks for duplicate usernames
3. Creates the user and saves to database

Each of these should be a separate method for clarity and testability.

#### Problem 5: Inconsistent Style

- `u_list` uses snake_case, but Java convention is camelCase (`userList` or just `users`)
- Single-letter parameter names (`d`) mixed with abbreviated names (`un`, `pw`)
- No Javadoc comments on any public methods

### AI-Suggested Refactored Version

```java
/**
 * Manages user registration and lookup operations.
 */
class UserManager {
    private List<User> users;
    private DatabaseConnection database;

    public UserManager(DatabaseConnection database) {
        this.database = database;
        this.users = new ArrayList<>();
    }

    /**
     * Register a new user after validating their information.
     * @return true if registration was successful, false otherwise
     */
    public boolean registerUser(String username, String password, String email) {
        if (!isValidInput(username, password, email)) {
            return false;
        }

        if (isUsernameTaken(username)) {
            return false;
        }

        User newUser = new User(username, password, email);
        users.add(newUser);
        return saveUserToDatabase(newUser);
    }

    /**
     * Find a user by their username.
     * @return the User if found, null otherwise
     */
    public User findUserByUsername(String username) {
        for (User user : users) {
            if (user.getUsername().equals(username)) {
                return user;
            }
        }
        return null;
    }

    private boolean isValidInput(String username, String password, String email) {
        return username.length() >= 3
            && password.length() >= 8
            && email.contains("@");
    }

    private boolean isUsernameTaken(String username) {
        for (User user : users) {
            if (user.getUsername().equals(username)) {
                return true;
            }
        }
        return false;
    }

    private boolean saveUserToDatabase(User user) {
        return database.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            user.getUsername(),
            user.getPassword(),
            user.getEmail()
        );
    }
}

/**
 * Represents a registered user.
 */
class User {
    private String username;
    private String password;
    private String email;

    public User(String username, String password, String email) {
        this.username = username;
        this.password = password;
        this.email = email;
    }

    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public String getEmail() { return email; }
}
```

### What Changed and Why

| Change | Before | After | Benefit |
|--------|--------|-------|---------|
| Class names | `UserMgr`, `U` | `UserManager`, `User` | Instantly clear what each class represents |
| Method names | `a()`, `f()` | `registerUser()`, `findUserByUsername()` | Methods describe what they do |
| Variable names | `un`, `pw`, `em`, `nu`, `res` | `username`, `password`, `email`, `newUser` | Self-documenting code |
| Extracted methods | One big method | `isValidInput()`, `isUsernameTaken()`, `saveUserToDatabase()` | Each method has one job; easier to test and modify |
| SQL query | String concatenation | Parameterized query (`?`) | Prevents SQL injection attacks |
| Comments | None | Javadoc on public methods | Other developers understand the API |
| Style | Mixed (`u_list` snake_case) | Consistent camelCase | Follows Java conventions |

### Issues I Might Have Missed Without AI

The **SQL injection vulnerability** was the most important catch. I was focused on naming and structure, but the AI immediately flagged the security risk. This shows that readability improvements and security reviews often go hand-in-hand — when code is hard to read, security issues hide more easily.

---

## Exercise 2: Function Refactoring (Python)

### The Original Code

```python
def process_orders(orders, inventory, customer_data):
    results = []
    total_revenue = 0
    error_orders = []

    for order in orders:
        item_id = order['item_id']
        quantity = order['quantity']
        customer_id = order['customer_id']

        if item_id not in inventory:
            error_orders.append({'order_id': order['order_id'], 'error': 'Item not in inventory'})
            continue
        if inventory[item_id]['quantity'] < quantity:
            error_orders.append({'order_id': order['order_id'], 'error': 'Insufficient quantity'})
            continue
        if customer_id not in customer_data:
            error_orders.append({'order_id': order['order_id'], 'error': 'Customer not found'})
            continue

        price = inventory[item_id]['price'] * quantity
        if customer_data[customer_id]['premium']:
            price = price * 0.9

        inventory[item_id]['quantity'] -= quantity

        shipping = 0
        if customer_data[customer_id]['location'] == 'domestic':
            if price < 50:
                shipping = 5.99
        else:
            shipping = 15.99

        tax = price * 0.08
        final_price = price + shipping + tax
        total_revenue += final_price

        result = {
            'order_id': order['order_id'],
            'item_id': item_id,
            'quantity': quantity,
            'customer_id': customer_id,
            'price': price,
            'shipping': shipping,
            'tax': tax,
            'final_price': final_price
        }
        results.append(result)

    return {
        'processed_orders': results,
        'error_orders': error_orders,
        'total_revenue': total_revenue
    }
```

### Prompt Used

> I have a function that I think is doing too much. Please help me refactor it by:
> 1. Identifying the different responsibilities this function has
> 2. Suggesting how to break it into smaller, focused functions
> 3. Improving the organization and flow of the code
> 4. Pointing out any other issues you notice
>
> What this function should do: Process orders, update inventory, and track revenue.

### AI Analysis: Responsibilities Identified

The function has **six distinct responsibilities** jammed into one:

1. **Order validation** — checking inventory availability and customer existence
2. **Price calculation** — computing base price with premium discount
3. **Inventory management** — reducing stock quantities
4. **Shipping calculation** — determining shipping cost based on location and price
5. **Tax calculation** — computing tax amount
6. **Revenue tracking** — accumulating total revenue

**Why this is a problem:** If the tax rate changes from 8% to 10%, you have to dig through a 50-line function to find the one relevant line. If the shipping rules change, same problem. If a bug appears in price calculation, you're debugging the entire order processing flow instead of one small function.

**The principle: Single Responsibility.** Each function should do one thing. This makes code easier to read, test, modify, and debug.

### AI-Suggested Refactored Version

```python
def validate_order(order, inventory, customer_data):
    """Check if an order can be fulfilled. Returns an error message or None."""
    item_id = order['item_id']
    quantity = order['quantity']
    customer_id = order['customer_id']

    if item_id not in inventory:
        return 'Item not in inventory'
    if inventory[item_id]['quantity'] < quantity:
        return 'Insufficient quantity'
    if customer_id not in customer_data:
        return 'Customer not found'
    return None


def calculate_item_price(item_id, quantity, customer_id, inventory, customer_data):
    """Calculate the price for items, applying premium discount if applicable."""
    price = inventory[item_id]['price'] * quantity

    if customer_data[customer_id].get('premium', False):
        price *= 0.9  # 10% discount for premium customers

    return price


def calculate_shipping(price, customer_location):
    """Determine shipping cost based on location and order value."""
    if customer_location == 'domestic':
        return 5.99 if price < 50 else 0  # Free domestic shipping over $50
    return 15.99  # International shipping


def calculate_tax(price, tax_rate=0.08):
    """Calculate tax on the given price."""
    return price * tax_rate


def process_single_order(order, inventory, customer_data):
    """Process one order: validate, calculate costs, update inventory."""
    # Validate
    error = validate_order(order, inventory, customer_data)
    if error:
        return None, {'order_id': order['order_id'], 'error': error}

    item_id = order['item_id']
    quantity = order['quantity']
    customer_id = order['customer_id']

    # Calculate costs
    price = calculate_item_price(item_id, quantity, customer_id, inventory, customer_data)
    shipping = calculate_shipping(price, customer_data[customer_id]['location'])
    tax = calculate_tax(price)
    final_price = price + shipping + tax

    # Update inventory
    inventory[item_id]['quantity'] -= quantity

    result = {
        'order_id': order['order_id'],
        'item_id': item_id,
        'quantity': quantity,
        'customer_id': customer_id,
        'price': price,
        'shipping': shipping,
        'tax': tax,
        'final_price': final_price
    }

    return result, None


def process_orders(orders, inventory, customer_data):
    """Process all orders and return results with revenue summary."""
    results = []
    error_orders = []
    total_revenue = 0

    for order in orders:
        result, error = process_single_order(order, inventory, customer_data)

        if error:
            error_orders.append(error)
        else:
            results.append(result)
            total_revenue += result['final_price']

    return {
        'processed_orders': results,
        'error_orders': error_orders,
        'total_revenue': total_revenue
    }
```

### What Changed and Why

| Original | Refactored | Benefit |
|----------|-----------|---------|
| One 50-line function | Six focused functions, each under 15 lines | Each function is easy to read and understand |
| Validation mixed into the loop | `validate_order()` — standalone function | Can be tested independently; validation rules easy to find and change |
| Price calculation buried in the loop | `calculate_item_price()` — standalone function | Premium discount logic is isolated; easy to add new discount types |
| Shipping logic mixed in | `calculate_shipping()` — standalone function | Shipping rules can change without touching anything else |
| Tax hardcoded in the loop | `calculate_tax()` with default parameter | Tax rate is configurable; function is reusable |
| Everything processes inside one loop | `process_single_order()` handles one order | Can test with one order instead of building a list |

### Key Python Concepts

**`.get('premium', False)`** — The refactored version uses `.get()` with a default value instead of direct dictionary access. If a customer doesn't have a `premium` key, the original code would crash with a `KeyError`. The refactored version safely defaults to `False`.

**Returning `None` for errors** — `validate_order` returns `None` when there's no error and a string message when there is. This pattern lets the caller check `if error:` cleanly. In Python, `None` is "falsy" (treated as `False` in an `if` statement).

**Default parameters** — `calculate_tax(price, tax_rate=0.08)` means the tax rate defaults to 8% but can be overridden. If the rate changes for certain states, you can call `calculate_tax(price, tax_rate=0.10)` without modifying the function.

**Returning tuples** — `process_single_order` returns `(result, error)` — a tuple where one is always `None`. This is a common Python pattern for functions that can either succeed or fail.

### Additional Issues Noticed

1. **The function modifies `inventory` directly** — This is a "side effect." The caller might not realize that passing their inventory dictionary to this function will change it. A safer approach would be to return the inventory changes and let the caller apply them.

2. **No error handling for missing keys** — If an order dictionary is missing `item_id`, the function crashes with a `KeyError`. Defensive coding would check for required keys first.

3. **Magic numbers** — `0.9` (discount), `5.99` (domestic shipping), `15.99` (international shipping), `0.08` (tax rate), and `50` (free shipping threshold) are hardcoded. These should be constants or configuration values.

---

## Exercise 3: Code Duplication Detection (JavaScript)

### The Original Code

```javascript
function calculateUserStatistics(userData) {
  // Calculate average age
  let totalAge = 0;
  for (let i = 0; i < userData.length; i++) {
    totalAge += userData[i].age;
  }
  const averageAge = totalAge / userData.length;

  // Calculate average income
  let totalIncome = 0;
  for (let i = 0; i < userData.length; i++) {
    totalIncome += userData[i].income;
  }
  const averageIncome = totalIncome / userData.length;

  // Calculate average score
  let totalScore = 0;
  for (let i = 0; i < userData.length; i++) {
    totalScore += userData[i].score;
  }
  const averageScore = totalScore / userData.length;

  // Find highest age
  let highestAge = userData[0].age;
  for (let i = 1; i < userData.length; i++) {
    if (userData[i].age > highestAge) {
      highestAge = userData[i].age;
    }
  }

  // Find highest income
  let highestIncome = userData[0].income;
  for (let i = 1; i < userData.length; i++) {
    if (userData[i].income > highestIncome) {
      highestIncome = userData[i].income;
    }
  }

  // Find highest score
  let highestScore = userData[0].score;
  for (let i = 1; i < userData.length; i++) {
    if (userData[i].score > highestScore) {
      highestScore = userData[i].score;
    }
  }

  return {
    age: { average: averageAge, highest: highestAge },
    income: { average: averageIncome, highest: highestIncome },
    score: { average: averageScore, highest: highestScore }
  };
}
```

### Prompt Used

> I suspect there might be repeated patterns in this code that could be consolidated. Please help me by:
> 1. Identifying similar code segments that appear multiple times
> 2. Suggesting ways to eliminate the duplication
> 3. Showing me what the refactored code could look like
> 4. Explaining the benefits of the suggested changes

### AI Analysis: Duplication Patterns Found

The AI identified **two repeated patterns**, each appearing three times:

**Pattern 1: Calculate average** (repeated 3 times)

```javascript
let total = 0;
for (let i = 0; i < userData.length; i++) {
    total += userData[i].PROPERTY;
}
const average = total / userData.length;
```

The only thing that changes between the three copies is the property name (`age`, `income`, `score`). The loop structure, the division, and the accumulation pattern are identical.

**Pattern 2: Find highest value** (repeated 3 times)

```javascript
let highest = userData[0].PROPERTY;
for (let i = 1; i < userData.length; i++) {
    if (userData[i].PROPERTY > highest) {
        highest = userData[i].PROPERTY;
    }
}
```

Again, only the property name changes. The loop structure and comparison logic are identical.

**Total: 6 nearly-identical loops** doing only 2 distinct operations. This is textbook duplication.

### Why Duplication Is a Problem

1. **Bug risk:** If you fix a bug in the "average age" loop but forget to fix the identical bug in the "average income" loop, you have an inconsistency.
2. **Change amplification:** If the average calculation needs to exclude null values, you'd have to make the same change in 3 places.
3. **Code bloat:** 50+ lines of code for something that could be expressed in 10.

### AI-Suggested Refactored Version

```javascript
/**
 * Calculate the average of a specific property across all items.
 */
function calculateAverage(data, property) {
  const total = data.reduce((sum, item) => sum + item[property], 0);
  return total / data.length;
}

/**
 * Find the highest value of a specific property across all items.
 */
function findHighest(data, property) {
  return Math.max(...data.map(item => item[property]));
}

/**
 * Calculate statistics (average and highest) for specified properties.
 */
function calculateUserStatistics(userData) {
  const properties = ['age', 'income', 'score'];

  const stats = {};
  for (const property of properties) {
    stats[property] = {
      average: calculateAverage(userData, property),
      highest: findHighest(userData, property)
    };
  }

  return stats;
}
```

### How the Refactoring Works — JavaScript Concepts Explained

#### `data.reduce((sum, item) => sum + item[property], 0)`

This replaces the manual "loop and accumulate" pattern. `reduce` processes every item in an array and "reduces" it to a single value.

Breaking it down:
- `data` — the array of user objects
- `.reduce(...)` — "go through each item and combine them into one result"
- `(sum, item) =>` — for each item, `sum` is the running total so far, `item` is the current user
- `sum + item[property]` — add this user's value to the running total
- `, 0` — start the running total at 0

**Equivalent to:**
```javascript
let sum = 0;                    // Start at 0
for (let item of data) {
    sum = sum + item[property]; // Add each item's value
}
return sum;
```

#### `data.map(item => item[property])`

`map` transforms every item in an array. `data.map(item => item.age)` turns `[{age: 25, ...}, {age: 30, ...}]` into `[25, 30]`.

#### `Math.max(...array)`

`Math.max()` finds the biggest number. The `...` (spread operator) unpacks an array into individual arguments. So `Math.max(...[25, 30, 22])` becomes `Math.max(25, 30, 22)` which returns `30`.

#### `item[property]` — Dynamic property access

In JavaScript, `item.age` and `item['age']` do the same thing. But `item[property]` where `property` is a variable containing `'age'` lets you access different properties dynamically. This is what makes the helper functions reusable — you pass the property name as a string.

### Adding a New Property

The power of eliminating duplication becomes clear when requirements change. To add statistics for a new property like `experience`:

**Before (duplicated code):** Copy-paste another ~16 lines of loop code, change the property name in 4 places.

**After (refactored code):** Add one word:

```javascript
const properties = ['age', 'income', 'score', 'experience'];
```

That's it. One line change instead of 16 lines of copy-paste.

### Edge Case the AI Flagged

The original code crashes if `userData` is empty — `userData[0].age` throws an error when there are no items, and dividing by `userData.length` (which is 0) returns `Infinity`. The refactored version should add a guard:

```javascript
function calculateUserStatistics(userData) {
  if (!userData || userData.length === 0) {
    return { age: { average: 0, highest: 0 },
             income: { average: 0, highest: 0 },
             score: { average: 0, highest: 0 } };
  }
  // ... rest of function
}
```

---

## Reflection

### Which prompting strategy was most useful?

**Function Refactoring** (Exercise 2) was the most valuable because it taught a transferable skill — recognizing when a function has too many responsibilities and knowing how to split it up. The before/after difference was dramatic: one 50-line function became six clear, testable functions.

### What did the AI suggest that I might not have thought of?

The **SQL injection vulnerability** in Exercise 1 was the biggest surprise. I was focused on naming and structure, but the AI immediately identified a critical security flaw. This reinforces that code readability and security go together — messy code hides dangerous bugs.

In Exercise 2, the suggestion to use **default parameters** for the tax rate (`tax_rate=0.08`) was something I wouldn't have thought of. It makes the function flexible without adding complexity.

### Were there any AI suggestions I disagreed with?

The JavaScript `reduce` and `Math.max(...spread)` syntax in Exercise 3 is powerful but potentially harder to read for beginners than a simple `for` loop. For a team of junior developers, the AI also suggested an intermediate approach using `for...of` loops with a helper function — which might be more appropriate depending on the team's comfort level. The "best" refactoring depends on who will be reading the code.

### What safeguards before applying refactoring to production code?

1. **Have tests in place BEFORE refactoring** — if tests pass before and after, you know you haven't broken anything
2. **Refactor in small steps** — change one thing at a time, run tests after each change
3. **Use version control (git)** — commit before refactoring so you can revert if things go wrong
4. **Get code review** — another developer's eyes catch things you miss
5. **Don't refactor and add features at the same time** — these are separate activities with separate risks
