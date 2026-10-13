
import random


class QLearningAgent:
    """
    Demonstration Q-learning agent for dynamic pricing.
    Rewards are simulated, not collected from real customers.
    """

    def __init__(self, learning_rate=0.1, discount_factor=0.9,
                 exploration_rate=0.2):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

        self.actions = ["decrease", "maintain", "increase"]
        self.q_table = {}

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = {
                action: 0.0 for action in self.actions
            }
        return self.q_table[state]

    def choose_action(self, state):
        q_values = self.get_q_values(state)

        if random.random() < self.exploration_rate:
            return random.choice(self.actions)

        best_value = max(q_values.values())
        best_actions = [
            action for action, value in q_values.items()
            if value == best_value
        ]
        return random.choice(best_actions)

    def simulate_reward(self, state, action, current_price,
                        stock_quantity):
        demand_level, stock_level = state

        price_changes = {
            "decrease": -0.10,
            "maintain": 0.0,
            "increase": 0.10,
        }

        selling_price = current_price * (
            1 + price_changes[action]
        )

        # Illustrative cost assumption: 70% of current price.
        estimated_cost = current_price * 0.70
        estimated_profit_per_unit = selling_price - estimated_cost

        demand_units = {
            "low": random.randint(0, 3),
            "medium": random.randint(2, 7),
            "high": random.randint(5, 12),
        }[demand_level]

        # A price increase may reduce simulated customer demand.
        if action == "increase":
            demand_units = int(demand_units * 0.7)
        elif action == "decrease":
            demand_units = int(demand_units * 1.2)

        if stock_level == "low":
            demand_units = min(demand_units, 3)

        units_sold = min(demand_units, stock_quantity)

        # Reward is estimated profit from simulated sales.
        reward = units_sold * estimated_profit_per_unit

        return reward

    def train(self, state, current_price, stock_quantity,
              episodes=1000):
        for _ in range(episodes):
            action = self.choose_action(state)

            reward = self.simulate_reward(
                state,
                action,
                current_price,
                stock_quantity
            )

            q_values = self.get_q_values(state)
            old_value = q_values[action]
            best_future_value = max(q_values.values())

            q_values[action] = old_value + self.learning_rate * (
                reward
                + self.discount_factor * best_future_value
                - old_value
            )

        return self.get_q_values(state)

    def recommend(self, state, current_price,
                  stock_quantity, episodes=1000):
        q_values = self.train(
            state, current_price, stock_quantity, episodes
        )

        best_action = max(q_values, key=q_values.get)

        price_changes = {
            "decrease": -0.10,
            "maintain": 0.0,
            "increase": 0.10,
        }

        recommended_price = current_price * (
            1 + price_changes[best_action]
        )

        return best_action, round(recommended_price, 2), q_values