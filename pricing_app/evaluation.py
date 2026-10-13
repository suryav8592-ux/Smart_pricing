
import random


def compare_pricing_strategies(
    current_price,
    stock_quantity,
    episodes=100
):
    random.seed(42)

    fixed_revenue = 0
    dynamic_revenue = 0

    fixed_stock = stock_quantity
    dynamic_stock = stock_quantity

    fixed_price = current_price
    dynamic_price = current_price

    for _ in range(episodes):
        # Simulate customer demand
        demand = random.randint(1, 10)

        # Fixed pricing strategy
        fixed_units = min(demand, fixed_stock)
        fixed_revenue += fixed_units * fixed_price
        fixed_stock -= fixed_units

        # Dynamic pricing strategy
        if demand >= 7:
            dynamic_price = current_price * 1.10
        elif demand <= 3:
            dynamic_price = current_price * 0.90
        else:
            dynamic_price = current_price

        dynamic_units = min(demand, dynamic_stock)
        dynamic_revenue += dynamic_units * dynamic_price
        dynamic_stock -= dynamic_units

        if fixed_stock == 0 and dynamic_stock == 0:
            break

    return {
        "fixed_revenue": round(fixed_revenue, 2),
        "dynamic_revenue": round(dynamic_revenue, 2),
        "fixed_stock": fixed_stock,
        "dynamic_stock": dynamic_stock,
    }