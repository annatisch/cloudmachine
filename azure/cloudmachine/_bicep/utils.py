from typing import List, Dict, Any
import json
import random
import string


def resolve_value(value: Any, **params) -> str:
    try:
        value: str = value.resolve()
    except AttributeError:
        value: str = json.dumps(value).replace('"', "'")
    if params :
        resolved_params = {k: resolve_value(v) for k, v in params.items()}
        try:
            return value.format(**resolved_params)
        except IndexError:
            # This will happen if the value is a dict, like '{}'
            return value
    return value


def resolve_key(key: Any) -> str:
    try:
        return key.resolve()
    except AttributeError:
        if key.isidentifier():
            return key
        return f"'{key}'"


def generate_suffix(length: int = 5, /) -> str:
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length)
    ).lower()


def generate_name(seed: str, max_length: int = 20) -> str:
    return ''.join([random.Random(c).choice(string.ascii_lowercase) for c in resolve_value(seed)][:max_length])


def serialize(value: Any, indent: str = "", /, **params) -> str:
    bicep = ""
    if isinstance(value, dict):
        bicep += "{\n"
        bicep += serialize_dict(value, indent + "  ", **params)
        bicep += indent + "}\n"
    elif isinstance(value, list):
        bicep += "[\n"
        bicep += serialize_list(value, indent + "  ", **params)
        bicep += indent + "]\n"
    else:
        bicep += resolve_value(value, **params)
    return bicep


def serialize_list(list_val: List[Any], indent: str, /, **params) -> str:
    bicep = ""
    for item in list_val:
        if isinstance(item, dict):
            bicep += f"{indent}{{\n"
            bicep += serialize_dict(item, indent + '  ', **params)
            bicep += f"{indent}}}\n"
        elif isinstance(item, list):
            bicep += f"{indent}[\n"
            bicep += serialize_list(item, indent + '  ', **params)
            bicep += f"{indent}]\n"
        else:
            bicep += f"{indent}{resolve_value(item)}\n"
    return bicep


def serialize_dict(dict_val: Dict[str, Any], indent: str, /, **params) -> str:
    bicep = ""
    for key, value in dict_val.items():
        if isinstance(value, dict) and value:
            bicep += f"{indent}{key}: {{\n"
            bicep += serialize_dict(value, indent + '  ', **params)
            bicep += f"{indent}}}\n"
        elif isinstance(value, list) and value:
            bicep += f"{indent}{key}: [\n"
            bicep += serialize_list(value, indent + '  ', **params)
            bicep += f"{indent}]\n"
        else:
            bicep += f"{indent}{resolve_key(key)}: {resolve_value(value, **params)}\n"
    return bicep
