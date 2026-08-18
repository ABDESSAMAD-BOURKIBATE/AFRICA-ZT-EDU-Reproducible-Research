#!/usr/bin/env python3
"""Reproducible synthetic evaluation for AFRICA-ZT-EDU.

This simulation compares three policy-enforcement designs on the same synthetic
cross-border education workload:
  1. Legacy perimeter + coarse RBAC
  2. Zero-trust contextual ABAC without jurisdiction/purpose controls
  3. AFRICA-ZT-EDU with jurisdiction, purpose, lawful-basis, minimization,
     and evidence-bound transfer receipts.

The generated data are synthetic and are not intended to represent any country,
institution, or legal system. Jurisdiction profiles are deliberately abstract.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, Iterable, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Embed TrueType outlines in generated PDFs rather than Matplotlib's Type 3
# bitmap-like glyphs. This improves archival and IEEE PDF-preflight compatibility.
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

ARCHS = ("Legacy RBAC", "Zero-Trust ABAC", "AFRICA-ZT-EDU")
ROLE_NAMES = np.array(["student", "instructor", "registrar", "support", "researcher", "service"])
RESOURCE_NAMES = np.array([
    "identity_profile",
    "enrollment_record",
    "transcript",
    "assessment",
    "learning_analytics",
    "aggregate_report",
])
ACTION_NAMES = np.array(["read", "update", "export", "aggregate", "verify"])
PURPOSE_NAMES = np.array([
    "course_delivery",
    "credential_verification",
    "student_support",
    "administration",
    "research_analytics",
    "marketing",
])
BASIS_NAMES = np.array(["none", "contract", "consent", "public_task", "research_approval"])

# Per-resource sensitivity and full schema size.
SENSITIVITY = np.array([4, 2, 3, 3, 3, 1], dtype=np.int8)
FULL_FIELDS = np.array([18, 14, 16, 20, 24, 8], dtype=np.int16)

# Minimum fields needed for [resource, purpose]. Values are intentionally
# conservative and illustrative; they are not legal prescriptions.
MIN_FIELDS = np.array(
    [
        [3, 4, 6, 8, 2, 3],   # identity profile
        [5, 4, 6, 9, 3, 3],   # enrollment
        [4, 5, 5, 8, 3, 2],   # transcript
        [8, 3, 6, 7, 4, 2],   # assessment
        [6, 2, 5, 6, 4, 3],   # learning analytics
        [4, 4, 4, 5, 4, 4],   # aggregate report
    ],
    dtype=np.int16,
)

# Purpose compatibility matrix [resource, purpose].
PURPOSE_COMPAT = np.array(
    [
        [1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0],
        [1, 1, 0, 1, 1, 0],
        [1, 0, 1, 1, 1, 0],
        [1, 0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1],
    ],
    dtype=bool,
)

# Valid lawful bases by purpose [purpose, basis].
BASIS_OK = np.array(
    [
        [0, 1, 0, 1, 0],  # course delivery
        [0, 1, 1, 1, 0],  # credential verification
        [0, 1, 1, 1, 0],  # student support
        [0, 1, 0, 1, 0],  # administration
        [0, 0, 1, 0, 1],  # research analytics
        [0, 0, 1, 0, 0],  # marketing
    ],
    dtype=bool,
)

# Role/resource/action authorization cube.
ROLE_RULES = np.zeros((len(ROLE_NAMES), len(RESOURCE_NAMES), len(ACTION_NAMES)), dtype=bool)
# Student
ROLE_RULES[0, :, 0] = [1, 1, 1, 1, 1, 1]
ROLE_RULES[0, [0, 2], 4] = True
# Instructor
ROLE_RULES[1, [1, 2, 3, 4, 5], 0] = True
ROLE_RULES[1, [3, 4], 1] = True
ROLE_RULES[1, [3, 4, 5], 3] = True
# Registrar
ROLE_RULES[2, [0, 1, 2, 3, 5], 0] = True
ROLE_RULES[2, [0, 1, 2], 1] = True
ROLE_RULES[2, [0, 1, 2], 2] = True
ROLE_RULES[2, [0, 1, 2], 4] = True
# Support
ROLE_RULES[3, [0, 1, 3, 4, 5], 0] = True
ROLE_RULES[3, [1, 4], 1] = True
# Researcher
ROLE_RULES[4, [2, 3, 4, 5], 0] = True
ROLE_RULES[4, [3, 4, 5], 3] = True
ROLE_RULES[4, [4, 5], 2] = True
# Service workload
ROLE_RULES[5, :, :] = True


def _sample_legitimate_pairs(rng: np.random.Generator, roles: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Sample mostly role-conforming resource/action pairs with a controlled misuse tail."""
    n = roles.size
    resources = np.empty(n, dtype=np.int8)
    actions = np.empty(n, dtype=np.int8)
    misuse = rng.random(n) < 0.18
    resources[misuse] = rng.integers(0, len(RESOURCE_NAMES), misuse.sum(), dtype=np.int8)
    actions[misuse] = rng.integers(0, len(ACTION_NAMES), misuse.sum(), dtype=np.int8)
    for role in range(len(ROLE_NAMES)):
        idx = np.flatnonzero((roles == role) & ~misuse)
        allowed = np.argwhere(ROLE_RULES[role])
        pick = rng.integers(0, len(allowed), len(idx))
        resources[idx] = allowed[pick, 0].astype(np.int8)
        actions[idx] = allowed[pick, 1].astype(np.int8)
    return resources, actions


