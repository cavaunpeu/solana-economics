from utils import load_constants


def compute_staker_yield(inflation, uptime, commission, perc_staked):
  return inflation * uptime * (1 - commission) / perc_staked


def compute_inflation_rate(base_rate, grow_rate, ltr, timestep):
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


def compute_unstaked_dilution(inflation):
  return -inflation / (1 + inflation)


def compute_staked_dilution(inflation, perc_staked):
  numer = (inflation / perc_staked) - inflation
  denom = 1 + inflation
  return numer / denom


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

  # Update parameters given previous timestep.
  inflation_prev = previous_state['inflation']
  perc_staked_prev = previous_state['perc_staked']
  unstaked_valuation = (1 + compute_unstaked_dilution(inflation_prev)) * previous_state['unstaked_valuation']
  staked_valuation = (1 + compute_staked_dilution(inflation_prev, perc_staked_prev)) * previous_state['staked_valuation']
  total_supply = previous_state['total_supply'] * (1 + inflation_prev)
  award = previous_state['total_supply'] * inflation_prev

  # Compute definite parameters for upcoming timestep.
  inflation = compute_inflation_rate(base_rate, grow_rate, ltr, timestep)

  # Compute tentative parameters for upcoming timestep.
  _sol_staked = previous_state['sol_staked'] + award
  _sol_unstaked = total_supply - _sol_staked

  # Update staked and unstaked behaviors.
  staked_keep_strat_frac = params['staked_policy'](previous_state['staker_yield'], behavior='staked')
  unstaked_keep_strat_frac = params['unstaked_policy'](previous_state['staker_yield'], behavior='unstaked')
  sol_staked = staked_keep_strat_frac * _sol_staked + (1 - unstaked_keep_strat_frac) * _sol_unstaked

  # Update definite parameters for current timestep.
  perc_staked = sol_staked / total_supply
  unstaked_dilution = compute_unstaked_dilution(inflation)
  staked_dilution = compute_staked_dilution(inflation, perc_staked)

  return {
    'sol_staked': sol_staked,
    'perc_staked': perc_staked,
    'total_supply': total_supply,
    'inflation': inflation,
    'unstaked_dilution': unstaked_dilution,
    'staked_dilution': staked_dilution,
    'unstaked_valuation': unstaked_valuation,
    'staked_valuation': staked_valuation,
  }
  return p_staker_behavior


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


def s_unstaked_dilution(params, substep, state_history, previous_state, policy_input):
  return 'unstaked_dilution', policy_input['unstaked_dilution']


def s_staked_dilution(params, substep, state_history, previous_state, policy_input):
  return 'staked_dilution', policy_input['staked_dilution']


def s_unstaked_valuation(params, substep, state_history, previous_state, policy_input):
  return 'unstaked_valuation', policy_input['unstaked_valuation']


def s_staked_valuation(params, substep, state_history, previous_state, policy_input):
  return 'staked_valuation', policy_input['staked_valuation']


CONSTANTS = load_constants()


def constant_stake_policy(previous_yield, behavior):
  """
  There are two behaviors in the network: to be staked or unstaked.

  This policy computes the probability that a given member maintains
  their current behavior.
  """
  return 1

def proactive_stake_policy(previous_yield, behavior):
  """
  There are two behaviors in the network: to be staked or unstaked.

  This policy computes the probability that a given member maintains
  their current behavior.
  """
