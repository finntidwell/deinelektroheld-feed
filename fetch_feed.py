import csv
import os
import requests

EMAIL = os.environ["CONNECTIVO_EMAIL"]
PASSWORD = os.environ["CONNECTIVO_PW"]
URL = "https://app.connectivo.de/public/client/offers"

MERCHANT_ID = ""  # leer lassen = alle Shops, sonst z. B. "100563920"
CATEGORIES = ["916", "930", "853"]  # hier deine Kategorie-IDs eintragen
SORTS = ["RELEVANCE_DESC", "PRICE_ASC", "PRICE_DESC"]

seen = {}

def fetch(category, sort):
    params = {"categories": category, "amount": 100, "sortBy": sort}
    if MERCHANT_ID:
        params["merchantId"] = MERCHANT_ID
    r = requests.get(URL, params=params, auth=(EMAIL, PASSWORD), timeout=60)
    r.raise_for_status()
    new = 0
    for p in r.json()["products"]:
        if p["id"] not in seen:
            p["_category"] = category
            seen[p["id"]] = p
            new += 1
    return new

for cat in CATEGORIES:
    for sort in SORTS:
        print(cat, sort, "neu:", fetch(cat, sort), "gesamt:", len(seen))

with open("feed.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["id", "title", "brand", "price", "currency", "shipping", "image",
                "link", "ean", "description", "availability",
                "shop_id", "shop_name", "category_id"])
    for p in seen.values():
        shop = p.get("shop") or {}
        w.writerow([
            p["id"],
            p["title"].replace(" *0% MwSt. gem. §12 Abs. 3 UStG", ""),
            p.get("brand") or "",
            p["price"]["amount"],
            p["price"]["currency"],
            (p.get("shippingPrice") or {}).get("amount", ""),
            (p.get("image") or {}).get("url", ""),
            p["clickUrl"],
            p.get("ean") or "",
            p.get("description") or "",
            p.get("availability") or "in stock",
            shop.get("id", ""),
            shop.get("name", ""),
            p["_category"],
        ])

print("Produkte in feed.csv:", len(seen))
