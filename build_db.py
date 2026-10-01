import sqlite3
import pandas as pd


CLEAN_FILE = "pharmeasy_orders_clean.csv"
REGIONS_FILE = "regions_master.csv"
DATABASE_FILE = "pharmeasy.db"


def build_database():
    print("Loading cleaned orders...")
    orders = pd.read_csv(CLEAN_FILE)

    print("Loading regions master...")
    regions = pd.read_csv(REGIONS_FILE)

    print(f"Orders loaded: {len(orders)}")
    print(f"Regions loaded: {len(regions)}")

    # Connect to SQLite.
    conn = sqlite3.connect(DATABASE_FILE)

    # Store both datasets as database tables.
    regions.to_sql(
        "regions_master",
        conn,
        if_exists="replace",
        index=False
    )

    orders.to_sql(
        "orders_clean",
        conn,
        if_exists="replace",
        index=False
    )

    print("Created table: regions_master")
    print("Created table: orders_clean")

    cursor = conn.cursor()

    # -----------------------------------------
    # Check 1: regions_master row count
    # -----------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM regions_master"
    )
    region_count = cursor.fetchone()[0]

    print(f"regions_master rows: {region_count}")

    # -----------------------------------------
    # Check 2: orders_clean row count
    # -----------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM orders_clean"
    )
    order_count = cursor.fetchone()[0]

    print(f"orders_clean rows: {order_count}")

    # -----------------------------------------
    # Check 3: duplicate order IDs
    # -----------------------------------------

    duplicate_query = """
    SELECT COUNT(*)
    FROM (
        SELECT order_id
        FROM orders_clean
        GROUP BY order_id
        HAVING COUNT(*) > 1
    )
    """

    cursor.execute(duplicate_query)
    duplicate_order_ids = cursor.fetchone()[0]

    print(
        f"Duplicate order_id values: "
        f"{duplicate_order_ids}"
    )

    # -----------------------------------------
    # Check 4: LEFT JOIN row count
    # -----------------------------------------

    left_join_query = """
    SELECT COUNT(*)
    FROM regions_master r
    LEFT JOIN orders_clean o
        ON r.region = o.region
    """

    cursor.execute(left_join_query)
    left_join_count = cursor.fetchone()[0]

    print(f"LEFT JOIN rows: {left_join_count}")

    # -----------------------------------------
    # Check 5: INNER JOIN row count
    # -----------------------------------------

    inner_join_query = """
    SELECT COUNT(*)
    FROM regions_master r
    INNER JOIN orders_clean o
        ON r.region = o.region
    """

    cursor.execute(inner_join_query)
    inner_join_count = cursor.fetchone()[0]

    print(f"INNER JOIN rows: {inner_join_count}")

    # -----------------------------------------
    # Check 6:
    # Kurnool COUNT(*) vs COUNT(order_id)
    # -----------------------------------------

    kurnool_query = """
    SELECT
        r.region,
        COUNT(*) AS joined_rows,
        COUNT(o.order_id) AS order_count
    FROM regions_master r
    LEFT JOIN orders_clean o
        ON r.region = o.region
    WHERE r.region = 'Kurnool'
    GROUP BY r.region
    """

    cursor.execute(kurnool_query)
    kurnool_result = cursor.fetchone()

    if kurnool_result:
        region = kurnool_result[0]
        joined_rows = kurnool_result[1]
        actual_orders = kurnool_result[2]

        print(
            f"{region} COUNT(*): "
            f"{joined_rows}"
        )

        print(
            f"{region} COUNT(order_id): "
            f"{actual_orders}"
        )

    # -----------------------------------------
    # Close connection
    # -----------------------------------------

    conn.close()

    print(f"Database saved to {DATABASE_FILE}")


if __name__ == "__main__":
    build_database()