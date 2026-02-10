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
    """Calculate the discount value for a single promotion. Returns 0 if it doesn't apply."""
    min_purchase = promo.get('min_purchase')
    if min_purchase is not None and cart_total < min_purchase:
        return 0

    if promo['type'] == 'percent':
        return cart_total * promo['value'] / 100
    elif promo['type'] == 'fixed':
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
    Only the highest discount applies (they don't stack).
    """
    cart_total = calculate_cart_total(cart)

    # Find the best promotional discount
    best_discount = 0
    for promo in promos:
        promo_discount = apply_promotion(promo, cart_total)
        best_discount = max(best_discount, promo_discount)

    # Check loyalty discount and keep whichever is higher
    loyalty_discount = apply_loyalty_discount(
        cart_total, user['status'], user.get('months', 0)
    )
    best_discount = max(best_discount, loyalty_discount)

    # Check for free shipping
    if check_free_shipping(promos, cart_total):
        user['free_shipping'] = True

    return {
        'original': cart_total,
        'discount': best_discount,
        'final': cart_total - best_discount,
        'free_shipping': user.get('free_shipping', False)
    }
