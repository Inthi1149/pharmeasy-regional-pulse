import pandas as pd
import numpy as np


RAW_FILE = "pharmeasy_orders_raw.csv"
CLEAN_FILE = "pharmeasy_orders_clean.csv"

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "region",
    "product",
    "category",
    "quantity",
    "unit_price",
    "sales",
    "profit",
]


REGION_MAP = {
    "hyderabad": "Hyderabad",
    "hyd": "Hyderabad",
    "warangal": "Warangal",
    "vijayawada": "Vijayawada",
    "visakhapatnam": "Visakhapatnam",
    "vizag": "Visakhapatnam",
    "guntur": "Guntur",
    "nellore": "Nellore",
    "tirupati": "Tirupati",
    "karimnagar": "Karimnagar",
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "kurnool": "Kurnool",
}


PRODUCT_CATEGORY = {
    "Paracetamol 500mg": "Medicines",
    "Azithromycin 500mg": "Medicines",
    "Cetirizine 10mg": "Medicines",
    "Vitamin C Tablets": "Wellness",
    "Multivitamin Tablets": "Wellness",
    "Protein Powder": "Wellness",
    "Face Wash": "Personal Care",
    "Shampoo": "Personal Care",
    "Moisturizer": "Personal Care",
    "Baby Diapers": "Baby Care",
    "Baby Lotion": "Baby Care",
    "Baby Shampoo": "Baby Care",
    "Blood Pressure Monitor": "Medical Devices",
    "Digital Thermometer": "Medical Devices",
    "Glucometer": "Medical Devices",
    "Ashwagandha Capsules": "Ayurveda",
    "Triphala Tablets": "Ayurveda",
    "Chyawanprash": "Ayurveda",
}


def validate_schema(df, required_columns):
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        status = "blocked_schema"
    else:
        status = "validated"

    return {
        "status": status,
        "row_count": len(df),
        "missing_columns": missing_columns,
    }


def normalize_region(value):
    if pd.isna(value):
        return value

    cleaned = str(value).strip().lower()
    return REGION_MAP.get(cleaned, str(value).strip())


def main():
    print("Loading raw dataset...")

    df = pd.read_csv(RAW_FILE)

    print(f"Raw rows: {len(df)}")

    # ---------------------------------
    # 1. Validate the raw schema
    # ---------------------------------

    raw_validation = validate_schema(df, REQUIRED_COLUMNS)
    print("Raw schema validation:", raw_validation)

    if raw_validation["status"] == "blocked_schema":
        print("Pipeline stopped because required columns are missing.")
        return

    # ---------------------------------
    # 2. Remove exact duplicate rows
    # ---------------------------------

    before_dedup = len(df)

    df = df.drop_duplicates().copy()

    duplicates_removed = before_dedup - len(df)

    print(f"Exact duplicates removed: {duplicates_removed}")
    print(f"Rows after deduplication: {len(df)}")

    # ---------------------------------
    # 3. Check missing values
    # ---------------------------------

    missing_category = df["category"].isna().sum()
    missing_profit = df["profit"].isna().sum()

    print(f"Missing category before imputation: {missing_category}")
    print(f"Missing profit before imputation: {missing_profit}")

    # ---------------------------------
    # 4. Normalize region names
    # ---------------------------------

    df["region"] = df["region"].apply(normalize_region)

    print(
        "Canonical regions after normalization:",
        df["region"].nunique()
    )

    # ---------------------------------
    # 5. Impute missing category
    #    using product -> category lookup
    # ---------------------------------

    missing_category_mask = df["category"].isna()

    df.loc[missing_category_mask, "category"] = (
        df.loc[missing_category_mask, "product"]
        .map(PRODUCT_CATEGORY)
    )

    # ---------------------------------
    # 6. Impute missing profit
    #    using category mean margin
    # ---------------------------------

    valid_profit_rows = df[
        df["profit"].notna()
        & df["sales"].notna()
        & (df["sales"] != 0)
    ].copy()

    valid_profit_rows["margin"] = (
        valid_profit_rows["profit"]
        / valid_profit_rows["sales"]
    )

    category_mean_margin = (
        valid_profit_rows
        .groupby("category")["margin"]
        .mean()
    )

    missing_profit_mask = df["profit"].isna()

    df.loc[missing_profit_mask, "profit"] = (
        df.loc[missing_profit_mask]
        .apply(
            lambda row:
            row["sales"]
            * category_mean_margin[row["category"]],
            axis=1
        )
    )

    df["profit"] = df["profit"].round(2)

    # ---------------------------------
    # 7. Final missing-value checks
    # ---------------------------------

    print(
        "Missing category after imputation:",
        df["category"].isna().sum()
    )

    print(
        "Missing profit after imputation:",
        df["profit"].isna().sum()
    )

    # ---------------------------------
    # 8. Validate clean dataset
    # ---------------------------------

    clean_validation = validate_schema(
        df,
        REQUIRED_COLUMNS
    )

    print("Clean schema validation:", clean_validation)

    # ---------------------------------
    # 9. Test broken-schema path
    # ---------------------------------

    broken_df = df.drop(columns=["profit"])

    broken_validation = validate_schema(
        broken_df,
        REQUIRED_COLUMNS
    )

    print("Broken schema test:", broken_validation)

    # ---------------------------------
    # 10. Save clean dataset
    # ---------------------------------

    df.to_csv(CLEAN_FILE, index=False)

    print(f"Clean dataset saved to {CLEAN_FILE}")


if __name__ == "__main__":
    main()