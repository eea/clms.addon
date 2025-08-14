"""Utils"""

import os


def get_env_var(env_var_name):
    """Return env var value"""
    env = os.environ.get
    value = env(env_var_name, None)
    return value
