import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_DIR = DATA_DIR / "schemas"



def load_schema(schema_name: str) -> dict:
    schema_path = SCHEMA_DIR / f"{schema_name}.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data(data_name: str):
    """Load a JSON test-data file from data/<data_name>.json (e.g. parametrize cases)."""
    data_path = DATA_DIR / f"{data_name}.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)