def _basis_for_purpose(rng: np.random.Generator, purpose: np.ndarray) -> np.ndarray:
    """Generate a lawful basis that is correct most of the time and absent/misaligned otherwise."""
    n = purpose.size
    basis = np.empty(n, dtype=np.int8)
    aligned = rng.random(n) < 0.91
    for p in range(len(PURPOSE_NAMES)):
        idx = np.flatnonzero((purpose == p) & aligned)
        valid = np.flatnonzero(BASIS_OK[p])
        basis[idx] = rng.choice(valid, len(idx)).astype(np.int8)
    idx = np.flatnonzero(~aligned)
    basis[idx] = rng.choice(np.arange(len(BASIS_NAMES)), len(idx), p=[0.55, 0.12, 0.12, 0.11, 0.10]).astype(np.int8)
    return basis


def _transfer_admissible(
    src: np.ndarray,
    dst: np.ndarray,
    sensitivity: np.ndarray,
    purpose: np.ndarray,
    action: np.ndarray,
    basis_ok: np.ndarray,
) -> np.ndarray:
    """Evaluate an abstract cross-border transfer policy over synthetic jurisdiction profiles."""
    same = src == dst
    src_profile = src // 4  # 0=strict residency, 1=conditional, 2=interoperable
    src_bloc = src // 4
    dst_bloc = dst // 4
    trusted = (src_bloc == dst_bloc) | (((src + dst) % 7) == 0)

    allowed = same.copy()
    cross = ~same

    # Strict residency profile.
    m = cross & (src_profile == 0)
    allowed[m & (sensitivity == 1) & basis_ok] = True
    allowed[m & (sensitivity == 2) & trusted & basis_ok] = True

    # Conditional transfer profile.
    m = cross & (src_profile == 1)
    allowed[m & (sensitivity <= 2) & basis_ok] = True
    allowed[m & (sensitivity == 3) & trusted & basis_ok & (purpose != 5)] = True

    # Interoperable/trusted-flow profile.
    m = cross & (src_profile == 2)
    allowed[m & (sensitivity <= 2) & basis_ok] = True
    allowed[
        m
        & (sensitivity == 3)
        & basis_ok
        & (purpose != 5)
        & (trusted | (action == 3) | (action == 4))
    ] = True
    # Critical identity transfers are only modeled as selective verification.
    allowed[
        m
        & (sensitivity == 4)
        & trusted
        & basis_ok
        & (purpose == 1)
        & (action == 4)
    ] = True
    return allowed


