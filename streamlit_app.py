"""
streamlit_app.py

Interactive frontend for the EFPC benefits simulator. Lets a user enter
salary, contribution percentage, service time and age, and see contribution
split, eligibility, portability, applicable income tax bracket, and a
balance growth projection - all computed by efpc_calculator.py.

Run with:
    streamlit run streamlit_app.py
"""

import matplotlib.pyplot as plt
import streamlit as st

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

st.set_page_config(page_title="EFPC Benefits Simulator", page_icon="📊")

st.title("EFPC Benefits Simulator")
st.caption(
    "Simulador de contribuição, elegibilidade e tributação para planos de "
    "previdência complementar fechada (CD/CV) no Brasil."
)

with st.sidebar:
    st.header("Parâmetros")
    salary = st.number_input("Salário (R$)", min_value=0.0, value=8000.0, step=100.0)
    ur_value = st.number_input("Valor da UR (R$)", min_value=1.0, value=100.0, step=1.0)
    participant_percentage = st.slider(
        "Percentual de contribuição escolhido (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5
    )
    years_of_service = st.number_input("Anos de vínculo/contribuição", min_value=0.0, value=6.0, step=1.0)
    age = st.number_input("Idade", min_value=18, max_value=90, value=47)
    annual_return_rate = st.slider(
        "Taxa de retorno anual estimada (%)", min_value=0.0, max_value=15.0, value=6.0, step=0.5
    ) / 100
    projection_years = st.slider("Anos de projeção", min_value=1, max_value=40, value=30)

contribution = calculate_contribution(salary, participant_percentage, ur_value)
eligibility = check_eligibility(years_of_service, age)
portable = check_portability(years_of_service)
ir_rate = income_tax_rate(years_of_service)

col1, col2, col3 = st.columns(3)
col1.metric("Contribuição do participante", f"R$ {contribution.participant_contribution:,.2f}")
col2.metric("Contrapartida da patrocinadora", f"R$ {contribution.sponsor_contribution:,.2f}")
col3.metric("Contribuição total mensal", f"R$ {contribution.total_contribution:,.2f}")

st.subheader("Elegibilidade e regras")
status_labels = {
    "elegivel_normal": "✅ Elegível para aposentadoria normal (55+, 5+ anos)",
    "elegivel_antecipada": "✅ Elegível para aposentadoria antecipada (45+, 5+ anos)",
    "tempo_de_vinculo_insuficiente": "⏳ Tempo de vínculo ainda insuficiente (mínimo 5 anos)",
    "idade_insuficiente": "⏳ Idade ainda insuficiente para os requisitos atuais",
}
st.write(status_labels[eligibility["status"]])
st.write("✅ Portabilidade liberada" if portable else "⏳ Portabilidade ainda não liberada (mínimo 3 anos)")
st.write(f"Alíquota de IR aplicável (tabela regressiva): **{ir_rate:.0%}**")

bpd = check_bpd_eligibility(years_of_service)
if bpd["eligible_bpd"]:
    st.write("✅ Elegível para BPD (Benefício Proporcional Diferido)")
else:
    st.write(
        f"⏳ BPD ainda não liberado (faltam {bpd['years_short']:.1f} ano(s) "
        f"de vínculo)"
    )

with st.expander("Pecúlio e reajuste anual (institutos adicionais)"):
    peculio_multiplier = st.slider(
        "Múltiplo do salário para pecúlio", min_value=1, max_value=48, value=24
    )
    peculio = calculate_peculio(salary, peculio_multiplier)
    st.write(f"Pecúlio ilustrativo (morte/invalidez): **R$ {peculio:,.2f}**")

    st.divider()
    adjustment_index = st.slider(
        "Índice de reajuste anual (%) — ex.: IPC-FGV", min_value=0.0, max_value=15.0, value=4.5, step=0.1
    ) / 100
    adjustment_years = st.number_input("Anos de reajuste acumulado", min_value=1, max_value=30, value=1)
    adjusted_value = apply_annual_adjustment(
        contribution.total_contribution, adjustment_index, adjustment_years
    )
    st.write(
        f"Contribuição total corrigida após {adjustment_years} ano(s): "
        f"**R$ {adjusted_value:,.2f}**"
    )

st.subheader("Projeção de saldo acumulado")
balances = simulate_balance_growth(
    salary, participant_percentage, ur_value, projection_years, annual_return_rate
)
fig, ax = plt.subplots()
ax.plot(range(1, len(balances) + 1), balances, marker="o", markersize=3)
ax.set_xlabel("Anos de contribuição")
ax.set_ylabel("Saldo acumulado (R$)")
ax.grid(alpha=0.3)
st.pyplot(fig)

st.caption(
    "Projeto educacional/portfólio. Não substitui cálculo atuarial certificado "
    "(tábua biométrica, fator de conversão) - ver README para escopo completo."
)
