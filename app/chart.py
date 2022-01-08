from abc import ABC, abstractclassmethod

import altair as alt
import streamlit as st


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
      scale=alt.Scale(domain=(-10, 10)),
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
      scale=alt.Scale(domain=(initial_valuation * .25, initial_valuation * 1.75)),
      title="U.S. Dollars ($)"
    ),
    color='cohort'
    ).properties(
      title={
        "text": "Capital Valuation Over Time",
      }
    )
    return cls(chart)
