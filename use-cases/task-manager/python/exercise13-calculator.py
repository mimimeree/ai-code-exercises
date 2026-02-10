def calculate(principal, rate, time, additional=0, frequency=12):
    """
    Calculate compound interest with optional annual contributions.

    Simulates the growth of an investment over time, compounding at a
    specified frequency (default: monthly). Additional contributions are
    added once per year at the end of each year (except the final year).

    Args:
        principal (float): Initial investment amount in dollars.
        rate (float): Annual interest rate as a percentage (e.g., 5 for 5%).
        time (int): Number of years to grow the investment.
        additional (float): Amount added at the end of each year (default: 0).
        frequency (int): How many times per year interest compounds (default: 12).

    Returns:
        dict with "final_amount", "interest_earned", "total_contributions"
    """
    result = principal
    rate_per_period = rate / 100 / frequency
    total_periods = time * frequency

    for period in range(1, total_periods + 1):
        interest = result * rate_per_period
        result += interest

        # Add annual contribution at end of each year (except the last year)
        is_year_boundary = (period % frequency == 0)
        is_not_final_year = (period < total_periods)

        if is_year_boundary and is_not_final_year:
            result += additional

    return {
        "final_amount": round(result, 2),
        "interest_earned": round(result - principal - (additional * (time - 1)), 2),
        "total_contributions": principal + (additional * (time - 1))
    }
