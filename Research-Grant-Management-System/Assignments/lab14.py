from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course_Project" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

"""Lab 14 capstone entry point. Runs the integrated graph and writes a local dashboard."""
from graph.lab14_capstone import DEFAULT_REQUEST, print_dashboard, run_capstone


def main() -> int:
    summary = run_capstone(DEFAULT_REQUEST)
    print_dashboard(summary)
    # A blocked run is a valid, safe outcome when required evidence/approval is absent.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
