# RenkuLab Setup — AFRICA-ZT-EDU

## Recommended Renku project metadata

**Name:** `africa-zt-edu-reproducible-research`

**Visibility during setup:** Private  
Switch to **Public** only after the full reproduction run and metadata check.

**Description:**

> Reproducible computational artifact for AFRICA-ZT-EDU, a policy-centric Zero-Trust and privacy-preserving reference architecture for cross-border digital education in Africa. The project contains synthetic policy experiments, differential-privacy and policy-staleness analyses, cryptographic/policy benchmarks, source data, figures, and reproducibility metadata. No real learner records are used.

## Recommended Renku session launcher

- Type: Session Launcher
- Environment: Create from Code (preferred) or Python Data Science - Jupyter
- Code-based environment file: `requirements.txt` or `environment.yml`
- User interface: JupyterLab / VSCodium
- Resources: start with the largest free CPU/RAM class available to your account for the full 3M-request run
- Disk: at least 5 GB recommended

## First validation

```bash
python -m pip install -r requirements.txt
python run_all.py --quick
```

## Full reproduction

```bash
python run_all.py --full
```

Expected high-level published-scale checks are documented in `REPRODUCIBILITY.md`.
