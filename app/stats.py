from collections import OrderedDict

from millify import millify
import numpy as np


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
  'staker_yield': {
    'label': 'Staker Yield',
    'delta_func': lambda curr, prev: (curr - prev) / prev,
    'format_func': format_float_stat
  }
})