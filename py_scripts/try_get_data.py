"""
Author: Jet C.
GitHub: https://github.com/jet-c-21
Create Date: 2025-04-04
"""

import requests

def get_data():
    url = "https://www.coolpc.com.tw/evaluate.php"
    response = requests.get(url)

    # Fetch the HTML content
    response = requests.get(url)
    response.encoding = "big5"  # The page encoding is Big5
    html = response.text

    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Extract items and prices (this depends on the actual HTML structure)
    # Here is a generalized example (the actual selectors may need adjustment):

    items = []
    for tr in soup.select("table tr"):
        columns = tr.select("td")
        if len(columns) >= 2:
            item_name = columns[0].get_text(strip=True)
            item_price = columns[1].get_text(strip=True)

            # Ensure item_price is numeric before adding
            if item_price.replace(",", "").isdigit():
                items.append(
                    {"item": item_name, "price": int(item_price.replace(",", ""))}
                )

    # Save as JSON
    with open("coolpc_items.json", "w", encoding="utf-8") as json_file:
        json.dump(items, json_file, ensure_ascii=False, indent=4)

    print(f"Extracted {len(items)} items.")


if __name__ == '__main__':
    get_data()