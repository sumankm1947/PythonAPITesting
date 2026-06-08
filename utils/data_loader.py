import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = PROJECT_ROOT / "data" / "schemas"



def load_schema(schema_name: str) -> dict:
    schema_path = SCHEMA_DIR / f"{schema_name}.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)



            