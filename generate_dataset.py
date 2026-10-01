import random
import numpy as np
import pandas as pd

SEED = 2026
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_FILE = "pharmeasy_orders_raw.csv"

REGIONS = [
    "Hyderabad",
    "Warangal",
    "Vijayawada",
    "Visakhapatnam",
    "Guntur",
    "Nellore",
    "Tirupati",
    "Karimnagar",
    "Bengaluru",
]

# These monthly multipliers are designed to produce the
# required >8% / <=8% regional movement patterns.
MONTH_FACTORS = {
    "Hyderabad": {
        4: 1.00,
        5: 1.16,
        6: 1.40,
    },
    "Warangal": {
        4: 1.00,
        5: 0.78,
        6: 0.66,
    },
    "Vijayawada": {
        4: 1.00,
        5: 1.02,
        6: 0.90,
    },
    "Visakhapatnam": {
        4: 1.00,
        5: 0.38,
        6: 0.76,
    },
    "Guntur": {
        4: 1.00,
        5: 2.2219,
        6: 1.5965,
    },
    "Nellore": {
        4: 1.00,
        5: 1.06,
        6: 1.10,
    },
    "Tirupati": {
        4: 1.00,
        5: 1.67,
        6: 1.39,
    },
    "Karimnagar": {
        4: 1.00,
        5: 1.24,
        6: 0.69,
    },
    "Bengaluru": {
        4: 1.00,
        5: 0.85,
        6: 0.84,
    },
}

CATEGORIES = [
    "Medicines",
    "Personal Care",
    "Baby Care",
    "Wellness",
    "Medical Devices",
    "Ayurveda",
]

PRODUCTS = {
    "Paracetamol 500mg": "Medicines",
    "Azithromycin 500mg": "Medicines",
    "Cetirizine 10mg": "Medicines",

    "Face Wash": "Personal Care",
    "Shampoo": "Personal Care",
    "Moisturizer": "Personal Care",

    "Baby Diapers": "Baby Care",
    "Baby Lotion": "Baby Care",
    "Baby Shampoo": "Baby Care",

    "Vitamin C Tablets": "Wellness",
    "Multivitamin Tablets": "Wellness",
    "Protein Powder": "Wellness",

    "Blood Pressure Monitor": "Medical Devices",
    "Digital Thermometer": "Medical Devices",
    "Glucometer": "Medical Devices",

    "Ashwagandha Capsules": "Ayurveda",
    "Triphala Tablets": "Ayurveda",
    "Chyawanprash": "Ayurveda",
}

CATEGORY_MARGIN = {
    "Medicines": 0.14,
    "Personal Care": 0.22,
    "Baby Care": 0.18,
    "Wellness": 0.25,
    "Medical Devices": 0.16,
    "Ayurveda": 0.20,
}

PRODUCT_NAMES = list(PRODUCTS.keys())


# Exactly 16 raw region representations.
RAW_REGION_VARIANTS = {
    "Hyderabad": [
        "Hyderabad",
        "HYDERABAD",
    ],
    "Warangal": [
        "Warangal",
        " warangal",
    ],
    "Vijayawada": [
        "Vijayawada",
        "VIJAYAWADA",
    ],
    "Visakhapatnam": [
        "Visakhapatnam",
        "Vizag",
    ],
    "Guntur": [
        "Guntur",
        "GUNTUR",
    ],
    "Nellore": [
        "Nellore",
        " nellore",
    ],
    "Tirupati": [
        "Tirupati",
    ],
    "Karimnagar": [
        "Karimnagar",
    ],
    "Bengaluru": [
        "Bengaluru",
        "Bangalore",
    ],
}


def create_orders():
    rows = []

    # 2,100 unique orders distributed evenly enough
    # across region/month combinations.
    combinations = []

    for region in REGIONS:
        for month in [4, 5, 6]:
            combinations.append((region, month))

    for order_id in range(1, 2101):

        region, month = combinations[
            (order_id - 1) % len(combinations)
        ]

        product = random.choice(PRODUCT_NAMES)
        category = PRODUCTS[product]

        quantity = random.randint(1, 5)

        # Stable base value. The monthly factor controls
        # regional month-over-month movement.
        base_sales = 1000.00

        sales = round(
            base_sales
            * MONTH_FACTORS[region][month],
            2
        )

        unit_price = round(
            sales / quantity,
            2
        )

        margin = CATEGORY_MARGIN[category]

        profit = round(
            sales * margin,
            2
        )

        day = ((order_id - 1) % 28) + 1

        order_date = (
            f"2026-{month:02d}-{day:02d}"
        )

        variants = RAW_REGION_VARIANTS[region]

        # Cycle through variants deterministically.
        raw_region = variants[
            (order_id - 1) % len(variants)
        ]

        rows.append(
            {
                "order_id": order_id,
                "order_date": order_date,
                "region": raw_region,
                "product": product,
                "category": category,
                "quantity": quantity,
                "unit_price": unit_price,
                "sales": sales,
                "profit": profit,
            }
        )

    return pd.DataFrame(rows)


def main():

    # -----------------------------------
    # Create 2,100 unique orders
    # -----------------------------------

    df = create_orders()

    assert len(df) == 2100

    # -----------------------------------
    # Verify exactly 16 raw region values
    # -----------------------------------

    raw_region_count = df["region"].nunique()

    assert raw_region_count == 16, (
        f"Expected 16 raw region variants, "
        f"got {raw_region_count}"
    )

    # -----------------------------------
    # Add 48 missing category values
    # -----------------------------------

    category_missing_idx = df.sample(
        n=48,
        random_state=SEED + 1
    ).index

    df.loc[
        category_missing_idx,
        "category"
    ] = np.nan

    # -----------------------------------
    # Add 94 missing profit values
    # -----------------------------------

    profit_missing_idx = df.sample(
        n=94,
        random_state=SEED + 2
    ).index

    df.loc[
        profit_missing_idx,
        "profit"
    ] = np.nan

    # -----------------------------------
    # Add 59 EXACT duplicate rows
    # -----------------------------------

    eligible = df[
        df["category"].notna()
        & df["profit"].notna()
    ]

    duplicates = eligible.sample(
        n=59,
        random_state=SEED
    ).copy()

    df = pd.concat(
        [df, duplicates],
        ignore_index=True
    )

    # -----------------------------------
    # Acceptance checks
    # -----------------------------------

    assert len(df) == 2159

    assert df["category"].isna().sum() == 48

    assert df["profit"].isna().sum() == 94

    assert df["region"].nunique() == 16

    assert df.duplicated().sum() == 59

    # -----------------------------------
    # Save
    # -----------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Dataset generation successful.")
    print(f"Raw rows: {len(df)}")
    print(
        f"Exact duplicates: "
        f"{df.duplicated().sum()}"
    )
    print(
        f"Raw region variants: "
        f"{df['region'].nunique()}"
    )
    print(
        f"Missing category: "
        f"{df['category'].isna().sum()}"
    )
    print(
        f"Missing profit: "
        f"{df['profit'].isna().sum()}"
    )
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()