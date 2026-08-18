#!/usr/bin/env python3
"""Renku-friendly orchestration for the AFRICA-ZT-EDU reproducibility artifact."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("\n$", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quick", action="store_true", help="Fast validation run")
    mode.add_argument("--full", action="store_true", help="Full published-scale reproduction")
    parser.add_argument("--skip-benchmark", action="store_true")
    args = parser.parse_args()

    py = sys.executable
    if args.quick:
        run([
            py, "experiments/simulate_policy.py",
            "--requests-per-seed", "5000",
            "--seeds", "3",
            "--output", "renku_quick/data",
            "--figures", "renku_quick/figures",
        ])
        if not args.skip_benchmark:
            run([py, "scripts/benchmark.py", "--output-dir", "renku_quick/results", "--scale", "0.05"])
        print("\nQuick validation completed. Outputs are under renku_quick/.")
        return 0

    run([py, "experiments/simulate_policy.py"])
    if not args.skip_benchmark:
        run([py, "scripts/benchmark.py", "--output-dir", "results"])
    run([py, "scripts/generate_figures.py"])
    print("\nFull computational reproduction completed.")
    print("See data/, results/, and figures/. Compile the manuscript separately with LaTeX/Overleaf if desired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
