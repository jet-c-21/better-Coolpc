"""
Author: Jet C.
GitHub: https://github.com/jet-c-21
Create Date: 2025-04-04
"""

import datetime
import re
from typing import Dict, Optional

import requests
from pyquery import PyQuery
from pyquery import PyQuery as pq

from pycoolpc.item import Item


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

        response = requests.get(url)
        response.encoding = "big5"
        html = response.text

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

    def get_data(self):
        """

        what will the professinal developer desing the result structure for the page data?

        :return:
        """
        result = {}

        doc = self.get_doc(self.url)
        main_table_header = doc("tr#thy")
        _up_datetime_str = main_table_header("font#Mdy").text().strip()
        updated_datetime = self.get_updated_datetime(_up_datetime_str)

        main_table = doc("tbody#tbdy")
        for row in main_table("tr").items():
            family_id = row("td.w").text()
            family_name = row("td.t").text()
            if not family_name:
                continue

            if not family_id:
                continue

            family_id = int(family_id)

            # # !@# for debug
            # if family_id != 21:
            #     continue

            groups_in_family = row("td[nowrap] > select > optgroup").items()
            self._parse_family_el(family_id, family_name, groups_in_family)

    def _parse_family_el(self, family_id: int, family_name: str, groups_in_family: PyQuery) -> Dict:
        group_to_items = {}
        for group in groups_in_family:
            group_name = group.attr("label")
            category_name = None
            item_ls = []
            for item_el in group.items("option"):
                item_el_type = self.guess_item_el_type(item_el)
                if item_el_type == "category":
                    category_name = item_el.text()

                elif item_el_type == "item":
                    item_full_info = item_el("option").text()
                    item = Item(
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

            group_to_items[group_name] = item_ls

        return group_to_items


if __name__ == "__main__":
    parser = EvaluatePageParser()
    items = parser.get_data()
