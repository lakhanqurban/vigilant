# VLM Evaluation

This document describes how to evaluate VLM explanations in a publication-grade way,
following the protocol outlined in the original project idea.

## What is measured

The evaluation is split into two parts:

### 1. Annotation-based metrics (per sequence, vs expert labels)

Requires an annotation file with expert labels per sequence. Computed by
`vision_language_localization/evaluation/vlm_evaluation.py`:

- **Claim accuracy** — does the explanation mention the root causes an expert identified?
  Reported as claim precision, recall, and F1.
- **Hazard identification** — precision, recall, and F1 of the model's hazard set
  against the expert hazard set.
- **Hallucination rate** — fraction of model-reported hazards that are not supported
  by the expert labels.

Model explanations are mapped to a canonical taxonomy before scoring:

```python
# Claim categories (CLAIM_TAXONOMY)
low_feature_support | geometric_inconsistency | trajectory_drift |
safety_violation | environmental_obstruction | motion_blur

# Hazard categories (HAZARD_TAXONOMY)
localization_degradation | safety_violation | visual_ambiguity |
dynamic_obstacle | model_reported_risk | none
```

### 2. Reliability metrics (recorded by the pipeline)

- **Consistency** — repeated runs of the VLM on the same scene/prompt. Reported as
  the mean pairwise Jaccard similarity of the explanation vocabulary and of the
  detected claim sets. Enabled with `--vlm-consistency-runs N` (use `N=5` and a
  non-zero temperature for generative backends so samples actually vary).
- **Latency** — mean/std wall-clock time per explanation call.

### 3. RQ3 correlation (VLM signals vs safety metrics)

Implemented in `vision_language_localization/evaluation/correlation.py`.
Computes pairwise Pearson/Spearman correlations (with permutation p-values) between:

- VLM signals: `hazard_count`, `hallucination_risk`, `consistency_score`, `evidence_alignment`
- Safety metrics: `ate_rmse`, `rpe_mean`, `drift_final_m`, `violation_count`, `stl_robustness`

> Note: with a handful of sequences the permutation p-value has low statistical power.
> Treat these correlations as descriptive and scale up to more sequences before drawing conclusions.

## Annotation file format

Copy `annotations/example_annotations.json` and replace the labels with genuine
expert annotations:

```json
{
  "sequences": [
    {
      "sequence_id": "2011_09_26_drive_0009_sync",
      "expected_claims": ["trajectory_drift", "safety_violation"],
      "expected_hazards": ["localization_degradation", "safety_violation"]
    }
  ]
}
```

`expected_claims` and `expected_hazards` must use labels from the taxonomies above.
The included `example_annotations.json` is an **illustrative placeholder derived from
the numeric metrics** — it is NOT a substitute for expert annotation.

## Running the evaluation

1. Run the pipeline (with consistency enabled and the real VLM backend):

```bash
python scripts/run_pipeline.py \
  --slam-backend trajectory_file \
  --trajectory-root slam \
  --strict-trajectory-matching \
  --vlm-backend qwen_vl \
  --vlm-model-name Qwen/Qwen2.5-VL-3B-Instruct \
  --vlm-consistency-runs 5 \
  --vlm-temperature 0.7
```

2. Evaluate against expert annotations:

```bash
python scripts/evaluate_vlm.py \
  --report outputs/latest_run.json \
  --annotations annotations/my_expert_annotations.json \
  --output-root outputs
```

The result is written to `outputs/evaluation_report.json` and rendered by the dashboard.

## Reporting

For a paper, report per-sequence and aggregate (mean/std) values of:

- claim precision / recall / F1
- hazard precision / recall / F1
- hallucination rate
- consistency and latency (when applicable)
- correlation table with p-values (RQ3)
