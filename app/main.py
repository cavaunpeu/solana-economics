from collections import OrderedDict
import os
import time

import altair as alt
from millify import millify
import numpy as np
from ruamel.yaml import YAML
import streamlit as st

from model import (
  compute_staker_yield,
  compute_unstaked_dilution,
  compute_adjusted_staking_yield,
  p_staker_behavior,
  s_inflation,
  s_sol_staked,
  s_staker_yield,
  s_total_supply,
  s_perc_staked,
  s_unstaked_dilution,
  s_adjusted_staking_yield
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

st.sidebar.markdown('### Supply')

init_supply         = st.sidebar.slider("Initial SOL supply (100M)", 1., 10., C['initial_supply'] / 1e8, 1.) * 1e8

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
        'sol_staked': init_perc_staked * init_supply,
        'total_supply': init_supply,
        'staker_yield': compute_staker_yield(
          base_infl_rate, vdtr_uptime_freq, vdtr_comm_perc, init_perc_staked
        ),
        'unstaked_dilution': compute_unstaked_dilution(base_infl_rate),
        'adjusted_staking_yield': compute_adjusted_staking_yield(base_infl_rate, init_perc_staked)
    },
    partial_state_update_blocks=[
      {
            'policies': {
              'staker_behavior': p_staker_behavior,
            },
            'variables': {
              'sol_staked': s_sol_staked,
              'perc_staked': s_perc_staked,
              'total_supply': s_total_supply,
              'inflation': s_inflation,
              'staker_yield': s_staker_yield,
              'unstaked_dilution': s_unstaked_dilution,
              'adjusted_staking_yield': s_adjusted_staking_yield
            }
        }
    ],
    steps_per_run=TOTAL_YEARS
)

df = simulation.run()
assert df.index.tolist() == df['timestep'].tolist()
df.index.name = 'timestep'

# Simulation params

num_steps = len(df)

# Define stats dashboard

format_float_stat = lambda stat: f"{np.round(stat * 100, 2).item()}%"
format_int_stat = lambda stat: millify(stat)

stat2meta = OrderedDict({
  'timestep': {
    'label': 'Timestep',
    'delta_func': None,
    'format_func': format_int_stat
  },
  'total_supply': {
    'label': 'Total Supply',
    'delta_func': lambda curr, prev: curr - prev,
    'format_func': format_int_stat
  },
  'inflation': {
    'label': 'Inflation',
    'delta_func': lambda curr, prev: (curr - prev) / prev,
    'format_func': format_float_stat
  },
  'perc_staked': {
    'label': '% Staked',
    'delta_func': lambda curr, prev: (curr - prev) / prev,
    'format_func': format_float_stat
  },
})
stats_dboard = st.empty()

# Define plots

def build_perc_staked_plot(df):
  return alt.Chart(df).mark_line().encode(
    x=alt.X('timestep',
      scale=alt.Scale(domain=(0, num_steps - 1)),
      axis=alt.Axis(tickMinStep = 1)
    ),
    y=alt.Y('perc_staked',
      scale=alt.Scale(domain=(0, 1))
    )
  ).properties(
    title='% of Total SOL Staked Over Time'
  )

# Simulate

prevrow = None

for i in range(num_steps if run_simulation else 1):
  row = df.iloc[[i]]
  # Update stats
  cols = stats_dboard.columns(len(stat2meta))
  for ((stat, meta), col) in zip(stat2meta.items(), cols):
    if prevrow is not None and meta['delta_func'] is not None:
      delta = meta['delta_func'](row[stat].item(), prevrow[stat].item())
      delta = meta['format_func'](delta)
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
    perc_staked_plot = st.altair_chart(
      build_perc_staked_plot(row),
      use_container_width=True
    )
  else:
    perc_staked_plot.add_rows(row)
  # Finally
  if run_simulation:
    frac_complete = (i + 1) / num_steps
    time.sleep(C['speed'])
    progress_bar.progress(frac_complete)
    progress_text.text(f'{(frac_complete * 100):.2f}% Complete')
    prevrow = row
