def s_inflation(params, substep, state_history, previous_state, policy_input):
    """
    Update token inflation.

    If we start with 100 tokens, and inflation is 7%, then next year
    the system will have 107 tokens, where new tokens are distributed
    to stakers.
    """
    params,   = params  # I don't know why this is necessary.
    base_rate = params['base_infl_rate']
    grow_rate = params['dis_infl_rate']
    ltr       = params['long_term_infl_rate']
    timestep  = len(state_history)

    inflation = max(
      base_rate * (1 + grow_rate)**timestep,
      ltr
    )
    return 'inflation', inflation