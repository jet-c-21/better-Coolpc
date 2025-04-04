"""
Author: Jet C.
GitHub: https://github.com/jet-c-21
Create Date: 2025-04-04

Naming logic from wider to smaller:

Family > Group > Category > Item

"""
import datetime
import pathlib

THIS_FILE_PATH = pathlib.Path(__file__).resolve()
THIS_FILE_PARENT_DIR = THIS_FILE_PATH.parent
output_dir = THIS_FILE_PARENT_DIR / "output"

import requests
from pyquery import PyQuery as pq

from pycoolpc import ItemData


def guess_item_el_type(item_el) -> str:
    if item_el.attr("disabled") == "disabled":
        if item_el.attr("style") is not None:
            return "note"
        else:
            return "category"
    else:
        return "item"

def get_updated_datetime(coolpc_updated_datetime_str: str) -> datetime.datetime:
    """
    Extract datetime from a CoolPC update string, e.g. "2025/4/4 12:20"

    :param coolpc_updated_datetime_str: string like "2025/4/4 12:20"
    :return: datetime.datetime object
    """
    # Keep only the part matching YYYY/MM/DD HH:MM
    match = re.search(r"\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}", coolpc_updated_datetime_str)
    if not match:
        raise ValueError(f"Invalid datetime string: {coolpc_updated_datetime_str}")

    return datetime.datetime.strptime(match.group(0), "%Y/%m/%d %H:%M")


def get_data():
    url = "https://www.coolpc.com.tw/evaluate.php"
    response = requests.get(url)
    response.encoding = "big5"  # raw data is encoded in big5

    html = response.text
    # html = response.text.encode("utf-8")
    doc = pq(html)

    main_table_header = doc("tr#thy")
    _up_datetime_str = main_table_header("font#Mdy").text().strip()
    updated_datetime = get_updated_datetime(_up_datetime_str)


    main_table = doc("tbody#tbdy")

    for row in main_table("tr").items():
        family_id = row("td.w").text()
        family_name = row("td.t").text()
        if not family_name:
            continue

        if not family_id:
            continue

        family_id = int(family_id)
        if family_id != 21:
            continue

        all_groups = row("td[nowrap] > select > optgroup").items()
        for group in all_groups:
            group_name = group.attr("label")
            category_name = None
            item_ls = []
            for item_el in group.items("option"):
                item_el_type = guess_item_el_type(item_el)
                if item_el_type == "category":
                    category_name = item_el.text()

                elif item_el_type == "item":
                    item_full_info = item_el("option").text()
                    item = ItemData(
                        family_id=family_id,
                        family_name=family_name,
                        group_name=group_name,
                        category_name=category_name,
                        item_full_info=item_full_info,
                    )
                    item_ls.append(item)

                elif item_el_type == "note":
                    last_item = item_ls[-1]
                    last_item.add_note(item_el.text())

                else:
                    raise Exception(f"Unknown item type: {item_el_type}")


            # for item in item_ls:
            #     print(item.model_dump_json(indent=4))
            #     break

            break

    # how to iterate main_table ?


if __name__ == "__main__":
    get_data()
