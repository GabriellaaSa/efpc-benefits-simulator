import pytest

from efpc_calculator import (
    apply_annual_adjustment,
    calculate_contribution,
    calculate_peculio,
    check_bpd_eligibility,
    check_eligibility,
    check_portability,
    income_tax_rate,
    simulate_balance_growth,
)


def test_contribution_below_threshold_uses_flat_rate():
    result = calculate_contribution(salary=500.0, participant_percentage=5.0, ur_value=100.0)
    assert result.participant_contribution == pytest.approx(5.0)
    assert result.sponsor_contribution == pytest.approx(0.0)


def test_contribution_above_threshold_splits_base_and_excess():
    result = calculate_contribution(salary=1500.0, participant_percentage=5.0, ur_value=100.0)
    assert result.participant_contribution == pytest.approx(10.0 + 25.0)
    assert result.sponsor_contribution == pytest.approx(25.0)


def test_sponsor_contribution_is_capped():
    result = calculate_contribution(
        salary=2000.0, participant_percentage=12.0, ur_value=100.0, sponsor_cap_percentage=9.0
    )
    assert result.sponsor_contribution == pytest.approx(1000.0 * 0.09)


def test_participant_percentage_below_minimum_raises():
    with pytest.raises(ValueError):
        calculate_contribution(salary=1000.0, participant_percentage=0.5, ur_value=100.0)


@pytest.mark.parametrize(
    "years,age,expected_status",
    [
        (6, 56, "elegivel_normal"),
        (6, 47, "elegivel_antecipada"),
        (2, 60, "tempo_de_vinculo_insuficiente"),
        (6, 30, "idade_insuficiente"),
    ],
)
def test_check_eligibility(years, age, expected_status):
    result = check_eligibility(years_of_service=years, age=age)
    assert result["status"] == expected_status


@pytest.mark.parametrize(
    "years,expected_rate",
    [
        (1, 0.35),
        (3, 0.30),
        (5, 0.25),
        (7, 0.20),
        (9, 0.15),
        (12, 0.10),
    ],
)
def test_income_tax_rate(years, expected_rate):
    assert income_tax_rate(years) == expected_rate


def test_portability_requires_minimum_years():
    assert check_portability(years_of_service=2) is False
    assert check_portability(years_of_service=3) is True


def test_simulate_balance_growth_is_monotonically_increasing():
    balances = simulate_balance_growth(
        salary=8000.0,
        participant_percentage=5.0,
        ur_value=100.0,
        years=5,
        annual_return_rate=0.06,
    )
    assert len(balances) == 5
    assert all(b2 > b1 for b1, b2 in zip(balances, balances[1:]))


def test_bpd_eligibility_below_minimum():
    result = check_bpd_eligibility(years_of_service=1.5)
    assert result["eligible_bpd"] is False
    assert result["years_short"] == pytest.approx(1.5)


def test_bpd_eligibility_at_minimum():
    result = check_bpd_eligibility(years_of_service=3)
    assert result["eligible_bpd"] is True
    assert result["years_short"] == 0.0


def test_peculio_uses_salary_multiplier():
    assert calculate_peculio(salary=5000.0) == pytest.approx(120000.0)
    assert calculate_peculio(salary=5000.0, salary_multiplier=12) == pytest.approx(60000.0)


def test_annual_adjustment_compounds_over_years():
    adjusted = apply_annual_adjustment(value=1000.0, index_rate=0.05, years=2)
    assert adjusted == pytest.approx(1102.50)


def test_annual_adjustment_single_year_default():
    adjusted = apply_annual_adjustment(value=1000.0, index_rate=0.045)
    assert adjusted == pytest.approx(1045.0)
