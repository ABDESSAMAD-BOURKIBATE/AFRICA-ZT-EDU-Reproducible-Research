# Source and Claim Audit

**Evidence cutoff:** 18 August 2026  
**Purpose:** distinguish current official context, dated snapshots, peer-reviewed literature, synthetic data, analytical scoring, and measured computation.

## 1. Official standards and policy sources

| Source | Status used in the manuscript | Audit note |
|---|---|---|
| NIST SP 800-207 | Final publication (2020) | Primary source for zero-trust principles. |
| NIST SP 800-207A | Final publication (2023) | Primary source for cloud-native, multi-location zero-trust access control. |
| NIST SP 800-63-4 | Final publication (July 2025) | Primary source for current NIST digital-identity guidance. |
| NIST SP 1800-35 | Final publication (June 2025) | Implementation-oriented zero-trust practice guide. |
| NIST SP 800-162 / SP 800-204B | Final publications | Primary sources for ABAC and service-mesh ABAC. |
| W3C Verifiable Credentials Data Model v2.0 | W3C Recommendation dated 15 May 2025 | Treated as a final Recommendation. |
| W3C Bitstring Status List v1.0 | W3C Recommendation dated 15 May 2025 | Used for credential status and privacy-oriented revocation discussion. |
| W3C Web Authentication Level 3 | Candidate Recommendation Snapshot dated 26 May 2026 | Explicitly identified as not yet a final W3C Recommendation. |
| AU Data Policy Framework | Official African Union framework (2022) | Used for continental data-governance context, not as directly enforceable national law. |
| AU Digital Education Strategy 2023-2028 | Official AU strategy published in 2022 | Used to motivate digital-education priorities. |
| AfCFTA Digital Trade Protocol | Adopted 18 February 2024 | Used as a continental digital-trade instrument; national effect and implementation require separate review. |
| AU data-provisions guidelines | Official document published 22 May 2025 | Used as non-binding governance guidance unless incorporated through competent processes. |

## 2. Dated or dynamic contextual indicators

- ITU 2025 Internet-use estimates are retained with the year and denominator in the table and source CSV.
- The UN Trade and Development cyberlaw indicator is a dynamic tracker. The manuscript records the accessed value and does not treat legislative adoption as equivalent enforcement or harmonization.
- Malabo Convention participation values (21 signatures and 16 ratifications/accessions out of 55 AU member states) are tied to the **status list dated 8 July 2024**. They are used only as a historical contextual snapshot and must be refreshed before submission if a later authoritative status list is available.
- Contextual indicators use different concepts and denominators and are not combined into a composite ranking.

## 3. National/legal examples

Morocco Law 09-08 and the CNDP transfer page, Kenya's Data Protection Act and 2021 General Regulations, South Africa's POPIA, and the EU GDPR are cited as examples of recurring transfer, minimization, and privacy-by-design concerns. The architecture does not decide legal validity. Every real jurisdiction profile requires current review by competent institutional and legal personnel.

## 4. Peer-reviewed literature

The bibliography retains only the 45 works actually cited in the manuscript. Duplicate merged entries and uncited items were removed. Recent works on learning-analytics maturity, micro-credentials, blockchain academic credentials, higher-education identity, and zero-trust decentralized identity were checked against publisher/DOI records. Acronyms and standards statuses were protected from BibTeX down-casing where needed.

## 5. Experimental evidence classification

| Evidence class | Files | What it supports | What it does not support |
|---|---|---|---|
| Analytical control rubric | `data/threat_control_scores.csv` | Traceability of explicit controls against 36 declared objectives | Breach probability, exploitability, implementation quality, or legal compliance |
| Synthetic policy simulation | `experiments/simulate_policy.py`, `data/seed_metrics.csv`, `data/results_summary.csv` | Relative policy expressiveness under a declared generator | Real institutional error rates or country performance |
| Staleness sensitivity | `data/policy_staleness.csv` | Consequence of incorrect registry entries in an isolated test | Observed regulator or institution error frequency |
| Differential-privacy utility | `data/dp_utility.csv` | Illustrative count-query privacy/utility trade-off | A complete production privacy-loss analysis |
| Single-host microbenchmark | `results/benchmark_raw.csv`, `results/benchmark_summary.csv` | Local computational cost of selected operations | End-to-end latency, throughput, mobile performance, HSM cost, or distributed-system capacity |
| Official context | `data/connectivity_2025.csv`, `data/governance_context.csv` | Motivation and design constraints | Evaluation of AFRICA-ZT-EDU effectiveness |

## 6. Reproducibility audit

- Default simulation: 30 seeds x 100,000 requests = 3,000,000 requests.
- The four generated simulation CSV files were reproduced byte-for-byte in an independent rerun with the recorded environment.
- The supplied benchmark raw CSV was independently re-aggregated; stored p50, p95, mean, standard deviation, and throughput values matched the raw samples.
- PDF compilation completed with 45 cited references, 13 fully bordered tables, and 15 pages.
- PDF inspection found embedded fonts and no Type 3 fonts, unresolved references, clipping, overlaps, or broken glyphs.
