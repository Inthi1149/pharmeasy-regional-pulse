import sqlite3
import pandas as pd


DATABASE_FILE = "pharmeasy.db"


def get_region_month_sales():
    """
    Return regional sales totals for April, May and June 2026.

    LEFT JOIN is used so regions with zero orders,
    such as Kurnool, are still included.
    """

    conn = sqlite3.connect(DATABASE_FILE)

    query = """
    SELECT
        r.region,

        ROUND(
            COALESCE(
                SUM(
                    CASE
                        WHEN substr(o.order_date, 6, 2) = '04'
                        THEN o.sales
                        ELSE 0
                    END
                ),
                0
            ),
            2
        ) AS apr_sales,

        ROUND(
            COALESCE(
                SUM(
                    CASE
                        WHEN substr(o.order_date, 6, 2) = '05'
                        THEN o.sales
                        ELSE 0
                    END
                ),
                0
            ),
            2
        ) AS may_sales,

        ROUND(
            COALESCE(
                SUM(
                    CASE
                        WHEN substr(o.order_date, 6, 2) = '06'
                        THEN o.sales
                        ELSE 0
                    END
                ),
                0
            ),
            2
        ) AS jun_sales

    FROM regions_master r

    LEFT JOIN orders_clean o
        ON r.region = o.region

    GROUP BY r.region

    ORDER BY r.region
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


def get_join_checks():
    """
    Demonstrate INNER JOIN vs LEFT JOIN behaviour.
    """

    conn = sqlite3.connect(DATABASE_FILE)

    left_query = """
    SELECT COUNT(*) AS row_count
    FROM regions_master r
    LEFT JOIN orders_clean o
        ON r.region = o.region
    """

    inner_query = """
    SELECT COUNT(*) AS row_count
    FROM regions_master r
    INNER JOIN orders_clean o
        ON r.region = o.region
    """

    left_count = pd.read_sql_query(
        left_query,
        conn
    ).iloc[0]["row_count"]

    inner_count = pd.read_sql_query(
        inner_query,
        conn
    ).iloc[0]["row_count"]

    conn.close()

    return {
        "left_join_rows": int(left_count),
        "inner_join_rows": int(inner_count),
    }


def get_kurnool_count_check():
    """
    Demonstrate why COUNT(order_id) should be used
    when counting orders after a LEFT JOIN.
    """

    conn = sqlite3.connect(DATABASE_FILE)

    query = """
    SELECT
        r.region,
        COUNT(*) AS count_star,
        COUNT(o.order_id) AS count_order_id
    FROM regions_master r

    LEFT JOIN orders_clean o
        ON r.region = o.region

    WHERE r.region = 'Kurnool'

    GROUP BY r.region
    """

    result = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return result


def main():

    print("\nREGION MONTHLY SALES")
    print("--------------------")

    monthly_sales = get_region_month_sales()

    print(
        monthly_sales.to_string(
            index=False
        )
    )

    print("\nJOIN CHECKS")
    print("-----------")

    join_checks = get_join_checks()

    print(
        "LEFT JOIN rows:",
        join_checks["left_join_rows"]
    )

    print(
        "INNER JOIN rows:",
        join_checks["inner_join_rows"]
    )

    print("\nKURNOOL COUNT CHECK")
    print("-------------------")

    kurnool = get_kurnool_count_check()

    print(
        kurnool.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()