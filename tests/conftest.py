"""Auto-generated conftest — patches Reflex state for standalone testing."""

import functools
import reflex.state

_global_states: list = []


def _get_state_from_cache(self, state_cls):
    for state in _global_states:
        if isinstance(state, state_cls):
            return state
    state = state_cls(_reflex_internal_init=True)
    _global_states.append(state)
    return state


def _no_chain_background_task(state, _fn_name, fn):
    if isinstance(state, type):
        return functools.partial(fn, _get_state_from_cache(None, state))
    return functools.partial(fn, state)


reflex.state._no_chain_background_task = _no_chain_background_task


async def _aenter(self):
    return self


reflex.state.BaseState.__aenter__ = _aenter
reflex.state.BaseState._get_state_from_cache = _get_state_from_cache
_original_init = reflex.state.BaseState.__init__


def _new_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    _global_states.append(self)


reflex.state.BaseState.__init__ = _new_init
