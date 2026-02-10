# Exercise 14: Design Pattern Implementation Challenge

---

## Pattern 1: Strategy Pattern (JavaScript — Shipping Calculator)

### The Original Code

```javascript
function calculateShippingCost(packageDetails, destinationCountry, shippingMethod) {
  const { weight, length, width, height } = packageDetails;
  let cost = 0;

  if (shippingMethod === 'standard') {
    if (destinationCountry === 'USA') {
      cost = weight * 2.5;
    } else if (destinationCountry === 'Canada') {
      cost = weight * 3.5;
    } else if (destinationCountry === 'Mexico') {
      cost = weight * 4.0;
    } else {
      cost = weight * 4.5;
    }
    if (weight < 2 && (length * width * height) > 1000) {
      cost += 5.0;
    }
  } else if (shippingMethod === 'express') {
    if (destinationCountry === 'USA') {
      cost = weight * 4.5;
    } else if (destinationCountry === 'Canada') {
      cost = weight * 5.5;
    } else if (destinationCountry === 'Mexico') {
      cost = weight * 6.0;
    } else {
      cost = weight * 7.5;
    }
    if ((length * width * height) > 5000) {
      cost += 15.0;
    }
  } else if (shippingMethod === 'overnight') {
    if (destinationCountry === 'USA') {
      cost = weight * 9.5;
    } else if (destinationCountry === 'Canada') {
      cost = weight * 12.5;
    } else {
      return "Overnight shipping not available for this destination";
    }
  }

  return cost.toFixed(2);
}
```

### What's Wrong With This Code?

The function has **nested conditionals** — an outer layer checking the shipping method, and an inner layer checking the destination country. Every shipping method repeats the same country-checking pattern with different rates.

Problems:
- **Adding a new shipping method** means adding another huge `else if` block with all the country checks duplicated
- **Adding a new country** means finding and updating the rates inside every shipping method block
- **Each method has unique surcharge rules** tangled into the same function
- **Testing** requires testing every combination of method × country

### Prompt Used

> I'd like to refactor this code to implement the Strategy design pattern.
>
> I think this pattern is applicable because each shipping method (standard, express, overnight) has its own pricing logic, surcharge rules, and country restrictions. These are interchangeable "strategies" for calculating shipping cost.
>
> I'm thinking of implementing it by creating a separate class or object for each shipping method, where each one has a `calculate(packageDetails, country)` method, and then selecting the right strategy based on the shipping method string.

### AI Response: Validation and Plan

The AI confirmed the Strategy pattern is a good fit and suggested this plan:

1. **Define a common interface** — each strategy must have a `calculate(package, country)` method
2. **Create one strategy per shipping method** — StandardShipping, ExpressShipping, OvernightShipping
3. **Extract country rates into data** — replace the if/else country chains with a rate lookup object
4. **Create a strategy selector** — maps method names to their strategy objects
5. **Simplify the main function** — just picks a strategy and calls it

### What Is the Strategy Pattern?

**Analogy:** Think of a GPS navigation app. You choose a "strategy" for your route: fastest, shortest, avoid highways, or walking. Each strategy calculates the route differently, but they all take the same input (start and end point) and produce the same output (a route). You can switch strategies without changing the app — you just pick a different one.

**In code terms:** Instead of a giant if/else chain where each branch has different logic, you create separate objects (strategies) that each implement the same interface. The main code just picks the right strategy and calls it.

```
BEFORE: One function with if/else for each method
    calculateShippingCost()
    ├── if standard → [all standard logic]
    ├── else if express → [all express logic]
    └── else if overnight → [all overnight logic]

AFTER: Separate strategy for each method
    calculateShippingCost() → picks strategy → strategy.calculate()
    ├── StandardShippingStrategy.calculate()
    ├── ExpressShippingStrategy.calculate()
    └── OvernightShippingStrategy.calculate()
```

### Refactored Code

