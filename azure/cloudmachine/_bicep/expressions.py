import json
from typing import Dict, List, TypeVar, Generic, Literal, Optional, Any, Union
from enum import Enum

from .utils import resolve_value, serialize

BicepDataTypes = Literal["string", "array", "object", "int", "bool"]


class Expression:
    def __init__(self, value: Union['Expression', str], /) -> None:
        self._value = value

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, Expression):
            return self._value == value._value
        return False

    def __hash__(self):
        return hash(self._value)

    def _resolve_ref(self, expression: Union['Expression', str]):
        try:
            return expression.resolve()
        except AttributeError:
            return expression

    def _resolve_obj(self, value: Union['Expression', Any]):
        try:
            return value.resolve()
        except AttributeError:
            return serialize(value)

    def resolve(self) -> str:
        return self._resolve_ref(self._value)
    
    def format(
            self,
            *,
            prefix: Union['Expression', str] = "",
            suffix: Union['Expression', str] = "",
    ) -> str:
        return f"{self._resolve_ref(prefix)}${{{self.resolve()}}}{self._resolve_ref(suffix)}"


class Subscription(Expression):
    def __init__(self, subscription: Optional[Union[Expression, str]] = None, /):
        self._sub = subscription

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, Subscription):
            return self._sub == value._sub
        return False

    def __hash__(self):
        return hash(self._sub)

    def resolve(self) -> str:
        if self._sub:
            return f"subscription({resolve_value(self._sub)})"
        return f"subscription()"

    @property
    def subscription_id(self) -> Expression:
        return Expression(f"{self.resolve()}.subscriptionId")


class Output(Expression):
    def __init__(
            self,
            path: Union[Expression, str],
            symbol: Optional[Expression] = None,
            resolve_to_str: bool = False
    ) -> None:
        self.symbol = symbol
        self._path = path
        self._to_str = resolve_to_str

    def __eq__(self, value):
        if isinstance(value, Output):
            return self._path == value._path and self.symbol == value.symbol
        return False

    def __hash__(self):
        return hash((self.symbol, self._path))

    def resolve(self) -> str:
        value = self._resolve_ref(self._path)
        if self.symbol:
            return f"{self.symbol.resolve()}.{self._path}"
        #if self._to_str:
        #    return f"'${value}'"
        return value

class ResourceSymbol(Expression):
    def __init__(
            self,
            value: str,
            *,
            name: str = "name",
            id: str = "id",
            principal_id: Optional[str] = None,
    ) -> None:
        self._value = value
        self._name_output = name
        self._id_output = id
        self._principal_id_output = principal_id 

    def __repr__(self) -> str:
        return f"Symbol({self._value})"

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, ResourceSymbol):
            return self._value == value._value
        return False

    def __hash__(self):
        return hash(self._value)

    def resolve(self) -> str:
        return self._value

    @property
    def name(self) -> Output:
        return Output(self._name_output, self)

    @property
    def id(self) -> Output:
        return Output(self._id_output, self)

    @property
    def principal_id(self) -> Output:
        if not self._principal_id_output:
            raise ValueError("Module has no principal ID output.")
        return Output(self._principal_id_output, self)


class ModuleSymbol(ResourceSymbol):
    def __init__(self, value: str, *, name: str = "outputs.name", id: str = "outputs.resourceId", principal_id = None):
        super().__init__(value, name=name, id=id, principal_id=principal_id)

class ResourceGroupSymbol(ModuleSymbol):
    def __init__(self, symbol: str, *, varname: str, varvalue: str):
        super().__init__(symbol)
        self._varname = varname
        self._varvalue = varvalue

    def __repr__(self) -> str:
        return f"ResourceGroup({self._varname})"

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, ResourceGroupSymbol):
            return self._varname == value._varname
        return False

    def __hash__(self):
        return hash(self._varname)

    # def resolve(self) -> str:
    #     return self._varname
    @property
    def varname(self) -> Expression:
        return Expression(self._varname)

    def declare(self) -> str:
        declaration = ""
        declaration += f"var {self._varname} = "
        declaration += serialize(self._varvalue)
        declaration += "\n\n"
        return declaration

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
        return f"Variable({self._name})"

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


class Parameter(Expression):
    def __init__(
            self,
            name: str,
            type: str,
            *,
            default: Optional[Any] = None,
            secure: bool = False,
            description: Optional[str] = None,
            varname: Optional[str] = None,
            allowed: Optional[List[int]] = None,
            max_value: Optional[int] = None,
            min_value: Optional[int] = None,
            max_length: Optional[int] = None,
            min_length: Optional[int] = None,
    ):
        self._name = name
        self._type = type
        self._default = default
        self._secure = secure
        self._description = description
        self._varname = varname
        self._allowed = allowed
        self._max_value = max_value
        self._min_value = min_value
        self._max_length = max_length
        self._min_length = min_length

    def __repr__(self) -> str:
        return f"Parameter({self._name})"

    def __eq__(self, value):
        if isinstance(value, Parameter):
            return self._name == value._name and self._type == value._type
        return False

    def __hash__(self):
        return hash((self._name, self._type))

    def main_declare(self) -> str:
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
        declaration += f"param {self._name} {self._type}"
        if self._default is not None:
            declaration += " = "
            declaration += serialize(self._default)
        declaration += "\n\n"
        return declaration

    def module_declare(self) -> str:
        return f"param {self._name} {self._type}\n"

    def parameter(self) -> Dict[str, Dict[str, str]]:
        if not self._varname:
            return {}
        value = f"${{{self._varname}={self._default}}}" if self._default else f"${{{self._varname}}}"
        return {
            self._name: {
                "value": value
            }
        }

    def resolve(self) -> str:
        return self._name


class Guid(Expression):
    def __init__(self, basestr: Union[Expression, str], *args: Union[Expression, str]) -> None:
        self._args = [basestr] + list(args)

    def __eq__(self, value):
        if isinstance(value, Guid):
            return self._args == value._args
        return False

    def __hash__(self):
        return hash(tuple(self._args))

    def resolve(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"guid({arg_str})"


class UniqueString(Expression):
    def __init__(self, basestr: Union[Expression, str], *args: Union[Expression, str]) -> None:
        self._args = [basestr] + list(args)

    def __eq__(self, value):
        if isinstance(value, UniqueString):
            return self._args == value._args
        return False

    def __hash__(self):
        return hash(tuple(self._args))

    def resolve(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"uniqueString({arg_str})"
