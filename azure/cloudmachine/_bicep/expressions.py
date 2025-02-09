import json
from typing import Dict, List, Type, TypeVar, Generic, Literal, Optional, Any, Union
from enum import StrEnum

from .utils import resolve_value, serialize

BicepDataTypes = Literal["string", "array", "object", "int", "bool"]

class ParameterDefault(StrEnum):
    MISSING = 'None'

MISSING = ParameterDefault.MISSING


class Expression:
    def __init__(self, value: Union['Expression', str], /) -> None:
        self._value = value

    def __eq__(self, value: Any) -> bool:
        try:
            self.value == value.value
        except AttributeError:
            return False

    def __repr__(self) -> str:
        return resolve_value(self._value)

    def __hash__(self):
        return hash(self.value)

    def _resolve_expression(self, expression: Union['Expression', str]):
        try:
            return expression.value
        except AttributeError:
            return expression

    def _resolve_obj(self, value: Union['Expression', Any]):
        try:
            return value.value
        except AttributeError:
            return serialize(value)

    @property
    def value(self) -> str:
        return self._resolve_expression(self._value)
    
    def format(
            self,
            *,
            prefix: Union['Expression', str] = "",
            suffix: Union['Expression', str] = "",
    ) -> str:
        return f"{self._resolve_expression(prefix)}${{{self.value}}}{self._resolve_expression(suffix)}"


class Subscription(Expression):
    def __init__(self, subscription: Optional[Union[Expression, str]] = None, /):
        self._sub = subscription

    def __repr__(self) -> str:
        return f"subscription({self._sub})"

    @property
    def value(self) -> str:
        if self._sub:
            return f"subscription({resolve_value(self._sub)})"
        return f"subscription()"

    @property
    def subscription_id(self) -> Expression:
        return Expression(f"{self.value}.subscriptionId")


class ResourceSymbol(Expression):
    def __init__(
            self,
            value: str,
            *,
            principal_id: bool = False,
    ) -> None:
        self._value = value
        self._principal_id_output = principal_id 

    def __repr__(self) -> str:
        return f"resource({self._value})"

    @property
    def value(self) -> str:
        return self._value

    @property
    def name(self) -> 'Output[str]':
        return Output("name", self)

    @property
    def id(self) -> 'Output[str]':
        return Output("id", self)

    @property
    def principal_id(self) -> 'Output[str]':
        if not self._principal_id_output:
            raise ValueError("Module has no principal ID output.")
        return Output("principalId", self)


class Variable(Expression):
    def __init__(
            self,
            name: str,
            type: str,
            value: Any,
            *,
            description: Optional[str] = None
    ):
        self._name = name
        self._type = type
        self._value = value
        self._description = description

    def __repr__(self) -> str:
        return f"var({self._name})"

    def __str__(self) -> str:
        return self._name

    def __eq__(self, value):
        if isinstance(value, Variable):
            return self._name == value._name and self._type == value._type
        return False

    def __hash__(self):
        return hash((self._name, self._type))

    def main_declare(self) -> str:
        declaration = ""
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        declaration += f"var {self._name} = "
        declaration += serialize(self._value)
        declaration += "\n\n"
        return declaration

    def module_declare(self) -> str:
        return f"param {self._name} {self._type}\n"

    def resolve(self) -> str:
        return self._name


ParameterType = TypeVar("ParameterType", str, int, bool, dict, list, None)
class Parameter(Expression, Generic[ParameterType]):
    name: str
    type: str
    default: Optional[ParameterType]

    def __init__(
            self,
            name: str,
            *,
            type: Type[ParameterType] = str,
            default: ParameterType = MISSING,
            secure: bool = False,
            description: Optional[str] = None,
            varname: Optional[str] = None,
            allowed: Optional[List[int]] = None,
            max_value: Optional[int] = None,
            min_value: Optional[int] = None,
            max_length: Optional[int] = None,
            min_length: Optional[int] = None,
    ):
        self.name = name
        self.default = default
        self._type = type
        self._secure = secure
        self._description = description
        self._varname = varname
        self._allowed = allowed
        self._max_value = max_value
        self._min_value = min_value
        self._max_length = max_length
        self._min_length = min_length

    @property
    def value(self) -> str:
        return self.name

    @property
    def type(self) -> str:
        if self._type is str:
            return "string"
        if self._type is bool:
            return "boolean"
        if self._type is list:
            return "array"
        if self._type is int:
            return "int"
        if self._type is dict:
            return "object"
        else:
            raise TypeError(f"Unrecognized parameter type: '{self._type}'.")

    def __repr__(self) -> str:
        if self.default is not MISSING:
            return f"parameter({self.name}={self.default})"
        return f"parameter({self.name})"

    def __bicep(self) -> str:
        declaration = ""
        if self._secure:
            declaration += "@sys.secure()\n"
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        if self._allowed:
            declaration += "@sys.allowed([\n"
            for value in self._allowed:
                if isinstance(value, str):
                    clean_value = "'" + json.dumps(value).strip('"') + "'"
                else:
                    clean_value = json.dumps(value)
                declaration += f"  {clean_value}\n"
            declaration += "])\n"
        if self._max_value is not None:
            declaration += f"@sys.maxValue({self._max_value})\n"
        if self._min_value is not None:
            declaration += f"@sys.minValue({self._min_value})\n"
        if self._max_length is not None:
            declaration += f"@sys.maxLength({self._max_length})\n"
        if self._min_length is not None:
            declaration += f"@sys.minLength({self._min_length})\n"
        declaration += f"param {self.name} {self.type}"
        if self.default is not MISSING:
            declaration += " = "
            declaration += serialize(self.default)
        declaration += "\n\n"
        return declaration

    def __obj(self) -> Dict[str, Dict[str, str]]:
        if not self._varname:
            return {}
        value = f"${{{self._varname}={self.default}}}" if self.default else f"${{{self._varname}}}"
        return {
            self.name: {
                "value": value
            }
        }

class Output(Parameter[ParameterType]):
    def __init__(
            self,
            name: str,
            path: Union[Expression, str],
            symbol: Optional[ResourceSymbol] = None,
            *,
            type: Type[ParameterType] = str,
            description: Optional[str] = None
    ) -> None:
        self.symbol = symbol
        self._path = path
        super().__init__(name=name, type=type, description=description)

    def __repr__(self) -> str:
        return f"output({self.name}, {self.type})"

    @property
    def value(self) -> str:
        if self.symbol:
            return f"{self.symbol.name}.{self._path}"
        value = self._resolve_expression(self._path)
        return value

    def __bicep(self) -> str:
        declaration = ""
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        return declaration


class Guid(Parameter[str]):
    def __init__(self, basestr: Union[Expression, str], *args: Union[Expression, str]) -> None:
        self._args = [basestr] + list(args)

    def __repr__(self):
        return f"guid({self._args[0]}, ...)"

    @property
    def type(self) -> str:
        return "string"

    @property
    def value(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"guid({arg_str})"


class UniqueString(Parameter[str]):
    def __init__(self, basestr: Union[Expression, str], *args: Union[Expression, str]) -> None:
        self._args = [basestr] + list(args)

    def __repr__(self):
        return f"uniqueString({self._args[0]}, ...)"

    @property
    def type(self) -> str:
        return "string"

    @property
    def value(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"uniqueString({arg_str})"