```javascript
// ─── Rate Data ──────────────────────────────────────────────
// Country rates per kg for each shipping method
// Extracting these into data makes them easy to update without touching logic

const STANDARD_RATES = {
  USA: 2.5,
  Canada: 3.5,
  Mexico: 4.0,
  _default: 4.5  // International fallback
};

const EXPRESS_RATES = {
  USA: 4.5,
  Canada: 5.5,
  Mexico: 6.0,
  _default: 7.5
};

const OVERNIGHT_RATES = {
  USA: 9.5,
  Canada: 12.5
  // No _default — overnight isn't available internationally
};


// ─── Helper: Look Up Country Rate ───────────────────────────

function getCountryRate(rates, country) {
  return rates[country] ?? rates._default ?? null;
}


// ─── Shipping Strategies ────────────────────────────────────
// Each strategy encapsulates all the pricing logic for one shipping method

const standardShipping = {
  name: 'standard',

  calculate(packageDetails, country) {
    const { weight, length, width, height } = packageDetails;
    const rate = getCountryRate(STANDARD_RATES, country);
    if (rate === null) return null;

    let cost = weight * rate;

    // Dimensional weight surcharge: light packages that take up lots of space
    const volume = length * width * height;
    if (weight < 2 && volume > 1000) {
      cost += 5.0;
    }

    return cost;
  }
};

const expressShipping = {
  name: 'express',

  calculate(packageDetails, country) {
    const { weight, length, width, height } = packageDetails;
    const rate = getCountryRate(EXPRESS_RATES, country);
    if (rate === null) return null;

    let cost = weight * rate;

    // Large package surcharge for express
    const volume = length * width * height;
    if (volume > 5000) {
      cost += 15.0;
    }

    return cost;
  }
};

const overnightShipping = {
  name: 'overnight',

  calculate(packageDetails, country) {
    const { weight } = packageDetails;
    const rate = getCountryRate(OVERNIGHT_RATES, country);

    // Overnight not available for countries without a rate
    if (rate === null) return null;

    return weight * rate;
  }
};


// ─── Strategy Selector ──────────────────────────────────────

const shippingStrategies = {
  standard: standardShipping,
  express: expressShipping,
  overnight: overnightShipping
};


// ─── Main Function ──────────────────────────────────────────

function calculateShippingCost(packageDetails, destinationCountry, shippingMethod) {
  const strategy = shippingStrategies[shippingMethod];

  if (!strategy) {
    return "Unknown shipping method";
  }

  const cost = strategy.calculate(packageDetails, destinationCountry);

  if (cost === null) {
    return `${strategy.name} shipping not available for this destination`;
  }

  return cost.toFixed(2);
}
```

### How to Add a New Shipping Method Now

**Before (original):** Add another 15-line `else if` block inside the function, duplicating all the country logic.

**After (Strategy pattern):** Create a new strategy object and register it:

```javascript
const ECONOMY_RATES = { USA: 1.5, Canada: 2.0, _default: 3.0 };

const economyShipping = {
  name: 'economy',
  calculate(packageDetails, country) {
    const rate = getCountryRate(ECONOMY_RATES, country);
    if (rate === null) return null;
    return packageDetails.weight * rate;
    // No surcharges for economy
  }
};

// Register it — one line
shippingStrategies.economy = economyShipping;
```

The main `calculateShippingCost` function doesn't change at all. This is the **Open/Closed Principle**: the system is open for extension (add new methods) but closed for modification (existing code untouched).

### Benefits Gained

| Before | After |
|--------|-------|
| One 40-line function with nested if/else | Main function is 10 lines; each strategy is 10-15 lines |
| Adding a method means modifying the main function | Adding a method means creating a new object |
| Adding a country means editing every method block | Adding a country means updating one rate object |
| Testing requires all combinations in one test | Each strategy can be tested independently |
| Surcharge rules are tangled with rate lookups | Surcharge rules are isolated per strategy |

---

## Pattern 2: Factory Pattern (Python — Database Connections)

### The Original Code