def _latencies(rng: np.random.Generator, n: int, cross: np.ndarray) -> Dict[str, np.ndarray]:
    """Synthetic in-process policy latency, excluding Internet/network RTT."""
    base = 0.45 + rng.gamma(shape=2.2, scale=0.23, size=n)
    legacy = base + rng.gamma(shape=1.4, scale=0.16, size=n)
    zt = legacy + 0.55 + rng.gamma(shape=3.0, scale=0.72, size=n)
    cache_hit = rng.random(n) < 0.96
    jurisdiction = np.where(
        cache_hit,
        0.28 + rng.gamma(shape=1.5, scale=0.16, size=n),
        2.00 + rng.gamma(shape=2.0, scale=0.50, size=n),
    )
    proposed = (
        zt
        + jurisdiction
        + 0.35
        + rng.gamma(shape=2.0, scale=0.24, size=n)
        + 0.35
        + rng.gamma(shape=1.5, scale=0.22, size=n)
        + cross.astype(float) * (0.45 + rng.gamma(shape=1.5, scale=0.18, size=n))
    )
    return {ARCHS[0]: legacy, ARCHS[1]: zt, ARCHS[2]: proposed}


def _metrics_for_arch(
    architecture: str,
    permit: np.ndarray,
    truth: np.ndarray,
    candidate_prohibited: np.ndarray,
    cross: np.ndarray,
    latency: np.ndarray,
    disclosed_fields: np.ndarray,
) -> Dict[str, float]:
    invalid = ~truth
    valid = truth
    permits = int(permit.sum())
    false_permit = int((permit & invalid).sum())
    true_permit = int((permit & valid).sum())
    false_deny = int((~permit & valid).sum())
    candidate_n = int(candidate_prohibited.sum())
    escapes = int((permit & candidate_prohibited).sum())
    cross_permits = int((permit & cross).sum())

    receipt_coverage = 100.0 if architecture == ARCHS[2] and cross_permits else 0.0
    return {
        "architecture": architecture,
        "requests": float(len(permit)),
        "permit_rate_pct": 100.0 * permits / len(permit),
        "false_permit_rate_pct": 100.0 * false_permit / max(1, int(invalid.sum())),
        "permit_precision_pct": 100.0 * true_permit / max(1, permits),
        "legitimate_denial_rate_pct": 100.0 * false_deny / max(1, int(valid.sum())),
        "prohibited_transfer_escape_pct": 100.0 * escapes / max(1, candidate_n),
        "blocked_prohibited_transfer_pct": 100.0 * (candidate_n - escapes) / max(1, candidate_n),
        "mean_latency_ms": float(np.mean(latency)),
        "p50_latency_ms": float(np.quantile(latency, 0.50)),
        "p95_latency_ms": float(np.quantile(latency, 0.95)),
        "mean_fields_disclosed": float(np.mean(disclosed_fields[valid])),
        "median_fields_disclosed": float(np.median(disclosed_fields[valid])),
        "receipt_coverage_pct": receipt_coverage,
        "valid_request_share_pct": 100.0 * valid.mean(),
        "prohibited_transfer_candidates": float(candidate_n),
    }


