import pandas as pd

RAW_FILE = "pharmeasy_orders_raw.csv"
CLEAN_FILE = "pharmeasy_orders_clean.csv"

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "region",
    "category",
    "product",
    "quantity",
    "sales_inr",
    "profit_inr",
]


def validate_schema(df, required_columns):
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    return {
        "status": "validated" if not missing_columns else "blocked_schema",
        "row_count": len(df),
        "missing_columns": missing_columns,
    }


def clean_dataset():
    print("Loading raw dataset...")
    df = pd.read_csv(RAW_FILE)

    print(f"Raw rows: {len(df)}")

    raw_validation = validate_schema(df, REQUIRED_COLUMNS)
    print(f"Raw schema validation: {raw_validation}")

    if raw_validation["status"] != "validated":
        print("Pipeline stopped because required columns are missing.")
        return

    # 1. Remove exact duplicate rows.
    before_dedup = len(df)
    df = df.drop_duplicates().copy()
    duplicates_removed = before_dedup - len(df)

    print(f"Exact duplicates removed: {duplicates_removed}")
    print(f"Rows after deduplication: {len(df)}")

    # Record missing counts after deduplication and before imputation.
    missing_category_before = int(df["category"].isna().sum())
    missing_profit_before = int(df["profit_inr"].isna().sum())

    print(f"Missing category before imputation: {missing_category_before}")
    print(f"Missing profit before imputation: {missing_profit_before}")

    # 2. Normalize region names.
    df["region"] = df["region"].astype(str).str.strip().str.title()

    # 3. Impute missing category using an exact product -> category lookup.
    product_category_lookup = (
        df.loc[df["category"].notna(), ["product", "category"]]
        .drop_duplicates(subset=["product"])
        .set_index("product")["category"]
        .to_dict()
    )

    missing_category_mask = df["category"].isna()
    df.loc[missing_category_mask, "category"] = (
        df.loc[missing_category_mask, "product"]
        .map(product_category_lookup)
    )

    # 4. Impute missing profit using category mean profit margin.
    df["sales_inr"] = pd.to_numeric(df["sales_inr"], errors="coerce")
    df["profit_inr"] = pd.to_numeric(df["profit_inr"], errors="coerce")

    known_profit = df["profit_inr"].notna()

    margin_by_category = (
        (df.loc[known_profit, "profit_inr"] /
         df.loc[known_profit, "sales_inr"])
        .groupby(df.loc[known_profit, "category"])
        .mean()
    )

    missing_profit_mask = df["profit_inr"].isna()

    df.loc[missing_profit_mask, "profit_inr"] = (
        df.loc[missing_profit_mask].apply(
            lambda row: round(
                row["sales_inr"] * margin_by_category[row["category"]],
                2,
            ),
            axis=1,
        )
    )

    canonical_regions = df["region"].nunique()
    missing_category_after = int(df["category"].isna().sum())
    missing_profit_after = int(df["profit_inr"].isna().sum())

    print(f"Canonical regions after normalization: {canonical_regions}")
    print(f"Missing category after imputation: {missing_category_after}")
    print(f"Missing profit after imputation: {missing_profit_after}")

    clean_validation = validate_schema(df, REQUIRED_COLUMNS)
    print(f"Clean schema validation: {clean_validation}")

    # Demonstrate the blocked_schema path.
    broken_df = df.drop(columns=["profit_inr"])
    broken_validation = validate_schema(broken_df, REQUIRED_COLUMNS)
    print(f"Broken schema test: {broken_validation}")

    # Acceptance checks from the capstone.
    assert duplicates_removed == 59
    assert len(df) == 2100
    assert canonical_regions == 9
    assert missing_category_before == 48
    assert missing_profit_before == 94
    assert missing_category_after == 0
    assert missing_profit_after == 0
    assert clean_validation["status"] == "validated"
    assert broken_validation["status"] == "blocked_schema"
    assert broken_validation["missing_columns"] == ["profit_inr"]

    df.to_csv(CLEAN_FILE, index=False)
    print(f"Clean dataset saved to {CLEAN_FILE}")


if __name__ == "__main__":
    clean_dataset()