#!/usr/bin/env python3
"""Generate publication figures from the included CSV files."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
RESULTS = ROOT / "results"
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(FIG / f"{name}.png", dpi=240, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def connectivity() -> None:
    df = pd.read_csv(DATA / "connectivity_2025.csv")
    fig, ax = plt.subplots(figsize=(3.45, 2.35))
    y = np.arange(len(df))
    bars = ax.barh(y, df["value_percent"], color=["#355C7D", "#6C5B7B", "#C06C84"])
    ax.set_yticks(y, labels=["World", "Africa", "Low-income\neconomies"])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Individuals using the Internet (%)")
    ax.set_title("Connectivity context, 2025")
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    for bar, value in zip(bars, df["value_percent"]):
        ax.text(value + 1.2, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "connectivity_context")


def governance() -> None:
    df = pd.read_csv(DATA / "governance_context.csv")
    subset = df.iloc[[0, 1, 2]].copy()
    labels = ["Data-protection law\n(UNCTAD tracker)", "Malabo signatures\n(21/55)", "Malabo ratifications\n(16/55)"]
    fig, ax = plt.subplots(figsize=(3.45, 2.35))
    y = np.arange(len(subset))
    bars = ax.barh(y, subset["value_percent"], color=["#2A9D8F", "#E9C46A", "#E76F51"])
    ax.set_yticks(y, labels=labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of African/AU countries (%)")
    ax.set_title("Data-governance context")
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    for bar, value in zip(bars, subset["value_percent"]):
        ax.text(value + 1.2, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "governance_context")


def coverage() -> None:
    df = pd.read_csv(DATA / "threat_control_scores.csv")
    grouped = df.groupby(["threat_id", "threat"], sort=False)[["baseline_score", "proposed_score"]].sum().reset_index()
    grouped["baseline_pct"] = grouped["baseline_score"] / 3 * 100
    grouped["proposed_pct"] = grouped["proposed_score"] / 3 * 100
    overall = pd.DataFrame({
        "threat_id": ["ALL"],
        "threat": ["Overall"],
        "baseline_score": [df["baseline_score"].sum()],
        "proposed_score": [df["proposed_score"].sum()],
        "baseline_pct": [df["baseline_score"].sum() / len(df) * 100],
        "proposed_pct": [df["proposed_score"].sum() / len(df) * 100],
    })
    grouped = pd.concat([grouped, overall], ignore_index=True)
    short = {
        "T1": "T1  Phishing / account takeover",
        "T2": "T2  Stolen bearer token",
        "T3": "T3  Compromised endpoint",
        "T4": "T4  Overprivileged administrator",
        "T5": "T5  Unlawful / excessive transfer",
        "T6": "T6  API scraping / exfiltration",
        "T7": "T7  Credential forgery",
        "T8": "T8  Revocation bypass",
        "T9": "T9  Analytics privacy leakage",
        "T10": "T10  Audit tampering",
        "T11": "T11  Connectivity disruption",
        "T12": "T12  Lock-in / misconfiguration",
        "ALL": "Overall (36 objectives)",
    }
    labels = [short[r.threat_id] for r in grouped.itertuples()]
    y = np.arange(len(grouped))
    h = 0.36
    fig, ax = plt.subplots(figsize=(7.15, 5.15))
    ax.barh(y + h / 2, grouped["baseline_pct"], height=h, label="Perimeter-centric reference profile", color="#9AA0A6")
    ax.barh(y - h / 2, grouped["proposed_pct"], height=h, label="Proposed architecture", color="#2F6690")
    ax.set_yticks(y, labels=labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 106)
    ax.set_xlabel("Analytical objective coverage (%)")
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=2, frameon=False)
    ax.axhline(len(grouped) - 1.5, color="black", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    for idx, row in grouped.iterrows():
        ax.text(row["proposed_pct"] + 0.7, idx - h / 2, f"{row['proposed_pct']:.0f}", va="center", fontsize=7)
    fig.subplots_adjust(top=0.91, left=0.29, right=0.98, bottom=0.10)
    save(fig, "threat_coverage")

def benchmark() -> None:
    df = pd.read_csv(RESULTS / "benchmark_summary.csv")
    selected_names = [
        "Ed25519 sign (VC payload)",
        "Ed25519 verify (VC payload)",
        "AES-256-GCM encrypt (10 KiB)",
        "Sequential policy evaluation (50 rules)",
        "Sequential policy evaluation (200 rules)",
        "Synthetic authorization gate (200 rules + verify + 10 KiB encrypt)",
    ]
    labels_map = {
        selected_names[0]: "Ed25519 sign",
        selected_names[1]: "Ed25519 verify",
        selected_names[2]: "AES-GCM encrypt, 10 KiB",
        selected_names[3]: "Policy evaluation, 50 rules",
        selected_names[4]: "Policy evaluation, 200 rules",
        selected_names[5]: "Synthetic authorization gate",
    }
    subset = df.set_index("operation").loc[selected_names].reset_index()
    labels = [labels_map[x] for x in subset["operation"]]
    y = np.arange(len(subset))
    h = 0.34
    fig, ax = plt.subplots(figsize=(7.15, 3.15))
    ax.barh(y + h / 2, subset["p50_ms"], height=h, label="p50", color="#457B9D")
    ax.barh(y - h / 2, subset["p95_ms"], height=h, label="p95", color="#E76F51")
    ax.set_yticks(y, labels=labels)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel("Latency (ms, logarithmic scale)")
    ax.grid(axis="x", which="both", alpha=0.25, linewidth=0.6)
    ax.legend(loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "benchmark_latency")


def rounded_box(ax, xy, width, height, text, *, facecolor, edgecolor="#2B2D42", fontsize=8, weight="normal"):
    box = patches.FancyBboxPatch(
        xy, width, height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=0.9,
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=fontsize, weight=weight, wrap=True)
    return box


def arrow(ax, start, end, *, style="-|>", connectionstyle="arc3", color="#343A40", linewidth=0.9, alpha=0.9):
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle=style, connectionstyle=connectionstyle, color=color, lw=linewidth, alpha=alpha))


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.992, "Reference architecture and governed cross-border decision path", ha="center", va="top", fontsize=10.0, weight="bold")

    # External actors
    rounded_box(ax, (0.13, 0.855), 0.22, 0.07, "Learners & staff\npasskey • device posture", facecolor="#E8F1F8", fontsize=7.0, weight="bold")
    rounded_box(ax, (0.39, 0.855), 0.22, 0.07, "Institutions\nissuer • relying party", facecolor="#E8F1F8", fontsize=7.0, weight="bold")
    rounded_box(ax, (0.65, 0.855), 0.22, 0.07, "Partners & regulators\ncontrolled verification", facecolor="#E8F1F8", fontsize=7.0, weight="bold")

    rounded_box(ax, (0.13, 0.755), 0.74, 0.065, "Regional access and transfer gateways — North | West | East | Central | Southern Africa\nPEP • API gateway • mTLS • rate limits • low-bandwidth synchronization", facecolor="#DDEBF7", fontsize=7.0, weight="bold")

    # Row labels
    rounded_box(ax, (0.015, 0.595), 0.095, 0.105, "TRUST &\nPOLICY", facecolor="#D8E8CE", fontsize=7.2, weight="bold")
    rounded_box(ax, (0.015, 0.405), 0.095, 0.105, "EDUCATION\nPLANE", facecolor="#F7E4BE", fontsize=7.2, weight="bold")
    rounded_box(ax, (0.015, 0.205), 0.095, 0.115, "DATA &\nPRIVACY", facecolor="#F5D5D5", fontsize=7.2, weight="bold")

    # Trust and policy plane
    rounded_box(ax, (0.13, 0.595), 0.17, 0.105, "Identity\nFIDO2 • OIDC\nworkload ID", facecolor="#E9F5DB", fontsize=6.8, weight="bold")
    rounded_box(ax, (0.32, 0.595), 0.17, 0.105, "PDP / policy engine\nsubject • device\npurpose • risk", facecolor="#E9F5DB", fontsize=6.7, weight="bold")
    rounded_box(ax, (0.51, 0.595), 0.17, 0.105, "Jurisdiction profile\nbasis • safeguards\nfields • retention", facecolor="#E9F5DB", fontsize=6.7, weight="bold")
    rounded_box(ax, (0.70, 0.595), 0.17, 0.105, "Consent / rights\nobligations\nreceipts", facecolor="#E9F5DB", fontsize=6.8, weight="bold")

    # Education plane
    rounded_box(ax, (0.13, 0.405), 0.17, 0.105, "LMS / content\nlocal-first delivery\nevent stream", facecolor="#FFF0D6", fontsize=6.8, weight="bold")
    rounded_box(ax, (0.32, 0.405), 0.17, 0.105, "SIS / assessment\ngrades\nproctoring bounds", facecolor="#FFF0D6", fontsize=6.8, weight="bold")
    rounded_box(ax, (0.51, 0.405), 0.17, 0.105, "Credential issuer\nW3C VC 2.0\nstatus list", facecolor="#FFF0D6", fontsize=6.8, weight="bold")
    rounded_box(ax, (0.70, 0.405), 0.17, 0.105, "Wallet / verifier\nselective claims\noffline freshness", facecolor="#FFF0D6", fontsize=6.8, weight="bold")

    # Data plane
    rounded_box(ax, (0.13, 0.205), 0.23, 0.115, "Regional vaults\nclassification\nfield encryption • tokenization\nKMS/HSM boundary", facecolor="#FBE5E5", fontsize=6.7, weight="bold")
    rounded_box(ax, (0.385, 0.205), 0.23, 0.115, "Minimized claim views\npurpose • fields\nexpiry • receipts\ndeletion hooks", facecolor="#FBE5E5", fontsize=6.7, weight="bold")
    rounded_box(ax, (0.64, 0.205), 0.23, 0.115, "Private analytics\npseudonymization\naggregation • budgets\nfederation", facecolor="#FBE5E5", fontsize=6.7, weight="bold")

    rounded_box(ax, (0.13, 0.045), 0.74, 0.095, "ACCOUNTABILITY & RESILIENCE\nSigned receipts • append-only audit • SIEM/DLP\nIncident workflow • policy versions • asynchronous buffering", facecolor="#EDE7F6", fontsize=6.9, weight="bold")

    # Main flow arrows
    for x in (0.24, 0.50, 0.76):
        arrow(ax, (x, 0.855), (x, 0.82))
    arrow(ax, (0.50, 0.755), (0.405, 0.70))
    for x in (0.215, 0.405, 0.595, 0.785):
        arrow(ax, (x, 0.595), (x, 0.51))
    arrow(ax, (0.215, 0.405), (0.245, 0.32))
    arrow(ax, (0.405, 0.405), (0.50, 0.32))
    arrow(ax, (0.595, 0.405), (0.50, 0.32))
    arrow(ax, (0.785, 0.405), (0.755, 0.32))
    for x in (0.245, 0.50, 0.755):
        arrow(ax, (x, 0.205), (x, 0.14))

    # Policy relations
    arrow(ax, (0.405, 0.595), (0.50, 0.32), connectionstyle="arc3,rad=-0.10", color="#0B7285")

    save(fig, "reference_architecture")

def main() -> None:
    connectivity()
    governance()
    coverage()
    benchmark()
    from generate_architecture_v3 import main as generate_architecture_v3
    generate_architecture_v3()


if __name__ == "__main__":
    main()
