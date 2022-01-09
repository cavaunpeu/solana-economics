from abc import ABC, abstractclassmethod

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from model import compute_stake_propensity


class AltairChart(ABC):

  def __init__(self, chart, use_container_width=True):
    self.chart = st.altair_chart(chart, use_container_width=use_container_width)

  def add_rows(self, row):
    self.chart.add_rows(row)

  @abstractclassmethod
  def build(cls):
    raise NotImplementedError


class PercStakedAltairChart(AltairChart):

  def add_rows(self, row):
    self.chart.add_rows(self._preprocess(row))

  @classmethod
  def _preprocess(cls, row):
    return row.assign(perc_staked = row['perc_staked'] * 100)

  @classmethod
  def build(cls, df, num_steps):
    chart = alt.Chart(cls._preprocess(df)).mark_line().encode(
      x=alt.X('timestep',
        scale=alt.Scale(domain=(0, num_steps - 1)),
        axis=alt.Axis(tickMinStep = 1)
      ),
      y=alt.Y('perc_staked',
        scale=alt.Scale(domain=(0, 100)),
        title="% Total SOL Staked"
      )
    ).properties(
      title='% of Total SOL Staked Over Time'
    )
    return cls(chart)


class StakerYieldAltairChart(AltairChart):

  def add_rows(self, row):
    self.chart.add_rows(self._preprocess(row))

  @classmethod
  def _preprocess(cls, row):
    return row.assign(staker_yield = row['staker_yield'] * 100)

  @classmethod
  def build(cls, df, num_steps):
    chart = alt.Chart(cls._preprocess(df)).mark_line().encode(
      x=alt.X('timestep',
        scale=alt.Scale(domain=(0, num_steps - 1)),
        axis=alt.Axis(tickMinStep = 1)
      ),
      y=alt.Y('staker_yield',
        scale=alt.Scale(domain=(0, 20)),
        title="% Yield"
      )
    ).properties(
      title='% Yield on Staked Tokens'
    )
    return cls(chart)


class DilutionAltairChart(AltairChart):

  def add_rows(self, row):
    self.chart.add_rows(self._melt(row))

  @staticmethod
  def _melt(df):
    return df[['unstaked_dilution', 'staked_dilution', 'timestep']].melt(
      'timestep',
      var_name='cohort',
      value_name='dilution'
    ).assign(
      cohort = lambda df: df['cohort'].str.replace('_dilution', '')
    ).assign(
      dilution = lambda df: df['dilution'] * 100
    )

  @classmethod
  def build(cls, df, num_steps):
    chart = alt.Chart(
      cls._melt(df)
    ).mark_line().encode(
    x=alt.X('timestep',
      scale=alt.Scale(domain=(0, num_steps - 1))
    ),
    y=alt.Y('dilution',
      title="% Dilution"
    ),
    color='cohort'
    ).properties(
      title='Token Dilution Over Time'
    )
    return cls(chart)


class ValuationAltairChart(AltairChart):

  def add_rows(self, row):
    self.chart.add_rows(self._melt(row))

  @staticmethod
  def _melt(df):
    return df[['unstaked_valuation', 'staked_valuation', 'timestep']].melt(
      'timestep',
      var_name='cohort',
      value_name='valuation'
    ).assign(
      cohort = lambda df: df['cohort'].str.replace('_valuation', '')
    )

  @classmethod
  def build(cls, df, num_steps, initial_valuation):
    chart = alt.Chart(
      cls._melt(df)
    ).mark_line().encode(
    x=alt.X('timestep',
      scale=alt.Scale(domain=(0, num_steps - 1)),
      axis=alt.Axis(tickMinStep = 1)
    ),
    y=alt.Y('valuation',
      title="U.S. Dollars ($)"
    ),
    color='cohort'
    ).properties(
      title={
        "text": "Capital Valuation Over Time",
      }
    )
    return cls(chart)


class DilutionAltairChart(AltairChart):

  def add_rows(self, row):
    self.chart.add_rows(self._melt(row))

  @staticmethod
  def _melt(df):
    return df[['unstaked_dilution', 'staked_dilution', 'timestep']].melt(
      'timestep',
      var_name='cohort',
      value_name='dilution'
    ).assign(
      cohort = lambda df: df['cohort'].str.replace('_dilution', '')
    ).assign(
      dilution = lambda df: df['dilution'] * 100
    )

  @classmethod
  def build(cls, df, num_steps):
    chart = alt.Chart(
      cls._melt(df)
    ).mark_line().encode(
      x=alt.X('timestep',
        scale=alt.Scale(domain=(0, num_steps - 1))
      ),
      y=alt.Y('dilution',
        title="% Dilution"
      ),
      color='cohort'
    ).properties(
      title='Token Dilution Over Time'
    )
    return cls(chart)


class StakePropensityChart:

  YIELD_VALS = np.linspace(0, .16, 101)

  @classmethod
  def build(cls, yield_location, yield_scale):
    df = pd.DataFrame({
      'previous_yield': cls.YIELD_VALS * 100,
      'current_behavior': 'staked',
      'policy': 'proactive',
      'maintain_behavior_propensity': [compute_stake_propensity(prev_yield, yield_location, yield_scale) for prev_yield in cls.YIELD_VALS],
    }).pipe(
      lambda df: pd.concat([
        df,
        df.assign(
          maintain_behavior_propensity=1 - df['maintain_behavior_propensity'],
          current_behavior='unstaked'
        )
      ])
    )
    chart = alt.Chart(df).mark_line().encode(
      x=alt.X('previous_yield',
        scale=alt.Scale(domain=(df['previous_yield'].min(), df['previous_yield'].max())),
        title="Previous Yield %"
      ),
      y=alt.Y('maintain_behavior_propensity',
        title="Maintain Behavior Propensity"
      ),
      color='current_behavior'
    ).properties(
      title={
        "text": "Propensity to Maintain Behavior",
      }
    )
    return chart