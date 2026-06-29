# Dataset card: CSE-CIC-IDS2018 Wednesday 2018-02-28 processed flows

Date acquired: 2026-06-12

## Source

Official pages:

- `https://registry.opendata.aws/cse-cic-ids2018/`
- `https://www.unb.ca/cic/datasets/ids-2018.html`

Official public object:

```text
https://cse-cic-ids2018.s3.ca-central-1.amazonaws.com/Processed%20Traffic%20Data%20for%20ML%20Algorithms/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv
```

Local path:

```text
data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv
```

Verified source facts:

```text
HTTP status: 200 OK
Content-Length: 209249758 bytes
Last-Modified: Thu, 11 Oct 2018 16:10:33 GMT
SHA-256: F15E2A12304446058A0186C8AD67DE2BD15735A9BA5C70C9A1F4C4242AB06771
```

## Preregistration

The day, hierarchy, split, metrics, controls, bootstrap procedure, and pass/fail statuses were frozen before download and label inspection in:

```text
docs/rebuild/28_CSE_CIC_SECOND_DAY_PREREGISTRATION.md
```

## Local schema and labels

Rows after repeated-header removal:

```text
613071
```

Valid timestamps:

```text
613071
```

Observed timestamp range:

```text
2018-02-28 01:00:00 through 2018-02-28 12:59:59
```

Labels:

```text
Benign: 544200
Infilteration: 68871
```

The source label spelling `Infilteration` is preserved as observed. The pipeline maps all labels other than `Benign` to `is_attack = 1` only for reference filtering and final evaluation.

## Frozen hierarchy

```text
Protocol -> dst_port_band -> Dst Port -> SYN Flag Cnt -> ACK Flag Cnt -> PSH Flag Cnt
```

No attack label or attack-family-derived field is included in the hierarchy.

## Eligibility and caveats

- Official/reputed CSE-CIC benchmark data.
- Fresh external day selected before result inspection.
- Same benchmark and attack family as the previously evaluated Thursday file, so this is cross-day validation rather than fully independent cross-domain validation.
- Controlled cyber-range traffic must not be described as natural bank fraud.
- A pass could support a narrow fresh-day result; a failure remains valid diagnostic evidence.

## Final gate status

```text
diagnostic_only_failed_q1_tree_scan_gate
```

The parent-conditional p-adic scan did not beat category entropy with a positive confidence interval.
