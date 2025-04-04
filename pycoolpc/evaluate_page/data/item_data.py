import re
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class ItemData(BaseModel):
    family_id: int
    family_name: str
    group_name: str
    category_name: Optional[str]
    item_full_info: str

    item_brand: Optional[str] = None
    item_price: Optional[int] = None
    item_notes: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def extract_fields_from_full_info(self) -> "ItemData":
        self.item_brand = self._extract_brand_from_full_info()
        self.item_price = self._extract_price_from_full_info()
        return self

    def _extract_brand_from_full_info(self) -> Optional[str]:
        if self.item_full_info:
            return self.item_full_info.split(" ")[0]
        return None

    def _extract_price_from_full_info(self) -> Optional[int]:
        if self.item_full_info:
            match = re.search(r"\$([0-9,]+)", self.item_full_info)
            if match:
                return int(match.group(1).replace(",", ""))
        return None

    def add_note(self, s: str):
        self.item_notes.append(s)


if __name__ == "__main__":
    item = ItemData(
        family_id=21,
        family_name="音效卡｜電視卡(盒)｜影音",
        group_name="影像擷取卡/盒/器",
        category_name=None,
        item_full_info="伽利略【U3THVAC】USB3.0 影音擷取器 / 1080P 60 / USB-A、C / HDMI輸入, $490 ◆ ★",
    )

    print("Brand:", item.item_brand)  # → 伽利略【U3THVAC】USB3.0
    print("Price:", item.item_price)  # → 490
    item.add_note("Supports both USB-A and USB-C")
    print("Notes:", item.item_notes)
