from collections import OrderedDict
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

st.sidebar.markdown('# Solana Economic Simulator')

run_simulation = st.sidebar.button("Run")

st.sidebar.markdown('## Progress')

progress_bar = st.sidebar.progress(0)
progress_text = st.sidebar.text('0.0% Complete')

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
assert df.index.tolist() == df['timestep'].tolist()

# Simulation params

num_steps = len(df)

# Define stats dashboard

format_float_stat = lambda stat: f"{(stat * 100).round(2).item()}%"
format_int_stat = lambda stat: stat

stat2meta = OrderedDict({
  'timestep': {
    'label': 'Timestep',
    'showdelta': False,
    'format_func': format_int_stat
  },
  'inflation': {
    'label': 'Inflation',
    'showdelta': True,
    'format_func': format_float_stat
  },
  'staker_yield': {
    'label': 'Yield',
    'showdelta': True,
    'format_func': format_float_stat
  },
})
stats_dboard = st.empty()


# Simulate

prevrow = None

for i in range(num_steps if run_simulation else 1):
  row = df.iloc[[i]]
  # Update stats
  cols = stats_dboard.columns(len(stat2meta))
  for ((stat, meta), col) in zip(stat2meta.items(), cols):
    if prevrow is not None and meta['showdelta']:
      delta = row[stat].item() - prevrow[stat].item()
      delta = f"{np.round(delta * 100, 2)}%"
    else:
      delta = None
    with col:
      st.metric(
        label=meta['label'],
        value=meta['format_func'](row[stat]),
        delta=delta
      )
  # Update plots
  if i == 0:
    inflation_plot = st.line_chart(row['inflation'])
  else:
    inflation_plot.add_rows(row['inflation'])
  # Finally
  if run_simulation:
    frac_complete = (i + 1) / num_steps
    time.sleep(.2)
    progress_bar.progress(frac_complete)
    progress_text.text(f'{(frac_complete * 100):.2f}% Complete')
    prevrow = row
