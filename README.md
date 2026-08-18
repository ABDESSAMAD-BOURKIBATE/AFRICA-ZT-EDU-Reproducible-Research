# AFRICA-ZT-EDU Reproducible Research Artifact

**AFRICA-ZT-EDU: A Policy-Centric Zero-Trust and Privacy-Preserving Architecture for Cross-Border Digital Education in Africa**

Author: **Abdessamad Bourkibate**  
ORCID: **0009-0000-6186-8071**

Affiliations:
- Department of Computer Science, University of the People, Pasadena, CA, USA.
- Faculty of Legal, Economic and Social Sciences, Cadi Ayyad University, Marrakech, Morocco.
- Share In, Casablanca, Morocco.

## Purpose

This repository is the reproducible computational companion to the AFRICA-ZT-EDU research article. It contains the synthetic policy experiment, differential-privacy utility experiment, policy-registry staleness analysis, single-host cryptographic/policy microbenchmark, source data, row-level analytical scores, and scripts used to regenerate the research figures.

All learner, institution, jurisdiction, credential, and cohort payloads used by the experiments are **synthetic**. The artifact is not a production deployment, legal opinion, compliance certification, or country-level assessment.

## One-click reproduction in RenkuLab

Open `REPRODUCE_PAPER.ipynb` in a RenkuLab Python/Jupyter session and run the cells in order.

For the command line:

```bash
python -m pip install -r requirements.txt
python run_all.py --full
```

For a fast validation run before launching the complete 3,000,000-request experiment:

```bash
python run_all.py --quick
```

## Reproduced components

- 30-seed policy simulation: 3,000,000 synthetic authorization requests
- differential-privacy count utility study
- jurisdiction-policy staleness sensitivity analysis
- 36-objective analytical threat/control dataset
- local Ed25519/AES-GCM/policy microbenchmark
- scientific figures derived from the supplied CSV outputs

See `REPRODUCIBILITY.md` for the exact methodology and expected headline values.
