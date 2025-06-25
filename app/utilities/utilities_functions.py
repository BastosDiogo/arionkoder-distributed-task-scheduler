import time
from utilities.logs import Logging

def get_func_from_name(func_name: str):
    """Simulates the mapping of a function name to the actual Python function."""

    def process_data(x, y):
        Logging().info(f"Running process data.: {x} + {y}")
        return x + y

    def send_email(recipient, subject, body):
        Logging().info(f"Running send_email to {recipient}: {subject}")
        return f"Email para {recipient}: {subject}"

    def calculate_pi(n_digits):
        Logging().info(f"Running calculate for {n_digits} digits.")
        time.sleep(n_digits * 0.001)
        return sum(1/16**k * (4/(8*k+1) - 2/(8*k+4) - 1/(8*k+5) - 1/(8*k+6)) for k in range(min(n_digits, 1000)))

    func_map = {
        "process_data": process_data,
        "send_email": send_email,
        "calculate_pi": calculate_pi,
    }
    return func_map.get(func_name)