def escape_like_param(value: str) -> str:
    escapes = {
        '%': '\\%',
        '_': '\\_',
        '\\': '\\\\',
    }
    for char, escaped in escapes.items():
        value = value.replace(char, escaped)
    return value