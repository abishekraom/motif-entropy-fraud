# Dataset card: CSE-CIC-IDS2018 Thursday-01-03 processed flow subset

Date: 2026-06-09

## Source

Official/reputed source pages checked:

- `https://www.unb.ca/cic/datasets/ids-2018.html`
- `https://registry.opendata.aws/cse-cic-ids2018`
- S3 bucket: `s3://cse-cic-ids2018/`

Downloaded file:

- S3 key: `Processed Traffic Data for ML Algorithms/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv`
- Local path: `data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv`
- Size observed after download: 107,842,858 bytes

## Provenance facts from source pages

The Registry of Open Data on AWS describes CSE-CIC-IDS2018 as a collaborative project between the Communications Security Establishment and the Canadian Institute for Cybersecurity using profiles to generate cybersecurity data systematically. It includes seven attack scenarios: Brute-force, Heartbleed, Botnet, DoS, DDoS, Web attacks, and infiltration. The dataset includes network traffic and log files plus 80 CICFlowMeter-V3 flow features.

The UNB/CIC page states redistribution/republishing/mirroring is allowed with citation and a link to the AWS page.

## Local schema audit

Rows loaded from downloaded Thursday file:

- 331,125 rows before removing repeated header rows.
- Label counts observed:
  - Benign: 238,037
  - Infilteration: 93,063
  - repeated header rows labeled `Label`: 25

Fields used for first diagnostic external event-stream audit:

- Time field: `Timestamp`
- Label field: `Label`
- Positive label rule: `Label != Benign`
- Hierarchy candidate:
  1. `Protocol`
  2. `dst_port_band`
  3. `Dst Port`
  4. `SYN Flag Cnt`
  5. `ACK Flag Cnt`
  6. `PSH Flag Cnt`

`dst_port_band` is a deterministic standard port-class feature:

- system: 0-1023
- registered: 1024-49151
- dynamic: 49152-65535
- nonnumeric/other: missing_or_nonstandard

## Claim eligibility

Eligible as an official/reputed external cybersecurity surveillance dataset for diagnostic generalization.

Caveats:

- This is one processed day/file, not the full CSE-CIC-IDS2018 benchmark.
- It should not by itself establish Q1/SPL cross-dataset success.
- If this route looks promising, the full benchmark or a pre-specified multi-day subset must be audited before manuscript claims.
- The labels and traffic are generated in a controlled benchmark environment; wording must say cybersecurity benchmark/event-stream surveillance, not natural bank fraud.

## Required claim status behavior

If the p-adic operator fails against flat/reversed/random hierarchy controls, record `diagnostic_only_failed_q1_multiresolution_gate` and stop empirical overclaiming.
