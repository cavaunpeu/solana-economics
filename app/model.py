def compute_staker_yield(inflation, uptime, commission, perc_staked):
  return inflation * uptime * (1 - commission) / perc_staked


def compute_inflation(base_rate, grow_rate, ltr, timestep):
    """
    Compute the % of token inflation that will occur over upcoming timestep.

    If we start with 100 tokens, and inflation is 7%, then next year
    the system will have 107 tokens, where new tokens are distributed
    to stakers.
    """
    return max(
      base_rate * (1 + grow_rate)**timestep,
      ltr
    )


def p_staker_behavior(params, substep, state_history, previous_state):
    """
    Compute the % of total SOL that will be staked in upcoming timestep.

    New SOL issued via inflation is awarded to stakers, and is automatically
    restaked, *subject to the stakers withdrawing this stake.*
    """
    params,   = params  # I don't know why this is necessary.
    base_rate = params['base_infl_rate']
    grow_rate = params['dis_infl_rate']
    ltr       = params['long_term_infl_rate']
    timestep  = previous_state['timestep'] + 1

    inflation = compute_inflation(base_rate, grow_rate, ltr, timestep)
    total_supply = previous_state['total_supply'] * (1 + previous_state['inflation'])
    award = previous_state['total_supply'] * previous_state['inflation']
    new_stake = previous_state['sol_staked'] + award  # Change staker withdraw logic here.

    return {
      'sol_staked': new_stake,
      'perc_staked': new_stake / total_supply,
      'total_supply': total_supply,
      'inflation': inflation
    }


def s_perc_staked(params, substep, state_history, previous_state, policy_input):
  return 'perc_staked', policy_input['sol_staked'] / policy_input['total_supply']


def s_inflation(params, substep, state_history, previous_state, policy_input):
  return 'inflation', policy_input['inflation']


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
  return 'total_supply', policy_input['total_supply']


def s_sol_staked(params, substep, state_history, previous_state, policy_input):
  return 'sol_staked', policy_input['sol_staked']