# Ez visszaad egy szótárat (dict), amit később GUI vagy CLI oldalon használunk.


import json
import os

def load_translations(lang_code="hu"):
    path = os.path.join("locales", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        print(f"⚠️ Nyelvi fájl nem található: {lang_code}")
        return {}
