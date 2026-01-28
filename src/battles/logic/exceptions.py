def Debug_AttributeError(
    value: int,
    module: str,
    class_name: str,
    func_name: str,
) -> AttributeError:
    return AttributeError(
        f"нет такого атрибута {value}\n"
        f"{module}\n"
        f"class: `{class_name}` method: `{func_name}`\n"
    )
