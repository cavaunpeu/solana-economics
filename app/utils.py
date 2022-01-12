from collections import deque
from enum import Enum
import os
from typing import Dict

from ruamel.yaml import YAML
import pandas as pd

from cadCAD.configuration import Configuration
from cadCAD.configuration.utils import config_sim
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor


def load_constants():
    config_path = os.path.join(os.path.dirname(__file__), "const.yaml")
    return YAML(typ="safe").load(open(config_path))


class CadCadSimulationBuilder:

    USER_ID = "streamlit"
    MODEL_ID = "solana-economics"
    EXEC_MODE = ExecutionMode()
    EXEC_CONTEXT = ExecutionContext(EXEC_MODE.single_proc)

    @classmethod
    def build(
        cls,
        system_params: Dict,
        initial_state: Dict,
        partial_state_update_blocks: Dict,
        steps_per_run: int = 100,
        num_runs: int = 1,
    ):
        # Build config
        config = Configuration(
            user_id=cls.USER_ID,
            model_id=cls.MODEL_ID,
            subset_id=None,
            subset_window=deque([0, None]),
            run_id=0,
            initial_state=initial_state,
            partial_state_update_blocks=partial_state_update_blocks,
            sim_config={"T": range(steps_per_run), "N": num_runs, "M": system_params},
        )
        # Define executor
        executor = Executor(cls.EXEC_CONTEXT, [config])
        return CadCadSimulation(executor)


class CadCadSimulation:
    def __init__(self, executor):
        self.executor = executor

    def run(self):
        flat_results, tensor_fields, sessions = self.executor.execute()
        df = pd.DataFrame(flat_results)
        return df
