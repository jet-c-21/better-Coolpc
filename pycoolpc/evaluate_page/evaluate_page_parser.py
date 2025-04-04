"""
Author: Jet C.
GitHub: https://github.com/jet-c-21
Create Date: 2025-04-04
"""

import datetime
import re
from typing import Dict, List, Optional

import requests
from charset_normalizer import from_bytes
from pyquery import PyQuery
from pyquery import PyQuery as pq

from pycoolpc.evaluate_page.data import ItemData


class EvaluatePageParser:
    EVALUATE_PAGE_URL = "https://www.coolpc.com.tw/evaluate.php"

    def __init__(self, url: Optional[str] = None):
        if url is None:
            self.url = EvaluatePageParser.EVALUATE_PAGE_URL
        else:
            self.url = url

    @staticmethod
    def get_doc(url: str) -> PyQuery:
        """
        Get the document from the given URL.
        If no URL is provided, use the default EVALUATE_PAGE_URL.
        """

        # response = requests.get(url)
        # response.encoding = "big5"
        # html = response.text

        response = requests.get(url)

        # Detect and decode with correct charset
        detected = from_bytes(response.content).best()
        html = detected._string  # This is a Unicode str decoded from Big5 or whatever was detected

        return pq(html)

    @staticmethod
    def guess_item_el_type(item_el) -> str:
        if item_el.attr("disabled") == "disabled":
            if item_el.attr("style") is not None:
                return "note"
            else:
                return "category"
        else:
            return "item"

    @staticmethod
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

    def get_data(self, specific_family_id: Optional[int] = None) -> Dict:
        """

        what will the professinal developer desing the result structure for the page data?

        :return:
        """
        doc = self.get_doc(self.url)
        main_table_header = doc("tr#thy")
        _up_datetime_str = main_table_header("font#Mdy").text().strip()
        updated_datetime = self.get_updated_datetime(_up_datetime_str)
        result = {
            "updated_datetime": updated_datetime.isoformat(),
            "families": [],
        }

        main_table = doc("tbody#tbdy")
        for row in main_table("tr").items():
            family_id = row("td.w").text()
            family_name = row("td.t").text()
            if family_name == "":
                continue

            if family_id == "":
                continue

            family_id = int(family_id)

            if specific_family_id is not None:
                if family_id != specific_family_id:
                    continue

            group_select_el_in_family = row("td[nowrap] > select")
            _parsed_groups = self._parse_family_el(family_id, family_name, group_select_el_in_family)

            family_dict = {
                "family_id": family_id,
                "family_name": family_name,
                "groups": _parsed_groups,
            }

            result["families"].append(family_dict)

        return result

    def _parse_family_el(
        self,
        family_id: int,
        family_name: str,
        groups_in_family: PyQuery,
        convert_item_data_to_dict=True,
    ) -> List[Dict]:
        group_ls = []
        for group in groups_in_family("optgroup").items():
            group_name = group.attr("label")
            category_name = None
            item_ls = []
            for item_el in group.items("option"):
                item_el_type = self.guess_item_el_type(item_el)
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

            group_dict = {
                "group_name": group_name,
                "items": item_ls,
            }

            if convert_item_data_to_dict:
                # Convert ItemData objects to dictionaries
                group_dict["items"] = [item.model_dump() for item in item_ls]

            group_ls.append(group_dict)

        return group_ls


if __name__ == "__main__":
    parser = EvaluatePageParser()
    data = parser.get_data()
    # print(data)