```python
class DatabaseConnection:
    def __init__(self, db_type, host, port, username, password, database,
                 use_ssl=False, connection_timeout=30, retry_attempts=3,
                 pool_size=5, charset='utf8'):
        # ... stores all 11 parameters ...
        
    def connect(self):
        if self.db_type == 'mysql':
            # MySQL-specific connection logic
        elif self.db_type == 'postgresql':
            # PostgreSQL-specific connection logic
        elif self.db_type == 'mongodb':
            # MongoDB-specific connection logic
        elif self.db_type == 'redis':
            # Redis-specific connection logic
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
```

### What's Wrong With This Code?

1. **One class tries to be everything** — `DatabaseConnection` handles MySQL, PostgreSQL, MongoDB, and Redis. Each database type has different connection string formats, different SSL handling, and different relevant parameters.

2. **Parameter bloat** — 11 parameters in `__init__`, but not all apply to every database type. Redis doesn't use `charset`. MongoDB doesn't use `connection_timeout` the same way. The caller has no idea which parameters matter for their database type.

3. **`if/elif` chain in `connect()`** — Every new database type means adding another branch. The method grows forever.

4. **No specialization** — You can't add MySQL-specific features without affecting all other database types.

### What Is the Factory Pattern?

**Analogy:** A pizza restaurant has one menu (the factory), but behind the scenes there are specialized stations — one for thin crust, one for deep dish, one for Neapolitan. You tell the cashier "I want a Neapolitan" and the right station makes it. You don't need to know how each station works; you just get a pizza.

**In code terms:** Instead of one class that uses if/else to handle every variant, you create:
1. A **base class** (or interface) that defines what all variants must do
2. **Specialized classes** for each variant (MySQLConnection, PostgreSQLConnection, etc.)
3. A **factory function** that creates the right class based on input

```
BEFORE: One class does everything
    DatabaseConnection(db_type='mysql')
    DatabaseConnection(db_type='postgresql')
    DatabaseConnection(db_type='mongodb')

AFTER: Factory creates the right specialized class
    create_connection('mysql')      → MySQLConnection
    create_connection('postgresql')  → PostgreSQLConnection
    create_connection('mongodb')     → MongoDBConnection
```

### Prompt Used

> I'd like to refactor this code to implement the Factory design pattern.
>
> I think this pattern is applicable because each database type (mysql, postgresql, mongodb, redis) needs its own connection logic, its own relevant parameters, and its own connection string format. A single class with if/else is doing too much.
>
> I'm thinking of implementing it by creating a base class with the shared interface, specialized subclasses for each database type, and a factory function that creates the right one based on db_type.

### Refactored Code

