from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="VLM Localization Safety Dashboard", layout="wide")
st.title("Vision-Language Assisted Localization and Safety")

report_path = Path("outputs/latest_run.json")
if not report_path.exists():
    st.warning("No report found at outputs/latest_run.json. Run scripts/run_pipeline.py first.")
    st.stop()

records = json.loads(report_path.read_text(encoding="utf-8"))
if not records:
    st.warning("Report is empty.")
    st.stop()

rows = []
for r in records:
    rows.append(
        {
            "sequence_id": r["sequence_id"],
            "frames": r["num_frames"],
            "scene_image_path": r.get("scene_image_path"),
            "slam_ate": r["slam_metrics"]["ate_rmse"],
            "fusion_ate": r["fusion_metrics"]["ate_rmse"],
            "slam_rpe": r["slam_metrics"]["rpe_mean"],
            "rv_robustness": r["runtime_verification"]["stl_robustness"],
            "violations": r["runtime_verification"]["violation_count"],
            "vlm_consistency": r["vlm"]["consistency_score"],
            "vlm_hallucination_risk": r["vlm"]["hallucination_risk"],
            "evidence_alignment": r["explanation_evidence"]["evidence_alignment_score"],
            "unsupported_claims": r["explanation_evidence"]["unsupported_claim_count"],
            "scene_caption": r["vlm"].get("scene_caption"),
            "explanation": r["vlm"]["explanation"],
        }
    )

frame = pd.DataFrame(rows)
st.dataframe(frame, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("SLAM vs Fusion ATE")
    fig = px.bar(frame, x="sequence_id", y=["slam_ate", "fusion_ate"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("STL Robustness")
    fig = px.line(frame, x="sequence_id", y="rv_robustness", markers=True)
    st.plotly_chart(fig, use_container_width=True)

selected = st.selectbox("Inspect sequence", frame["sequence_id"].tolist())
entry = next(x for x in records if x["sequence_id"] == selected)

st.subheader("VLM Explanation")
st.write(entry["vlm"]["explanation"])
if entry["vlm"].get("scene_caption"):
    st.write("Scene caption:", entry["vlm"]["scene_caption"])
if entry.get("scene_image_path"):
    st.write("Analyzed frame:", entry["scene_image_path"])
st.write("Hazards:", ", ".join(entry["vlm"]["hazards"]))
st.write("Evidence alignment score:", entry["explanation_evidence"]["evidence_alignment_score"])
if entry["explanation_evidence"]["flagged_claims"]:
    st.write("Flagged unsupported claim categories:", ", ".join(entry["explanation_evidence"]["flagged_claims"]))

st.subheader("Runtime Verification Properties")
st.json(entry["runtime_verification"]["property_summary"])

eval_path = Path("outputs/evaluation_report.json")
if eval_path.exists():
    evaluation = json.loads(eval_path.read_text(encoding="utf-8"))

    st.divider()
    st.title("VLM Evaluation")
    st.caption(f"Source: {evaluation.get('report_source')} | Annotations: {evaluation.get('annotations_source')}")

    summary = evaluation.get("summary", {})
    if summary.get("consistency", {}).get("mean_text_similarity") is not None:
        st.write(
            "Mean pairwise consistency (text similarity):",
            summary["consistency"]["mean_text_similarity"],
            "| Mean latency (s):",
            summary.get("latency", {}).get("mean_s"),
        )

    expl_rows = []
    for r in evaluation.get("per_sequence", []):
        m = r.get("explanation_metrics")
        if not m:
            continue
        expl_rows.append(
            {
                "sequence_id": r["sequence_id"],
                "claim_precision": m["claim_precision"],
                "claim_recall": m["claim_recall"],
                "claim_f1": m["claim_f1"],
                "hazard_precision": m["hazard_precision"],
                "hazard_recall": m["hazard_recall"],
                "hazard_f1": m["hazard_f1"],
                "hallucination_rate": m["hallucination_rate"],
            }
        )
    if expl_rows:
        st.subheader("Explanation & Hazard Metrics (vs expert annotations)")
        st.dataframe(pd.DataFrame(expl_rows), use_container_width=True)
        fig = px.bar(
            pd.DataFrame(expl_rows),
            x="sequence_id",
            y=["claim_f1", "hazard_f1", "hallucination_rate"],
            barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)

    correlation = evaluation.get("correlation_rq3", [])
    if correlation:
        st.subheader("RQ3: VLM Signals vs Safety Metrics Correlation")
        corr_rows = [
            {
                "vlm_signal": c["vlm_signal"],
                "safety_metric": c["safety_metric"],
                "pearson_r": c.get("pearson_r"),
                "pearson_p": c.get("pearson_p"),
                "spearman_r": c.get("spearman_r"),
                "spearman_p": c.get("spearman_p"),
            }
            for c in correlation
        ]
        corr_frame = pd.DataFrame(corr_rows)
        st.dataframe(corr_frame, use_container_width=True)

        pivot = corr_frame.pivot(index="vlm_signal", columns="safety_metric", values="pearson_r")
        if not pivot.empty:
            st.plotly_chart(
                px.imshow(
                    pivot,
                    text_auto=".2f",
                    color_continuous_scale="RdBu",
                    zmin=-1,
                    zmax=1,
                    aspect="auto",
                ),
                use_container_width=True,
            )
