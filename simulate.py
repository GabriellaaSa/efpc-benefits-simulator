"""
simulate.py

Runs example scenarios through efpc_calculator and produces two charts:
  1. Accumulated balance growth over a working career.
  2. The regressive income tax rate curve applied to withdrawals/benefits.

Usage:
    python simulate.py
"""

import matplotlib.pyplot as plt

from efpc_calculator import (
    calculate_contribution,
    check_eligibility,
    check_portability,
    income_tax_rate,
    simulate_balance_growth,
)


def print_example_scenario() -> None:
    salary = 8000.0
    ur_value = 100.0  # illustrative UR value in BRL
    participant_percentage = 5.0
    years_of_service = 6
    age = 47

    contribution = calculate_contribution(salary, participant_percentage, ur_value)
    eligibility = check_eligibility(years_of_service, age)
    portable = check_portability(years_of_service)
    ir_rate = income_tax_rate(years_of_service)

    print("=== Cenário de exemplo ===")
    print(f"Salário: R$ {salary:,.2f} | Contribuição escolhida: {participant_percentage}%")
    print(f"Contribuição do participante: R$ {contribution.participant_contribution:,.2f}")
    print(f"Contrapartida da patrocinadora: R$ {contribution.sponsor_contribution:,.2f}")
    print(f"Contribuição total mensal: R$ {contribution.total_contribution:,.2f}")
    print(f"Elegibilidade ({years_of_service} anos, {age} anos de idade): {eligibility['status']}")
    print(f"Portabilidade liberada: {portable}")
    print(f"Alíquota de IR aplicável: {ir_rate:.0%}")


def plot_balance_growth() -> None:
    balances = simulate_balance_growth(
        salary=8000.0,
        participant_percentage=5.0,
        ur_value=100.0,
        years=30,
        annual_return_rate=0.06,
    )

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(balances) + 1), balances, marker="o", markersize=3)
    plt.title("Simulação de saldo acumulado ao longo do vínculo")
    plt.xlabel("Anos de contribuição")
    plt.ylabel("Saldo acumulado (R$)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("balance_growth.png", dpi=150)
    print("Gráfico salvo em balance_growth.png")


def plot_ir_curve() -> None:
    years = list(range(1, 12))
    rates = [income_tax_rate(y) for y in years]

    plt.figure(figsize=(8, 5))
    plt.step(years, [r * 100 for r in rates], where="post")
    plt.title("Tabela regressiva de IR sobre benefícios previdenciários")
    plt.xlabel("Anos de contribuição")
    plt.ylabel("Alíquota de IR (%)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("ir_regressive_curve.png", dpi=150)
    print("Gráfico salvo em ir_regressive_curve.png")


if __name__ == "__main__":
    print_example_scenario()
    plot_balance_growth()
    plot_ir_curve()