```python
from abc import ABC, abstractmethod


# ─── Base Class ──────────────────────────────────────────────
# Defines the interface that ALL database connections must implement

class DatabaseConnection(ABC):
    """Base class for all database connections."""

    def __init__(self, host, port, username, password, database, use_ssl=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.use_ssl = use_ssl
        self.connection = None

    @abstractmethod
    def connect(self):
        """Connect to the database. Each subclass implements this differently."""
        pass

    @abstractmethod
    def build_connection_string(self):
        """Build the connection string specific to this database type."""
        pass


# ─── Specialized Classes ─────────────────────────────────────
# Each class knows ONLY about its own database type

class MySQLConnection(DatabaseConnection):
    """MySQL-specific database connection."""

    def __init__(self, host, port, username, password, database,
                 use_ssl=False, connection_timeout=30, charset='utf8'):
        super().__init__(host, port, username, password, database, use_ssl)
        self.connection_timeout = connection_timeout
        self.charset = charset

    def build_connection_string(self):
        conn_str = (
            f"mysql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
            f"&connectionTimeout={self.connection_timeout}"
        )
        if self.use_ssl:
            conn_str += "&useSSL=true"
        return conn_str

    def connect(self):
        connection_string = self.build_connection_string()
        print(f"MySQL Connection: {connection_string}")
        # In a real app: self.connection = mysql.connector.connect(...)
        print("Connection successful!")
        return self.connection


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL-specific database connection."""

    def build_connection_string(self):
        conn_str = (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
        if self.use_ssl:
            conn_str += "?sslmode=require"
        return conn_str

    def connect(self):
        connection_string = self.build_connection_string()
        print(f"PostgreSQL Connection: {connection_string}")
        # In a real app: self.connection = psycopg2.connect(...)
        print("Connection successful!")
        return self.connection


class MongoDBConnection(DatabaseConnection):
    """MongoDB-specific database connection."""

    def __init__(self, host, port, username, password, database,
                 use_ssl=False, retry_attempts=3, pool_size=5):
        super().__init__(host, port, username, password, database, use_ssl)
        self.retry_attempts = retry_attempts
        self.pool_size = pool_size

    def build_connection_string(self):
        conn_str = (
            f"mongodb://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?retryAttempts={self.retry_attempts}"
            f"&poolSize={self.pool_size}"
        )
        if self.use_ssl:
            conn_str += "&ssl=true"
        return conn_str

    def connect(self):
        connection_string = self.build_connection_string()
        print(f"MongoDB Connection: {connection_string}")
        # In a real app: self.connection = pymongo.MongoClient(...)
        print("Connection successful!")
        return self.connection


class RedisConnection(DatabaseConnection):
    """Redis-specific database connection."""

    def build_connection_string(self):
        return f"{self.host}:{self.port}/{self.database}"

    def connect(self):
        connection_string = self.build_connection_string()
        print(f"Redis Connection: {connection_string}")
        # In a real app: self.connection = redis.Redis(...)
        print("Connection successful!")
        return self.connection


# ─── The Factory ─────────────────────────────────────────────
# One function that creates the right connection type

CONNECTION_TYPES = {
    'mysql': MySQLConnection,
    'postgresql': PostgreSQLConnection,
    'mongodb': MongoDBConnection,
    'redis': RedisConnection,
}


def create_connection(db_type, **kwargs):
    """
    Factory function: create the right database connection based on type.

    Args:
        db_type: One of 'mysql', 'postgresql', 'mongodb', 'redis'
        **kwargs: Connection parameters (host, port, username, password, database, etc.)
                  Each database type accepts its own specific extra parameters.

    Returns:
        A DatabaseConnection subclass instance.

    Raises:
        ValueError: If db_type is not supported.
    """
    connection_class = CONNECTION_TYPES.get(db_type)

    if connection_class is None:
        supported = ', '.join(CONNECTION_TYPES.keys())
        raise ValueError(
            f"Unsupported database type: '{db_type}'. Supported: {supported}"
        )

    return connection_class(**kwargs)


# ─── Example Usage ───────────────────────────────────────────

# MySQL — only accepts MySQL-relevant parameters
mysql_db = create_connection(
    'mysql',
    host='localhost',
    port=3306,
    username='db_user',
    password='password123',
    database='app_db',
    use_ssl=True,
    charset='utf8mb4'  # MySQL-specific parameter
)
mysql_db.connect()

# MongoDB — only accepts MongoDB-relevant parameters
mongo_db = create_connection(
    'mongodb',
    host='mongodb.example.com',
    port=27017,
    username='mongo_user',
    password='mongo123',
    database='analytics',
    pool_size=10,        # MongoDB-specific parameter
    retry_attempts=5     # MongoDB-specific parameter
)
mongo_db.connect()
```

### Key Python Concepts in This Pattern

#### `ABC` and `@abstractmethod`

```python
from abc import ABC, abstractmethod

class DatabaseConnection(ABC):
    @abstractmethod
    def connect(self):
        pass
```

`ABC` stands for **Abstract Base Class**. An abstract class is a class that can't be used directly — you must create a subclass. The `@abstractmethod` decorator marks methods that every subclass MUST implement. If you create a subclass without a `connect()` method, Python raises an error immediately.

**Why this matters:** It's a contract. Anyone creating a new database connection class knows exactly what methods they need to implement. The code won't even let you forget.

#### `super().__init__(...)`

```python
class MySQLConnection(DatabaseConnection):
    def __init__(self, host, port, ...):
        super().__init__(host, port, ...)
        self.charset = charset  # MySQL-specific
```

