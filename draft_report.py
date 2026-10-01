from metrics_engine import (
    calculate_changes,
    flag_significant_regions_v1,
)
from queries import get_region_month_sales


def draft_report_v1(flagged_regions, metrics):
    """
    Produce one Context-Insight-Implication (CII) block
    for each unique flagged region.

    Regions flagged in both transitions are deduplicated
    into one block covering both periods.
    """
    reports = []

    # Deduplicate while keeping a predictable order.
    unique_regions = sorted(set(flagged_regions))

    for region in unique_regions:
        region_metrics = metrics[region]

        apr_sales = region_metrics["apr_sales"]
        may_sales = region_metrics["may_sales"]
        jun_sales = region_metrics["jun_sales"]

        apr_may_change = region_metrics["apr_to_may"]
        may_jun_change = region_metrics["may_to_jun"]

        flagged_apr_may = abs(apr_may_change) > 8
        flagged_may_jun = abs(may_jun_change) > 8

        periods = []

        if flagged_apr_may:
            periods.append(
                f"April to May ({apr_may_change:+.2f}%)"
            )

        if flagged_may_jun:
            periods.append(
                f"May to June ({may_jun_change:+.2f}%)"
            )

        context = (
            f"{region} recorded monthly sales of "
            f"INR {apr_sales:,.2f} in April, "
            f"INR {may_sales:,.2f} in May, and "
            f"INR {jun_sales:,.2f} in June 2026."
        )

        insight = (
            f"The region crossed the 8% operational-alert "
            f"threshold in {', '.join(periods)}."
        )

        implication = (
            "This movement should be reviewed by a human "
            "alongside the underlying order mix before any "
            "cause or business action is concluded."
        )

        reports.append(
            {
                "region": region,
                "Context": context,
                "Insight": insight,
                "Implication": implication,
            }
        )

    return reports


def main():
    monthly_sales = get_region_month_sales()

    apr_to_may, may_to_jun = calculate_changes(
        monthly_sales
    )

    apr_may_flagged = flag_significant_regions_v1(
        apr_to_may,
        threshold=8,
    )

    may_jun_flagged = flag_significant_regions_v1(
        may_to_jun,
        threshold=8,
    )

    # Union of regions flagged in either transition.
    flagged_regions = (
        set(apr_may_flagged)
        | set(may_jun_flagged)
    )

    metrics = {}

    for _, row in monthly_sales.iterrows():
        region = row["region"]

        metrics[region] = {
            "apr_sales": float(row["apr_sales"]),
            "may_sales": float(row["may_sales"]),
            "jun_sales": float(row["jun_sales"]),
            "apr_to_may": apr_to_may[region],
            "may_to_jun": may_to_jun[region],
        }

    report = draft_report_v1(
        flagged_regions,
        metrics,
    )

    for block in report:
        print("\n" + "=" * 60)
        print(block["region"])
        print("=" * 60)

        print("Context:")
        print(block["Context"])

        print("\nInsight:")
        print(block["Insight"])

        print("\nImplication:")
        print(block["Implication"])

    # -----------------------------------------
    # Acceptance checks
    # -----------------------------------------

    expected_regions = {
        "Bengaluru",
        "Guntur",
        "Hyderabad",
        "Karimnagar",
        "Tirupati",
        "Vijayawada",
        "Visakhapatnam",
        "Warangal",
    }

    report_regions = {
        block["region"]
        for block in report
    }

    assert report_regions == expected_regions
    assert len(report) == 8

    # Ensure each region occurs only once.
    assert len(report_regions) == len(report)

    # Stable and zero-order regions must not appear.
    assert "Nellore" not in report_regions
    assert "Kurnool" not in report_regions

    # Flagship Guntur value must come from computed metrics.
    assert round(
        metrics["Guntur"]["apr_to_may"],
        2,
    ) == 122.19

    # Every block must contain all three CII fields.
    for block in report:
        assert block["Context"]
        assert block["Insight"]
        assert block["Implication"]

    print("\n" + "=" * 60)
    print("ACCEPTANCE CHECKS")
    print("=" * 60)
    print("draft_report_v1 acceptance checks passed.")
    print(f"Unique CII regions: {len(report)}")
    print(
        "Guntur Apr->May flagship change: "
        f"{metrics['Guntur']['apr_to_may']:+.2f}%"
    )


if __name__ == "__main__":
    main()