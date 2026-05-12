import pandas as pd


# =========================
# MAIN FILTER ENGINE
# =========================
def apply_filters(df: pd.DataFrame, filters: dict, damage_map: dict = None):
    df = df.copy()

    for key, value in filters.items():

        if value is None or value == "":
            continue


        # =========================
        # BRAND
        # =========================
        if key == "brand":
            df = df[
                df["brand"]
                .astype(str)
                .str.lower()
                .str.strip()
                == str(value).lower().strip()
            ]


        # =========================
        # MODEL
        # =========================
        elif key == "model":
            df = df[
                df["model"]
                .astype(str)
                .str.lower()
                .str.contains(str(value).lower(), na=False)
            ]


        # =========================
        # PRICE
        # =========================
        elif key == "price_min":
            df = df[df["price"] >= float(value)]

        elif key == "price_max":
            df = df[df["price"] <= float(value)]


        # =========================
        # YEAR
        # =========================
        elif key == "year_min":
            df = df[df["year"] >= int(value)]

        elif key == "year_max":
            df = df[df["year"] <= int(value)]


        # =========================
        # MILEAGE (KM)
        # =========================
        elif key == "km_min":
            df = df[df["mileage"] >= int(value)]

        elif key == "km_max":
            df = df[df["mileage"] <= int(value)]


        # =========================
        # DAMAGE (INTELLIGENT MAP)
        # =========================
        elif key == "damage":

            if damage_map is None:
                continue

            damage_key = str(value).lower().strip()

            if damage_key not in damage_map:
                continue

            possible_values = [
                str(v).lower().strip()
                for v in damage_map[damage_key]
            ]

            df = df[
                df["damage"]
                .astype(str)
                .str.lower()
                .str.strip()
                .isin(possible_values)
            ]

    return df


# =========================
# AI SAFETY VALIDATION
# =========================
def validate_ai(ai: dict):
    """
    Fixuje głupie przypadki typu year_min > year_max
    """

    y_min = ai.get("year_min")
    y_max = ai.get("year_max")

    if y_min is not None and y_max is not None:
        try:
            if int(y_min) > int(y_max):
                ai["year_min"], ai["year_max"] = y_max, y_min
        except:
            pass

    return ai