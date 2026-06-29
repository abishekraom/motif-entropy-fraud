# Data Availability and Licensing Statement

## Manuscript-ready data availability statement

The software and curated derived audit artifacts are prepared for public release with the repository. Raw third-party datasets are not redistributed in this repository. IEEE-CIS Fraud Detection data must be obtained from the official Kaggle competition page by users who accept Kaggle's terms. CSE-CIC-IDS2018 data must be obtained from the Canadian Institute for Cybersecurity / AWS Open Data source. The repository documents expected local file placement in `data/README.md` and keeps curated derived tables, figures, and claim-status artifacts in `results/` for auditability. If SoftwareX requires a deposited data record, the public release should deposit only the redistributable derived artifacts and provide official raw-data acquisition links plus checksums/filenames where allowed.

## Raw data sources

| Dataset | Use | Redistribution status | Local placement |
|---|---|---|---|
| IEEE-CIS Fraud Detection | Fraud transaction audit and strong baselines | Do not commit raw CSVs; download from Kaggle official competition | `D:/motif-entropy-fraud/ieee-fraud-detection/` or `data/ieee_cis_mirror/` locally |
| CSE-CIC-IDS2018 Thursday/Wednesday | External cybersecurity event-stream tree-scan gates | Do not commit raw CSVs unless license/source permits; use official CIC/AWS sources | `data/cse_cic_ids2018/` |
| Curated derived artifacts | Paper evidence and reproducibility audit | Included/prepared in `results/` | `results/` |

## License statement

The local SoftwareX-prep version adds `LICENSE.txt` with the MIT License. The author must confirm this license before any public release or journal submission.
