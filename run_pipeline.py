import subprocess
import sys


def run_script(script_name):
    print(f"\n{'=' * 60}")
    print(f"Running: {script_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script_name],
        check=False,
    )

    if result.returncode != 0:
        print(f"\nPipeline stopped: {script_name} failed.")
        sys.exit(result.returncode)

    print(f"Completed: {script_name}")


def main():
    scripts = [
        "generate_dataset.py",
        "clean_data.py",
        "build_db.py",
        "queries.py",
        "metrics_engine.py",
        "draft_report.py",
    ]

    print("PHARMEASY REGIONAL PULSE PIPELINE")
    print("---------------------------------")

    for script in scripts:
        run_script(script)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("\nGenerated/validated outputs include:")
    print("- pharmeasy_orders_raw.csv")
    print("- pharmeasy_orders_clean.csv")
    print("- pharmeasy.db")
    print("- Regional monthly metrics")
    print("- CII draft report")

    print(
        "\nHuman-reviewed reporting and dashboard files "
        "are available separately in the project folder."
    )


if __name__ == "__main__":
    main()