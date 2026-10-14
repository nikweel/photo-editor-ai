import json

from .paths import DATA_DIR

FILE = DATA_DIR / "settings.json"


def get(key: str, default=None):
    try:
        return json.loads(FILE.read_text(encoding="utf-8")).get(key, default)
    except Exception:
        return default


def put(key: str, value) -> None:
    try:
        data = json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    data[key] = value
    try:
        FILE.parent.mkdir(parents=True, exist_ok=True)
        FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
