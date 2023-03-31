def preprocess_hocr(input_str: str) -> str:
    lines = input_str.split("\n")
    if lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines)