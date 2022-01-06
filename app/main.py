import os
import time

import numpy as np
from ruamel.yaml import YAML
import streamlit as st

from model import (
  compute_staker_yield,
  p_inflation,
  p_perc_staked,
  s_inflation,
  s_perc_staked,
  s_staker_yield,
)
from utils import CadCadSimulationBuilder


CONFIG_PATH = os.path.join(
  os.path.dirname(__file__),
  'const.yaml'
)
C = CONSTANTS = YAML(typ='safe').load(open(CONFIG_PATH))


# Define sidebar

st.sidebar.markdown('## Economic parameters')

st.sidebar.markdown('### Staker')

init_perc_staked    = st.sidebar.slider("Initial percentage staked", 0., 100., C['initial_fraction_staked'] * 100., .5) / 100

st.sidebar.markdown('### Inflation')

base_infl_rate      = st.sidebar.slider("Base inflation rate", 0., 20., C['base_inflation_rate'] * 100., .5) / 100
dis_infl_rate       = st.sidebar.slider("Disinflation rate", -20., 0., C['disinflation_rate'] * 100., .5) / 100
long_term_infl_rate = st.sidebar.slider("Long-term inflation rate", 0., 20., C['long_term_inflation_rate'] * 100., .5) / 100

st.sidebar.markdown('### Validator')

vdtr_comm_perc      = st.sidebar.slider("Validator commission percentage", 0., 100., C['validator_commission_fraction'] * 100., .5) / 100
vdtr_uptime_freq    = st.sidebar.slider("Validator uptime frequency", 0., 100., C['validator_uptime_frequency'] * 100., .5) / 100

st.sidebar.markdown('## Simulate mint')

progress_bar = st.sidebar.progress(0)

# Data validation

errors = []

if long_term_infl_rate > base_infl_rate:
  errors.append(
      lambda: st.error('Long-term inflation rate must be <= base inflation rate')
  )

# Run simulation

TOTAL_YEARS = C['total_years']

simulation = CadCadSimulationBuilder.build(
    system_params={
        'base_infl_rate': base_infl_rate,
        'dis_infl_rate': dis_infl_rate,
        'long_term_infl_rate': long_term_infl_rate,
        'vdtr_comm_perc': vdtr_comm_perc,
        'vdtr_uptime_freq': vdtr_uptime_freq,
    },
    initial_state={
        'inflation': base_infl_rate,
        'perc_staked': init_perc_staked,
        'staker_yield': compute_staker_yield(
          base_infl_rate, vdtr_uptime_freq, vdtr_comm_perc, init_perc_staked
        )
    },
    partial_state_update_blocks=[
        {
            'policies': {
              'inflation': p_inflation,
              'perc_staked': p_perc_staked,
            },
            'variables': {
              'inflation': s_inflation,
              'perc_staked': s_perc_staked,
              'staker_yield': s_staker_yield,
            }
        }
    ],
    steps_per_run=TOTAL_YEARS
)

df = simulation.run()

# Plot results

row = df.iloc[[0]]
inflation_stat = st.empty()
inflation_plot = st.line_chart(row['inflation'])

for i in range(1, len(df)):
  nextrow = df.iloc[[i]]
  # Compute stats
  inflation_delta = nextrow['inflation'].item() - row['inflation'].item()
  inflation_stat.metric(
    label="Inflation",
    value=f"{(nextrow['inflation'] * 100).round(2).item()}%",
    delta=f"{np.round(inflation_delta * 100, 2)}%"
  )
  # Update plots
  inflation_plot.add_rows(nextrow['inflation'])
  # Finally
  time.sleep(.15)
  row = nextrow

