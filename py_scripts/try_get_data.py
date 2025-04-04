"""
Author: Jet C.
GitHub: https://github.com/jet-c-21
Create Date: 2025-04-04

Naming logic from wider to smaller:

Family > Group > Category > Item

"""

import pathlib

THIS_FILE_PATH = pathlib.Path(__file__).resolve()
THIS_FILE_PARENT_DIR = THIS_FILE_PATH.parent
output_dir = THIS_FILE_PARENT_DIR / "output"


import json

from pycoolpc.evaluate_page import EvaluatePageParser

if __name__ == "__main__":
    epp = EvaluatePageParser()
    data = epp.get_data(
        specific_family_id=9,
    )

    data_json_path = output_dir / "coolpc-data.json"
    data_json_path.parent.mkdir(parents=True, exist_ok=True)
    with data_json_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False))
