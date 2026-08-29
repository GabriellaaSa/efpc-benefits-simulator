"""
efpc_calculator.py

Calculation utilities for Brazilian closed complementary pension funds
(EFPC - Entidade Fechada de Previdência Complementar), regulated by PREVIC
under LC 109/2001. Models the CD/CV (Contribuição Definida / Contribuição
Variável) contribution structure common to plans in this segment: a base
percentage on salary up to a reference threshold (UR - Unidade de Referência),
a participant-chosen percentage above it, and a capped sponsor match.

This is an educational/portfolio project, not a production actuarial tool.
Real benefit conversion (saldo -> renda) requires a certified actuary and a
biometric table, which is intentionally out of scope here - see README.
"""

from dataclasses import dataclass


@dataclass
class ContributionResult:
    participant_contribution: float
    sponsor_contribution: float
    total_contribution: float


def calculate_contribution(
    salary: float,
    participant_percentage: float,
    ur_value: float,
    ur_threshold: float = 10,
    sponsor_cap_percentage: float = 9,
) -> ContributionResult:
    """
    Calculates monthly participant and sponsor contributions.

    Rule modeled after typical CD/CV plans: 1% mandatory on salary up to
    `ur_threshold` UR, plus a participant-chosen percentage (minimum 1%) on
    the portion above that threshold. The sponsor matches the participant's
    contribution on the excess, capped at `sponsor_cap_percentage`.

    Args:
        salary: gross monthly salary (BRL).
        participant_percentage: percentage the participant chose to
            contribute on the portion of salary above the UR threshold
            (e.g. 5 for 5%). Must be >= 1.
        ur_value: monetary value of one UR (Unidade de Referência) for the
            plan/year in question.
        ur_threshold: number of UR below which the flat 1% rate applies.
        sponsor_cap_percentage: maximum percentage the sponsor will match on
            the portion above the threshold.
    """
    if participant_percentage < 1:
        raise ValueError("participant_percentage must be at least 1%")

    threshold_value = ur_threshold * ur_value
    base_salary = min(salary, threshold_value)
    excess_salary = max(0.0, salary - threshold_value)

    base_contribution = base_salary * 0.01
    excess_contribution = excess_salary * (participant_percentage / 100)
    participant_contribution = base_contribution + excess_contribution

    sponsor_rate = min(participant_percentage, sponsor_cap_percentage)
    sponsor_contribution = excess_salary * (sponsor_rate / 100)

    return ContributionResult(
        participant_contribution=round(participant_contribution, 2),
        sponsor_contribution=round(sponsor_contribution, 2),
        total_contribution=round(
            participant_contribution + sponsor_contribution, 2
        ),
    )


def check_eligibility(years_of_service: float, age: int) -> dict:
    """
    Checks retirement eligibility under a typical CD/CV plan.

    Normal retirement: minimum 5 years of service and age 55+.
    Early retirement: minimum 5 years of service and age 45+.
    """
    has_minimum_service = years_of_service >= 5
    eligible_normal = has_minimum_service and age >= 55
    eligible_early = has_minimum_service and age >= 45

    if eligible_normal:
        status = "elegivel_normal"
    elif eligible_early:
        status = "elegivel_antecipada"
    elif not has_minimum_service:
        status = "tempo_de_vinculo_insuficiente"
    else:
        status = "idade_insuficiente"

    return {
        "eligible_normal_retirement": eligible_normal,
        "eligible_early_retirement": eligible_early,
        "status": status,
    }


def income_tax_rate(years_of_contribution: float) -> float:
    """
    Returns the applicable income tax rate under the regressive table
    commonly used for complementary pension benefits/withdrawals in Brazil.
    Rate decreases the longer the contribution has been held, bottoming out
    at 10% after 10 years.
    """
    brackets = [
        (2, 0.35),
        (4, 0.30),
        (6, 0.25),
        (8, 0.20),
        (10, 0.15),
    ]
    for max_years, rate in brackets:
        if years_of_contribution <= max_years:
            return rate
    return 0.10


def check_portability(years_of_service: float, minimum_years: float = 3) -> bool:
    """Portability is typically released after a minimum vesting period."""
    return years_of_service >= minimum_years


def check_bpd_eligibility(years_of_service: float, minimum_years: float = 3) -> dict:
    """
    Checks eligibility for BPD (Benefício Proporcional Diferido): a participant
    who leaves the sponsoring company before retirement age can leave their
    accumulated balance in the plan and collect it later as a deferred
    benefit, instead of an immediate resgate or portability.

    Uses the same minimum vesting period as portability by default, since
    both institutos share the same underlying vesting logic in most CD/CV
    plans - only what the participant chooses to do with the balance differs.
    """
    eligible = years_of_service >= minimum_years
    return {
        "eligible_bpd": eligible,
        "minimum_years_required": minimum_years,
        "years_short": max(0.0, round(minimum_years - years_of_service, 2)),
    }


def calculate_peculio(
    salary: float, salary_multiplier: float = 24
) -> float:
    """
    Illustrative pecúlio (single lump-sum payment on death or invalidity)
    calculation, modeled as a configurable multiple of salary - a common
    structure across EFPC plans, though the exact multiplier is defined per
    plan regulation and not modeled here in detail (see README scope notes).

    Args:
        salary: gross monthly salary (BRL).
        salary_multiplier: number of salaries paid as pecúlio (plan-specific;
            24x is used here as an illustrative default).
    """
    return round(salary * salary_multiplier, 2)


def apply_annual_adjustment(
    value: float, index_rate: float, years: int = 1
) -> float:
    """
    Applies a compounding annual adjustment to a benefit value - e.g. the
    IPC-FGV index used for annual readjustment in plans like Valiaprev.

    Args:
        value: the benefit value before adjustment.
        index_rate: annual adjustment rate as a decimal (e.g. 0.045 for 4.5%).
        years: number of annual adjustments to apply (default 1).
    """
    return round(value * (1 + index_rate) ** years, 2)


def simulate_balance_growth(
    salary: float,
    participant_percentage: float,
    ur_value: float,
    years: int,
    annual_return_rate: float,
) -> list[float]:
    """
    Simulates accumulated balance growth over time under simple monthly
    contributions compounded at a fixed annual return rate. Returns the
    year-end balance for each year (index 0 = end of year 1).
    """
    monthly_return = (1 + annual_return_rate) ** (1 / 12) - 1
    balance = 0.0
    yearly_balances = []

    for year in range(1, years + 1):
        for _month in range(12):
            contribution = calculate_contribution(
                salary, participant_percentage, ur_value
            )
            balance = balance * (1 + monthly_return) + contribution.total_contribution
        yearly_balances.append(round(balance, 2))

    return yearly_balances