`super()` calls the parent class's method. Here, it runs `DatabaseConnection.__init__()` to set up the common fields (host, port, username, etc.), then the MySQL class adds its own specific fields. This avoids duplicating the common setup code in every subclass.

#### `**kwargs` — Keyword Arguments

```python
def create_connection(db_type, **kwargs):
    return connection_class(**kwargs)
```

`**kwargs` collects any named arguments into a dictionary. When you call `create_connection('mysql', host='localhost', port=3306)`, inside the function `kwargs` is `{'host': 'localhost', 'port': 3306}`. Then `connection_class(**kwargs)` unpacks that dictionary back into named arguments for the class constructor.

**Why this is useful for factories:** The factory doesn't need to know what parameters each database type needs. It just passes everything through to the right class.

### How to Add a New Database Type

**Before (original):** Modify the `DatabaseConnection` class — add another `elif` branch in `connect()`, add any new parameters to the already-bloated 11-parameter `__init__`.

**After (Factory pattern):**

```python
# Step 1: Create a new class
class SQLiteConnection(DatabaseConnection):
    def __init__(self, database, **kwargs):
        super().__init__('localhost', 0, '', '', database)

    def build_connection_string(self):
        return f"sqlite:///{self.database}"

    def connect(self):
        print(f"SQLite Connection: {self.build_connection_string()}")
        print("Connection successful!")
        return self.connection

# Step 2: Register it — one line
CONNECTION_TYPES['sqlite'] = SQLiteConnection
```

No existing code is modified. The factory, the base class, and all other connection types are untouched.

### Benefits Gained

| Aspect | Before | After |
|--------|--------|-------|
| **Parameters** | 11 parameters, most irrelevant for any given type | Each class accepts only its relevant parameters |
| **Adding a type** | Modify the existing class, risk breaking others | Create a new class, register in one line |
| **connect() method** | One method with 4 if/elif branches | Each class has its own clean connect() |
| **Type safety** | `charset` accepted for Redis (meaningless) | Redis class doesn't have charset parameter |
| **Testing** | Test one big class with all branches | Test each connection class independently |
| **Readability** | Scroll through 80 lines to find MongoDB logic | Open `MongoDBConnection` class — everything's there |

---

## Pattern Comparison: When to Use Which

| Pattern | Use When | Recognizable By |
|---------|----------|----------------|
| **Strategy** | Multiple algorithms that do the same job differently | if/else chain where each branch has parallel logic for the same task |
| **Factory** | Multiple types of objects that share an interface | if/else in constructors or creation code, classes with type-checking logic |
| **Observer** | One change needs to notify many listeners | Methods that explicitly call multiple update functions in sequence |
| **Adapter** | Wrapping an external API to fit your interface | Translation code between your data format and an external system's format |

### How to Spot Pattern Opportunities (Rules of Thumb)

1. **If you see a big if/else chain where each branch does a similar job differently** → Strategy pattern
2. **If you see object creation that varies by type** → Factory pattern
3. **If you see one change triggering updates in many places** → Observer pattern
4. **If you see code translating between two different data formats** → Adapter pattern
5. **If you're not sure, don't force a pattern** — premature abstraction is worse than no abstraction

---

## Reflection

### How did implementing the patterns improve maintainability?

Both patterns replaced "modify existing code" with "add new code." In the Strategy version, adding a shipping method doesn't touch the main function. In the Factory version, adding a database type doesn't touch the base class. This is the **Open/Closed Principle** — probably the single most important design principle for professional code.

### What future changes are easier because of these patterns?

- **Strategy:** New shipping methods, new countries, changing surcharge rules — all isolated changes
- **Factory:** New database types, type-specific features (like MongoDB's pool_size), changing connection string formats — all isolated

### Were there unexpected challenges?

The hardest part was deciding **how much to abstract**. For the Strategy pattern, I considered making the country rates part of the strategy interface too, but that would over-complicate things. The current approach (rates as data, surcharges as logic) struck a good balance. The AI's warning about over-engineering was valuable — patterns should solve real problems, not demonstrate cleverness.
