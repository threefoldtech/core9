
from js9 import j

from JumpScale9.core.State import State


class StateFactory:

    def __init__(self):
        self.__jslocation__ = "j.data.state"
        self._cache = {}

    def get(self, path="/host/jumpscale9.toml"):
        """
        """
        st = State(j.tools.executorLocal)
        st._configPath = path
        st.configLoad()
        return st
