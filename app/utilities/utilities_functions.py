import time

def get_func_from_name(func_name: str):
    """
    Simula o mapeamento de um nome de função para a função Python real.
    Em um sistema real, você teria um registro seguro de funções permitidas.
    """
    def process_data(x, y):
        print(f"Executando process_data: {x} + {y}")
        return x + y

    def send_email(recipient, subject, body):
        print(f"Executando send_email para {recipient}: {subject}")
        return f"Email para {recipient}: {subject}"

    def calculate_pi(n_digits):
        print(f"Executando calculate_pi para {n_digits} dígitos")
        time.sleep(n_digits * 0.001)
        return sum(1/16**k * (4/(8*k+1) - 2/(8*k+4) - 1/(8*k+5) - 1/(8*k+6)) for k in range(min(n_digits, 1000)))

    func_map = {
        "process_data": process_data,
        "send_email": send_email,
        "calculate_pi": calculate_pi,
    }
    return func_map.get(func_name)