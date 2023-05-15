import jsonref
from typing import Tuple


def dereference_openapi_spec(spec: dict) -> dict:
    dereferenced_dict = jsonref.JsonRef.replace_refs(spec)
    return dereferenced_dict


def reduce_openapi_spec(spec: dict) -> dict:
    # Remove responses from spec
    for path, operations in spec["paths"].items():
        for operation_name, operation in operations.items():
            if "responses" in operation:
                operation.pop("responses")
    return spec



def get_spec_endpoints(spec: dict) -> list[dict]:
    endpoints = [
        (f"{operation_name.upper()} {route}", docs)
        for route, operation in spec["paths"].items()
        for operation_name, docs in operation.items()
        if operation_name in ["get", "post", "patch", "put", "delete"]
    ]
    return endpoints


def get_spec_title_and_version(spec: dict) -> Tuple[str, str]:
    title = spec["info"].get("title", "")
    version = spec["info"].get("version", "1.0.0")
    return title, version
