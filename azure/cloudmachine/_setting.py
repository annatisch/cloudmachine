# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Provide access to settings for globally used Azure configuration values.
"""
from typing import Any, Awaitable, Callable, Literal, Mapping, Optional, Dict, Union, List, overload
import os

from azure.core.settings import _unset, _Unset, PrioritizedSetting, ValidInputType, ValueType


class StoredPrioritizedSetting(PrioritizedSetting):
    config_stores: List[Mapping[str, Any]]
    suffix: str

    def __init__(
        self,
        name: str,
        *,
        suffix: str = "",
        to_str: Optional[Callable[[ValidInputType], str]] = None,
        env_var: Optional[str] = None,
        env_vars: Optional[List[str]] = None,
        system_hook: Optional[Callable[[], ValidInputType]] = None,
        default: Union[ValidInputType, _Unset] = _unset,
        convert: Optional[Callable[[Union[ValidInputType, str]], ValueType]] = None,
        resource_outputs: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            name=name,
            env_var=env_var,
            system_hook=system_hook,
            default=default,
            convert=convert
        )
        self.suffix = suffix
        self._tostr = to_str or str
        self._env_vars = env_vars or []
        self._resource_outputs = resource_outputs or {}
        self.config_stores = []
        self._is_output = False
        if self._env_var in self._resource_outputs or [e for e in self._env_vars if e in self._resource_outputs]:
            self._is_output = True

    def __call__(self, value: Optional[ValidInputType] = None) -> ValueType:
        """Return the setting value according to the standard precedence.

        :param value: value
        :type value: str or int or float or None
        :returns: the value of the setting
        :rtype: str or int or float
        :raises: RuntimeError if no value can be determined
        """
        settingvalue = self._raw_value(value)
        return self._convert(settingvalue)

    def _raw_value(self, value: Optional[ValidInputType] = None) -> ValidInputType:
        # 5. immediate values
        if value is not None:
            return value

        # 4. previously user-set value
        if not isinstance(self._user_value, _Unset):
            return self._user_value

        # 3. check a config store
        if self.config_stores:
            for store in self.config_stores:
                for env_var in self._env_vars:
                    if env_var + self.suffix in store:
                        return store[env_var + self.suffix]
                if self._env_var and self._env_var in store:
                    return store[self._env_var + self.suffix]

        # 2. environment variable
        for env_var in self._env_vars:
            if env_var + self.suffix in os.environ:
                return os.environ[env_var + self.suffix]
        if self._env_var and self._env_var + self.suffix in os.environ:
            return os.environ[self._env_var + self.suffix]

        # 1. system setting
        if self._system_hook:
            return self._system_hook()

        # 0. implicit default
        if not isinstance(self._default, _Unset):
            return self._default

        all_vars = "\n".join([e + self.suffix for e in self._env_vars])
        if self._env_var:
            all_vars + f"\n{self._env_var + self.suffix}"
        message = f"No configured value found for setting {self._name!r}.\nChecked the following settings:\n{all_vars}"
        if self._is_output:
            message += f"\nYou may need to run the 'provision' command to populate resource settings."
        raise RuntimeError(message)

    def set_value(self, value: Union[PrioritizedSetting[ValidInputType, ValueType], ValidInputType]) -> None:
        """Specify a value for this setting programmatically.

        A value set this way takes precedence over all other methods except
        immediate values.

        :param value: a user-set value for this setting
        :type value: str or int or float
        """
        if isinstance(value, PrioritizedSetting):
            self._user_value = value._user_value
        else:
            self._user_value = value

    def to_dict(self) -> Dict[str, Union[str, float, int, bool, None]]:
        value = self._raw_value()
        if isinstance(value, (str, int, float, bool)):
            return {self._name: value}
        return {self._name: self._tostr(value)}
        
    def to_config(self) -> Dict[str, Union[str, float, int, bool, None]]:
        key: str
        if self._env_var:
            key = self._env_var
        elif self._env_vars:
            key = self._env_vars[0]
        else:
            key = self._name.upper()
        value = self._raw_value()
        if isinstance(value, (str, int, float, bool)):
            return {key: value}
        return {key: self._tostr(value)}

    def dump(
            self,
            *,
            read_env: bool = False,
            include_sensitive: bool = False
    ) -> Dict[str, str]:
        try:
            if self._user_value:
                return {self._name: self._tostr(self._user_value, include_sensitive)}
            if read_env and self.env_var and self.env_var in os.environ:
                return {self._name: self._tostr(os.environ[self.env_var], include_sensitive)}
            if not isinstance(self._default, (PrioritizedSetting, _Unset)):
                return {self._name: self._tostr(self._default, include_sensitive)}
        except RuntimeError:
            pass
        return {}
