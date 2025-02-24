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
from typing import Any, Callable, Mapping, Optional, Union, List
import os

from azure.core.settings import _unset, _Unset, PrioritizedSetting, ValidInputType, ValueType

from ._bicep.expressions import Parameter, MISSING, Expression


class StoredPrioritizedSetting(PrioritizedSetting):
    suffix: str

    def __init__(
        self,
        name: str,
        *,
        suffix: str = "",
        env_var: Optional[str] = None,
        env_vars: Optional[List[str]] = None,
        system_hook: Optional[Callable[[], ValidInputType]] = None,
        default: Union[ValidInputType, _Unset] = _unset,
        user_value: Union[ValidInputType, _Unset] = _unset,
        convert: Optional[Callable[[Union[ValidInputType, str]], ValueType]] = None,
    ):
        super().__init__(
            name=name,
            env_var=env_var,
            system_hook=system_hook,
            default=default,
            convert=convert,
        )
        self.suffix = suffix or ""
        self._user_value = user_value
        self._env_vars = env_vars or []

    def __call__(self, value: Optional[ValidInputType] = None, *, config_store: Optional[Mapping[str, Any]] = None) -> ValueType:
        """Return the setting value according to the standard precedence.

        :param value: value
        :type value: str or int or float or None
        :returns: the value of the setting
        :rtype: str or int or float
        :raises: RuntimeError if no value can be determined
        """
        settingvalue = self._raw_value(value, config_store=config_store)
        return self._convert(settingvalue)

    def _convert_parameter(self, value: Parameter[ValidInputType], *, config_store) -> ValidInputType:
        varname = value._varname or value.name
        if varname in config_store:
            return config_store[varname]
        if value.default is not MISSING and not isinstance(value.default, Expression):
            return value.default
        raise RuntimeError(f"No value for parameter {varname} found in config store.")

    def _raw_value(self, value: Optional[ValidInputType] = None, *, config_store) -> ValidInputType:
        # 5. immediate values
        if value is not None:
            if isinstance(value, Parameter):
                return self._convert_parameter(value, config_store=config_store or {})
            return value

        # 4. previously user-set value
        if not isinstance(self._user_value, _Unset):
            if isinstance(self._user_value, Parameter):
                return self._convert_parameter(self._user_value, config_store=config_store or {})
            return self._user_value

        # 3. check a config store
        if config_store:
            for env_var in self._env_vars:
                if env_var + self.suffix in config_store:
                    return config_store[env_var + self.suffix]
            if self._env_var and self._env_var in config_store:
                return config_store[self._env_var + self.suffix]

        # 2. environment variable
        for env_var in self._env_vars:
            if env_var + self.suffix in os.environ:
                return os.environ[env_var + self.suffix]
        if self._env_var and self._env_var in os.environ:
            return os.environ[self._env_var]

        # 1. system setting
        if self._system_hook:
            try:
                value = self._system_hook(config_store=config_store)
                if isinstance(value, Parameter):
                    return self._convert_parameter(value, config_store=config_store or {})
                return value
            except RuntimeError:
                pass

        # 0. implicit default
        if not isinstance(self._default, _Unset):
            return self._default

        all_vars = "\n".join([e + self.suffix for e in self._env_vars])
        all_vars += "\n" if all_vars else ""
        if self._env_var:
            all_vars += f"{self._env_var}\n"
        message = f"No configured value found for setting {self._name!r}.\nChecked the following settings:\n{all_vars}"
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