def run_seed(seed: int, n: int, stale_allow: float, stale_deny: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    roles = rng.choice(len(ROLE_NAMES), n, p=[0.43, 0.24, 0.08, 0.08, 0.11, 0.06]).astype(np.int8)
    resources, actions = _sample_legitimate_pairs(rng, roles)
    sensitivity = SENSITIVITY[resources]

    # Two institutions per jurisdiction; institution identity is not otherwise material.
    src = rng.integers(0, 12, n, dtype=np.int8)
    is_cross = rng.random(n) < 0.38
    dst = src.copy()
    dst[is_cross] = rng.integers(0, 12, is_cross.sum(), dtype=np.int8)
    # Ensure intended cross-border rows actually cross a jurisdiction.
    same_after = is_cross & (dst == src)
    dst[same_after] = ((dst[same_after] + rng.integers(1, 12, same_after.sum())) % 12).astype(np.int8)
    cross = src != dst

    purpose = rng.choice(len(PURPOSE_NAMES), n, p=[0.29, 0.16, 0.14, 0.20, 0.16, 0.05]).astype(np.int8)
    basis = _basis_for_purpose(rng, purpose)

    role_ok = ROLE_RULES[roles, resources, actions]
    relationship_ok = rng.random(n) < np.where(roles == 5, 0.975, 0.935)

    authn_level = rng.choice([1, 2, 3], n, p=[0.08, 0.55, 0.37]).astype(np.int8)
    required_authn = np.where((sensitivity >= 3) | (actions == 2) | (actions == 4), 3,
                             np.where((sensitivity == 2) | (actions == 1), 2, 1))
    authn_ok = authn_level >= required_authn
    device_trusted = rng.random(n) < 0.91
    device_required = (sensitivity >= 3) | (actions == 1) | (actions == 2)
    device_ok = (~device_required) | device_trusted
    session_age = rng.exponential(scale=155.0, size=n)
    session_limit = np.where(sensitivity == 4, 60.0, np.where(sensitivity == 3, 180.0, 600.0))
    session_ok = session_age <= session_limit

    high_risk = rng.random(n) < 0.055
    risk = np.where(high_risk, rng.beta(7.0, 2.0, n), rng.beta(2.0, 10.0, n))
    risk_threshold = np.where(sensitivity >= 3, 0.62, 0.78)
    risk_ok = risk <= risk_threshold

    purpose_ok = PURPOSE_COMPAT[resources, purpose]
    lawful_basis_ok = BASIS_OK[purpose, basis]
    transfer_ok = _transfer_admissible(src, dst, sensitivity, purpose, actions, lawful_basis_ok)

    zt_core = role_ok & relationship_ok & authn_ok & device_ok & session_ok & risk_ok
    truth = zt_core & purpose_ok & lawful_basis_ok & transfer_ok

    legacy_permit = role_ok & relationship_ok & (authn_level >= 1)
    zt_permit = zt_core

    observed_transfer = transfer_ok.copy()
    flip_allow = (~transfer_ok) & (rng.random(n) < stale_allow)
    flip_deny = transfer_ok & (rng.random(n) < stale_deny)
    observed_transfer[flip_allow] = True
    observed_transfer[flip_deny] = False
    proposed_permit = zt_core & purpose_ok & lawful_basis_ok & observed_transfer

    candidate_prohibited = zt_core & purpose_ok & lawful_basis_ok & cross & (~transfer_ok)
    lat = _latencies(rng, n, cross)
    full_fields = FULL_FIELDS[resources]
    min_fields = np.minimum(full_fields, MIN_FIELDS[resources, purpose])

    frames = []
    frames.append(_metrics_for_arch(ARCHS[0], legacy_permit, truth, candidate_prohibited, cross, lat[ARCHS[0]], full_fields))
    frames.append(_metrics_for_arch(ARCHS[1], zt_permit, truth, candidate_prohibited, cross, lat[ARCHS[1]], full_fields))
    frames.append(_metrics_for_arch(ARCHS[2], proposed_permit, truth, candidate_prohibited, cross, lat[ARCHS[2]], min_fields))
    df = pd.DataFrame(frames)
    df.insert(0, "seed", seed)
    return df


def summarize(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    numeric = [c for c in seed_metrics.columns if c not in ("seed", "architecture")]
    rows = []
    z = 1.959963984540054
    for architecture, group in seed_metrics.groupby("architecture", sort=False):
        row: Dict[str, float | str] = {"architecture": architecture}
        for metric in numeric:
            values = group[metric].astype(float)
            mean = values.mean()
            std = values.std(ddof=1)
            half = z * std / math.sqrt(len(values))
            row[f"{metric}_mean"] = mean
            row[f"{metric}_ci_low"] = mean - half
            row[f"{metric}_ci_high"] = mean + half
            row[f"{metric}_std"] = std
        rows.append(row)
    return pd.DataFrame(rows)


def dp_experiment(seed: int = 20260817, queries: int = 50000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    epsilons = np.array([0.25, 0.5, 1.0, 2.0, 4.0, 8.0])
    cohort_size = rng.integers(25, 251, queries)
    rate = rng.beta(3.0, 4.0, queries)
    true_count = rng.binomial(cohort_size, rate)
    rows = []
    for eps in epsilons:
        noisy = np.clip(true_count + rng.laplace(0.0, 1.0 / eps, queries), 0.0, cohort_size)
        pp_error = 100.0 * np.abs(noisy - true_count) / cohort_size
        rows.append({
            "epsilon": eps,
            "median_abs_error_pp": float(np.median(pp_error)),
            "mean_abs_error_pp": float(np.mean(pp_error)),
            "p95_abs_error_pp": float(np.quantile(pp_error, 0.95)),
        })
    return pd.DataFrame(rows)


def staleness_experiment(n: int = 200000, seed: int = 8128) -> pd.DataFrame:
    rates = np.array([0.0, 0.001, 0.0025, 0.005, 0.01, 0.02, 0.05])
    rng = np.random.default_rng(seed)
    # Directly estimate the enforcement consequence on a set of otherwise-valid,
    # prohibited transfers. This isolates registry staleness from unrelated checks.
    draws = rng.random(n)
    rows = []
    for rate in rates:
        escape = draws < rate
        rows.append({
            "stale_policy_rate_pct": 100.0 * rate,
            "prohibited_transfer_escape_pct": 100.0 * escape.mean(),
            "blocked_prohibited_transfer_pct": 100.0 * (1.0 - escape.mean()),
        })
    return pd.DataFrame(rows)


def _ci(summary: pd.DataFrame, arch: str, metric: str) -> Tuple[float, float, float]:
    row = summary.loc[summary["architecture"] == arch].iloc[0]
    return float(row[f"{metric}_mean"]), float(row[f"{metric}_ci_low"]), float(row[f"{metric}_ci_high"])


def make_figures(summary: pd.DataFrame, dp: pd.DataFrame, stale: pd.DataFrame, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)

    # Security decision errors.
    x = np.arange(len(ARCHS))
    fp = np.array([_ci(summary, a, "false_permit_rate_pct")[0] for a in ARCHS])
    fp_lo = np.array([_ci(summary, a, "false_permit_rate_pct")[1] for a in ARCHS])
    fp_hi = np.array([_ci(summary, a, "false_permit_rate_pct")[2] for a in ARCHS])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(x, fp, yerr=np.vstack([fp - fp_lo, fp_hi - fp]), capsize=4)
    ax.set_xticks(x, ARCHS, rotation=12, ha="right")
    ax.set_ylabel("False permit rate among policy-invalid requests (%)")
    ax.set_title("Access-decision safety across architectures")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "false_permit_rate.pdf", bbox_inches="tight")
    fig.savefig(out / "false_permit_rate.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    # Transfer blocking.
    blocked = np.array([_ci(summary, a, "blocked_prohibited_transfer_pct")[0] for a in ARCHS])
    blo = np.array([_ci(summary, a, "blocked_prohibited_transfer_pct")[1] for a in ARCHS])
    bhi = np.array([_ci(summary, a, "blocked_prohibited_transfer_pct")[2] for a in ARCHS])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(x, blocked, yerr=np.vstack([blocked - blo, bhi - blocked]), capsize=4)
    ax.set_xticks(x, ARCHS, rotation=12, ha="right")
    ax.set_ylim(0, 105)
    ax.set_ylabel("Blocked prohibited transfers (%)")
    ax.set_title("Jurisdiction-aware transfer enforcement")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "transfer_blocking.pdf", bbox_inches="tight")
    fig.savefig(out / "transfer_blocking.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    # Latency.
    p50 = np.array([_ci(summary, a, "p50_latency_ms")[0] for a in ARCHS])
    p95 = np.array([_ci(summary, a, "p95_latency_ms")[0] for a in ARCHS])
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(x - width / 2, p50, width, label="p50")
    ax.bar(x + width / 2, p95, width, label="p95")
    ax.set_xticks(x, ARCHS, rotation=12, ha="right")
    ax.set_ylabel("In-process policy latency (ms)")
    ax.set_title("Latency excludes network round-trip time")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "policy_latency.pdf", bbox_inches="tight")
    fig.savefig(out / "policy_latency.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    # Data minimization.
    fields = np.array([_ci(summary, a, "mean_fields_disclosed")[0] for a in ARCHS])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(x, fields)
    ax.set_xticks(x, ARCHS, rotation=12, ha="right")
    ax.set_ylabel("Mean fields released per legitimate request")
    ax.set_title("Purpose-bound data minimization")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "data_minimization.pdf", bbox_inches="tight")
    fig.savefig(out / "data_minimization.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    # Differential privacy utility.
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(dp["epsilon"], dp["median_abs_error_pp"], marker="o", label="Median")
    ax.plot(dp["epsilon"], dp["p95_abs_error_pp"], marker="s", label="95th percentile")
    ax.set_xscale("log", base=2)
    ax.set_xticks(dp["epsilon"], [str(x) for x in dp["epsilon"]])
    ax.set_xlabel(r"Privacy budget $\epsilon$ (illustrative)")
    ax.set_ylabel("Absolute error in cohort rate (percentage points)")
    ax.set_title("Privacy-utility sensitivity for DP aggregate counts")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "dp_utility.pdf", bbox_inches="tight")
    fig.savefig(out / "dp_utility.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    # Policy staleness sensitivity.
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(stale["stale_policy_rate_pct"], stale["prohibited_transfer_escape_pct"], marker="o")
    ax.set_xlabel("Stale/incorrect transfer-policy entries (%)")
    ax.set_ylabel("Prohibited-transfer escape rate (%)")
    ax.set_title("Sensitivity to jurisdiction-policy registry staleness")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "policy_staleness.pdf", bbox_inches="tight")
    fig.savefig(out / "policy_staleness.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests-per-seed", type=int, default=100_000)
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--stale-allow", type=float, default=0.0025)
    parser.add_argument("--stale-deny", type=float, default=0.0010)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--figures", type=Path, default=Path(__file__).resolve().parents[1] / "figures")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    all_metrics = []
    for i in range(args.seeds):
        all_metrics.append(run_seed(20260817 + i, args.requests_per_seed, args.stale_allow, args.stale_deny))
    seed_metrics = pd.concat(all_metrics, ignore_index=True)
    summary = summarize(seed_metrics)
    dp = dp_experiment()
    stale = staleness_experiment()

    seed_metrics.to_csv(args.output / "seed_metrics.csv", index=False)
    summary.to_csv(args.output / "results_summary.csv", index=False)
    dp.to_csv(args.output / "dp_utility.csv", index=False)
    stale.to_csv(args.output / "policy_staleness.csv", index=False)
    make_figures(summary, dp, stale, args.figures)

    pd.set_option("display.max_columns", 200)
    print(summary[[
        "architecture",
        "false_permit_rate_pct_mean",
        "blocked_prohibited_transfer_pct_mean",
        "p50_latency_ms_mean",
        "p95_latency_ms_mean",
        "mean_fields_disclosed_mean",
        "permit_precision_pct_mean",
        "legitimate_denial_rate_pct_mean",
    ]].to_string(index=False))
    print("\nDP utility:\n", dp.to_string(index=False))


if __name__ == "__main__":
    main()
