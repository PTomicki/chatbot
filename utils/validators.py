def validate_ai(ai: dict) -> dict:
    """
    Sanitization + correction logic dla AI output
    """

    # =========================
    # YEAR FIX
    # =========================
    y_min = ai.get("year_min")
    y_max = ai.get("year_max")

    if y_min is not None and y_max is not None:
        try:
            if int(y_min) > int(y_max):
                ai["year_min"], ai["year_max"] = y_max, y_min
        except:
            pass

    # =========================
    # DAMAGE NORMALIZATION
    # =========================
    if ai.get("damage") is not None:
        ai["damage"] = str(ai["damage"]).lower().strip()

    # =========================
    # BRAND / MODEL CLEANUP
    # =========================
    if ai.get("brand"):
        ai["brand"] = ai["brand"].strip()

    if ai.get("model"):
        ai["model"] = ai["model"].strip()

    return ai