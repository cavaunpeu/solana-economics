def compute_staker_yield(inflation, uptime, commission, perc_staked):
  return inflation * uptime * (1 - commission) / perc_staked


def p_inflation(params, substep, state_history, previous_state):
    """
    Compute the % of token inflation that will occur over upcoming timestep.

    If we start with 100 tokens, and inflation is 7%, then next year
    the system will have 107 tokens, where new tokens are distributed
    to stakers.
    """
    params,   = params  # I don't know why this is necessary.
    base_rate = params['base_infl_rate']
    grow_rate = params['dis_infl_rate']
    ltr       = params['long_term_infl_rate']
    timestep  = previous_state['timestep'] + 1

    inflation = max(
      base_rate * (1 + grow_rate)**timestep,
      ltr
    )
    return {'inflation': inflation}


def p_perc_staked(params, substep, state_history, previous_state):
    """
    Computer percentage of total SOL that will be staked in upcoming timestep.

    New SOL issued via inflation is awarded to stakers, and is *automatically
    restaked.*
    """
    perc_staked = previous_state['perc_staked']
    return {'perc_staked': perc_staked}


def s_inflation(params, substep, state_history, previous_state, policy_input):
  return 'inflation', policy_input['inflation']


def s_perc_staked(params, substep, state_history, previous_state, policy_input):
  return 'perc_staked', policy_input['perc_staked']


def s_staker_yield(params, substep, state_history, previous_state, policy_input):
    """
    Update the staker yield.
    """
    params,   = params  # I don't know why this is necessary.
    commission = params['vdtr_comm_perc']
    uptime = params['vdtr_uptime_freq']
    inflation = policy_input['inflation']
    perc_staked = policy_input['perc_staked']

    staker_yield = compute_staker_yield(inflation, uptime, commission, perc_staked)
    return 'staker_yield', staker_yield


def s_total_supply(params, substep, state_history, previous_state, policy_input):
  return 'total_supply', previous_state['total_supply'] * (1 + previous_state['inflation'])