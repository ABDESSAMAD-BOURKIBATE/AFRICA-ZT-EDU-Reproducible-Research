#!/usr/bin/env python3
"""Reproducible single-host microbenchmark for the paper.

The benchmark uses only synthetic data. It measures cryptographic and policy
operations that approximate a cross-border authorization gateway. Results are
microbenchmarks, not end-to-end production latency claims.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import cryptography
import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SEED = 20260817
random.seed(SEED)


@dataclass(frozen=True)
class Rule:
    role: str
    resource: str
    action: str
    purpose: str
    origin: str
    destination: str
    min_device_score: int
    required_basis: str
    effect: str = "permit"


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def make_credential() -> dict:
    return {
        "@context": ["https://www.w3.org/ns/credentials/v2"],
        "id": "urn:uuid:00000000-0000-4000-8000-000000000001",
        "type": ["VerifiableCredential", "AcademicCredential"],
        "issuer": "did:web:issuer.example.africa",
        "validFrom": "2026-08-17T00:00:00Z",
        "credentialSubject": {
            "id": "did:key:z6MkSyntheticLearner",
            "achievement": {
                "name": "Synthetic Cross-Border Digital Learning Certificate",
                "level": "micro-credential",
                "credits": 6,
                "language": "en",
            },
            "claims": {
                "completion": True,
                "scoreBand": "distinction",
                "issuingCountry": "MA",
            },
        },
        "credentialStatus": {
            "id": "https://status.example.africa/list/1#945",
            "type": "BitstringStatusListEntry",
            "statusPurpose": "revocation",
            "statusListIndex": "945",
            "statusListCredential": "https://status.example.africa/list/1",
        },
    }


def make_rules(count: int) -> list[Rule]:
    if count < 2:
        raise ValueError("count must be at least 2")
    roles = ["learner", "faculty", "registrar", "auditor", "partner"]
    resources = ["profile", "grade", "credential", "analytics", "proctoring"]
    actions = ["read", "issue", "verify", "aggregate", "export"]
    purposes = ["instruction", "assessment", "credential-verification", "support", "research"]
    jurisdictions = ["MA", "KE", "ZA", "NG", "SN"]
    bases = ["consent", "contract", "public-task", "adequacy", "safeguards"]
    rules: list[Rule] = []
    for i in range(count - 1):
        rules.append(
            Rule(
                role=roles[i % len(roles)],
                resource=resources[(i // 2) % len(resources)],
                action=actions[(i // 3) % len(actions)],
                purpose=purposes[(i // 5) % len(purposes)],
                origin=jurisdictions[(i // 7) % len(jurisdictions)],
                destination=jurisdictions[(i // 11 + 1) % len(jurisdictions)],
                min_device_score=60 + (i % 4) * 10,
                required_basis=bases[i % len(bases)],
            )
        )
    # Deliberately place the matching rule last to measure a conservative
    # sequential-policy path rather than best-case first-match latency.
    rules.append(
        Rule(
            role="registrar",
            resource="credential",
            action="verify",
            purpose="credential-verification",
            origin="MA",
            destination="KE",
            min_device_score=75,
            required_basis="safeguards",
        )
    )
    return rules


def evaluate_policy(rules: Sequence[Rule], request: dict) -> bool:
    for rule in rules:
        if (
            request["role"] == rule.role
            and request["resource"] == rule.resource
            and request["action"] == rule.action
            and request["purpose"] == rule.purpose
            and request["origin"] == rule.origin
            and request["destination"] == rule.destination
            and request["device_score"] >= rule.min_device_score
            and request["transfer_basis"] == rule.required_basis
        ):
            return rule.effect == "permit"
    return False


def percentile(values_ns: Sequence[int], q: float) -> float:
    return float(np.percentile(np.asarray(values_ns, dtype=np.float64), q))


def measure(
    label: str,
    fn: Callable[[], object],
    *,
    iterations: int,
    warmup: int,
    payload_bytes: int = 0,
    rules: int = 0,
) -> tuple[dict, list[dict]]:
    for _ in range(warmup):
        fn()

    samples_ns: list[int] = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        fn()
        samples_ns.append(time.perf_counter_ns() - start)

    mean_ns = statistics.fmean(samples_ns)
    summary = {
        "operation": label,
        "payload_bytes": payload_bytes,
        "rules": rules,
        "iterations": iterations,
        "p50_ms": statistics.median(samples_ns) / 1_000_000,
        "p95_ms": percentile(samples_ns, 95) / 1_000_000,
        "mean_ms": mean_ns / 1_000_000,
        "std_ms": statistics.pstdev(samples_ns) / 1_000_000,
        "ops_per_second": 1_000_000_000 / mean_ns,
    }
    raw = [
        {
            "operation": label,
            "sample": i,
            "latency_ns": value,
            "latency_ms": value / 1_000_000,
        }
        for i, value in enumerate(samples_ns, start=1)
    ]
    return summary, raw


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--scale", type=float, default=1.0, help="Scale sample counts (default: 1.0)")
    args = parser.parse_args()
    if args.scale <= 0:
        parser.error("--scale must be positive")

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    credential_bytes = canonical_json(make_credential())
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    signature = private_key.sign(credential_bytes)

    aes_key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(aes_key)
    associated_data = b"policy:v1|origin:MA|destination:KE|purpose:credential-verification"
    buffers = {
        1024: os.urandom(1024),
        10 * 1024: os.urandom(10 * 1024),
        100 * 1024: os.urandom(100 * 1024),
    }

    rules_50 = make_rules(50)
    rules_200 = make_rules(200)
    request = {
        "role": "registrar",
        "resource": "credential",
        "action": "verify",
        "purpose": "credential-verification",
        "origin": "MA",
        "destination": "KE",
        "device_score": 87,
        "transfer_basis": "safeguards",
    }

    # Cache ciphertexts for decrypt-only measurements.
    decrypt_inputs: dict[int, tuple[bytes, bytes]] = {}
    for size, buf in buffers.items():
        nonce = os.urandom(12)
        decrypt_inputs[size] = (nonce, aes.encrypt(nonce, buf, associated_data))

    def scaled(n: int) -> int:
        return max(100, int(round(n * args.scale)))

    cases: list[tuple[str, Callable[[], object], int, int, int]] = []
    cases.append(("Ed25519 sign (VC payload)", lambda: private_key.sign(credential_bytes), scaled(5000), len(credential_bytes), 0))
    cases.append(("Ed25519 verify (VC payload)", lambda: public_key.verify(signature, credential_bytes), scaled(5000), len(credential_bytes), 0))

    for size, buf in buffers.items():
        cases.append((f"AES-256-GCM encrypt ({size // 1024} KiB)", lambda b=buf: aes.encrypt(os.urandom(12), b, associated_data), scaled(3000 if size < 100 * 1024 else 1500), size, 0))
        nonce, ciphertext = decrypt_inputs[size]
        cases.append((f"AES-256-GCM decrypt ({size // 1024} KiB)", lambda n=nonce, c=ciphertext: aes.decrypt(n, c, associated_data), scaled(3000 if size < 100 * 1024 else 1500), size, 0))

    cases.append(("Sequential policy evaluation (50 rules)", lambda: evaluate_policy(rules_50, request), scaled(6000), 0, 50))
    cases.append(("Sequential policy evaluation (200 rules)", lambda: evaluate_policy(rules_200, request), scaled(4000), 0, 200))

    def end_to_end_gate() -> bytes:
        public_key.verify(signature, credential_bytes)
        if not evaluate_policy(rules_200, request):
            raise RuntimeError("Synthetic policy unexpectedly denied the request")
        nonce = os.urandom(12)
        ciphertext = aes.encrypt(nonce, buffers[10 * 1024], associated_data)
        decision_receipt = {
            "decision": "permit",
            "policy_version": "2026.08.17",
            "subject": "did:key:z6MkSyntheticLearner",
            "origin": "MA",
            "destination": "KE",
            "purpose": "credential-verification",
            "payload_digest": hashlib.sha256(ciphertext).hexdigest(),
        }
        return hashlib.sha256(canonical_json(decision_receipt)).digest()

    cases.append(("Synthetic authorization gate (200 rules + verify + 10 KiB encrypt)", end_to_end_gate, scaled(2500), 10 * 1024 + len(credential_bytes), 200))

    summaries: list[dict] = []
    raw_rows: list[dict] = []
    warmup = scaled(250)
    for label, fn, iterations, payload_bytes, rule_count in cases:
        summary, raw = measure(
            label,
            fn,
            iterations=iterations,
            warmup=warmup,
            payload_bytes=payload_bytes,
            rules=rule_count,
        )
        summaries.append(summary)
        raw_rows.extend(raw)
        print(f"{label:68s} p50={summary['p50_ms']:.4f} ms p95={summary['p95_ms']:.4f} ms")

    write_csv(output_dir / "benchmark_summary.csv", summaries)
    write_csv(output_dir / "benchmark_raw.csv", raw_rows)

    metadata = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": SEED,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "cryptography": cryptography.__version__,
        "numpy": np.__version__,
        "credential_payload_bytes": len(credential_bytes),
        "notes": [
            "Synthetic data only; no student records or personal data were processed.",
            "Single-host microbenchmark; excludes network, database, HSM, container-orchestration, and user-interface latency.",
            "Sequential policy matching places the permit rule last to avoid a best-case first-match measurement.",
        ],
    }
    (output_dir / "benchmark_environment.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
