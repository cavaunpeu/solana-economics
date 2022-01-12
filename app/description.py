import streamlit as st

from chart import StakePropensityChart


def description(yield_location, yield_scale):
  st.markdown('## Description')

  st.write("""
  In Solana, new SOL are minted on a given inflation schedule. These SOL are then distributed to those who "stake" their existing coins: participating in, or delegating to a validator who participates in, the validator of transactions on the Solana blockchain.

  In this vein, staking SOL has a positive, dynamic yield. Conversely, the value of unstaked SOL is continuously diluted.

  For more information on this system, please refer to the [Solana Economics Overview](https://docs.solana.com/economics_overview).
  """)

  st.markdown('## Simulation')

  st.write("""

  Below, we simulate this process. On the left, you can choose the "Staked" and "Unstaked" policy: the logic used to update ones strategy in this game.

  In the *proactive* policy, we define a participant's propensity to change their behavior varies with the staker yield in the previous timestep.
  """)

  st.altair_chart(
    StakePropensityChart.build(yield_location, yield_scale),
    use_container_width=True
  )

  st.write("""
  In the *constant* policy, a participant's behavior remains constant throughout.
  """)

  st.markdown('## Cohort-based Modeling')

  st.write("""
  Please note, policies are not *agent-based*; instead, they are *cohort-based.*

  For instance, imagine our policies are:

  * Staked: Proactive
  * Unstaked: Constant

  In a given timestep, if a proportion of the `Staked` cohort updates their behavior to `Unstaked`, then their policy (Proactive) flips to that of the latter (Constant).
  """)

  st.markdown('## About')

  st.write("""
  This work is *not* affiliated with the official Solana project in any way.

  * [Author](https://willwolf.io/)
  * [Code](https://github.com/cavaunpeu/solana-economics)
  """)
