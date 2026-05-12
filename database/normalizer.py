def normalize_df(df, schema):
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]

    reverse_map = {}

    for standard_key, real_col in schema.items():
        if real_col in df.columns:
            reverse_map[real_col] = standard_key

    df = df.rename(columns=reverse_map)

    return df