import json

from queries import get_region_month_sales


def compute_percentage_change_v1(current, previous):
    """
    Calculate percentage change from previous to current.
    Return 0 when previous is zero.
    """
    if previous == 0:
        return 0

    return ((current - previous) / previous) * 100


def flag_significant_regions_v1(changes, threshold=8):
    """
    Flag regions whose absolute MoM percentage change
    is strictly greater than the threshold.

    This is an operational-alert rule, not a
    statistical-significance test.
    """
    return {
        region: change
        for region, change in changes.items()
        if abs(change) > threshold
    }


def save_state_v1(month_summary, path):
    """
    Persist a computed monthly summary as JSON.
    """
    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            month_summary,
            file,
            indent=2,
            sort_keys=True,
        )


def load_previous_state_v1(path):
    """
    Reload a previously saved monthly summary.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_changes(monthly_sales):
    apr_to_may = {}
    may_to_jun = {}

    for _, row in monthly_sales.iterrows():
        region = row["region"]

        apr_to_may[region] = compute_percentage_change_v1(
            row["may_sales"],
            row["apr_sales"],
        )

        may_to_jun[region] = compute_percentage_change_v1(
            row["jun_sales"],
            row["may_sales"],
        )

    return apr_to_may, may_to_jun


def print_changes(title, changes):
    print("\n" + title)
    print("-" * len(title))

    for region, change in changes.items():
        print(f"{region:<15} {change:+.2f}%")


def print_flagged(title, flagged):
    print("\n" + title)
    print("-" * len(title))

    for region, change in flagged.items():
        print(f"{region:<15} {change:+.2f}%")


def main():
    monthly_sales = get_region_month_sales()

    apr_to_may, may_to_jun = calculate_changes(
        monthly_sales
    )

    print_changes(
        "APRIL TO MAY CHANGES",
        apr_to_may,
    )

    print_changes(
        "MAY TO JUNE CHANGES",
        may_to_jun,
    )

    apr_may_flagged = flag_significant_regions_v1(
        apr_to_may,
        threshold=8,
    )

    may_jun_flagged = flag_significant_regions_v1(
        may_to_jun,
        threshold=8,
    )

    print_flagged(
        "FLAGGED: APRIL TO MAY",
        apr_may_flagged,
    )

    print_flagged(
        "FLAGGED: MAY TO JUNE",
        may_jun_flagged,
    )

    # -----------------------------------------
    # Required state-persistence test
    # -----------------------------------------

    april_summary = {
        row["region"]: float(row["apr_sales"])
        for _, row in monthly_sales.iterrows()
    }

    state_path = "april_state.json"

    save_state_v1(
        april_summary,
        state_path,
    )

    loaded_april_summary = (
        load_previous_state_v1(state_path)
    )

    assert loaded_april_summary == april_summary, (
        "State persistence round-trip failed."
    )

    # -----------------------------------------
    # Acceptance checks
    # -----------------------------------------

    expected_apr_may = {
        "Hyderabad",
        "Warangal",
        "Visakhapatnam",
        "Guntur",
        "Tirupati",
        "Karimnagar",
        "Bengaluru",
    }

    expected_may_jun = {
        "Hyderabad",
        "Warangal",
        "Vijayawada",
        "Visakhapatnam",
        "Guntur",
        "Tirupati",
        "Karimnagar",
    }

    assert set(apr_may_flagged) == expected_apr_may
    assert set(may_jun_flagged) == expected_may_jun

    assert "Nellore" not in apr_may_flagged
    assert "Nellore" not in may_jun_flagged

    guntur_change = apr_to_may["Guntur"]

    assert round(guntur_change, 2) == 122.19

    assert compute_percentage_change_v1(
        100,
        0,
    ) == 0

    print("\nACCEPTANCE CHECKS")
    print("-----------------")
    print("All metrics acceptance checks passed.")
    print(
        f"Guntur Apr->May: "
        f"{guntur_change:+.2f}%"
    )
    print(
        "State persistence round-trip passed."
    )
    print(
        f"State saved to: {state_path}"
    )
    print(
        "Note: the 8% threshold is an "
        "operational-alert rule, not a "
        "statistical-significance test."
    )


if __name__ == "__main__":
    main()