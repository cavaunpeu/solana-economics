import streamlit as st
from ruamel.yaml import YAML

from model import s_inflation
from utils import CadCadSimulationBuilder

import os

CONFIG_PATH = os.path.join(
  os.path.dirname(__file__),
  'const.yaml'
)
C = CONSTANTS = YAML(typ='safe').load(open(CONFIG_PATH))


# Define sidebar

base_infl_rate      = st.sidebar.slider("Base inflation rate", 0., 20., C['base_inflation_rate'] * 100, .5) / 100
dis_infl_rate       = st.sidebar.slider("Disinflation rate", -20., 0., C['disinflation_rate'] * 100, .5) / 100
long_term_infl_rate = st.sidebar.slider("Long-term inflation rate", 0., 20., C['long_term_inflation_rate'] * 100, .5) / 100

# Data validation

errors = []

if long_term_infl_rate > base_infl_rate:
    errors.append(
        lambda: st.error('Long-term inflation rate must be <= base inflation rate')
    )

# Define simulation model

simulation = CadCadSimulationBuilder.build(
    system_params={
        'base_infl_rate': base_infl_rate,
        'dis_infl_rate': dis_infl_rate,
        'long_term_infl_rate': long_term_infl_rate,
    },
    initial_state={
        'inflation': base_infl_rate
    },
    partial_state_update_blocks=[
        {
            'policies': {},
            'variables': {
                'inflation': s_inflation,
            }
        }
    ]
)

df = simulation.run()

import pdb; pdb.set_trace()