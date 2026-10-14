import re

_NUMBER = re.compile(r"[-+−]?\s*(?:\d+[.,]?\d*|[.,]\d+)")  # «−» — типографский минус


def parse_number(text: str) -> float | None:
    """Первое число из строки, которую ввёл пользователь: «+0,5», «12 %», «-3.2°», «+1.5 EV». Нет числа — None."""
    m = _NUMBER.search(text)
    if not m:
        return None
    return float(m.group().replace(" ", "").replace(",", ".").replace("−", "-"))
