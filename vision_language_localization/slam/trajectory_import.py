from __future__ import annotations

from pathlib import Path

import numpy as np

from vision_language_localization.slam.mock_slam import SlamOutput


def _load_estimated_xyz(path: Path) -> np.ndarray:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows: list[list[float]] = []
    for line in lines:
        parts = [float(x) for x in line.split()]
        rows.append(parts)

    arr = np.array(rows, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError(f"Invalid trajectory matrix shape in {path}")

    if arr.shape[1] == 12:
        # KITTI pose row: r00 r01 r02 tx r10 r11 r12 ty r20 r21 r22 tz
        xyz = arr[:, [3, 7, 11]]
    elif arr.shape[1] >= 3:
        xyz = arr[:, :3]
    else:
        raise ValueError(f"Unsupported trajectory format with {arr.shape[1]} columns in {path}")

    return xyz


def load_external_slam_output(
    trajectory_file: Path,
    gt_xyz: np.ndarray,
) -> SlamOutput:
    est_xyz = _load_estimated_xyz(trajectory_file)

    n = min(len(est_xyz), len(gt_xyz))
    if n < 2:
        raise ValueError("Trajectory must contain at least 2 frames")

    est = est_xyz[:n]
    gt = gt_xyz[:n]

    err = np.linalg.norm(est - gt, axis=1)

    # Proxy quality features when external logs are not available.
    tracking_quality = np.clip(1.0 - err / (np.percentile(err, 90) + 1e-6), 0.0, 1.0)
    tracking_ok = tracking_quality > 0.25
    reprojection_error = 0.6 + 2.8 * (1.0 - tracking_quality)
    feature_count = (1400 * tracking_quality + 120).astype(np.int32)

    return SlamOutput(
        est_xyz=est,
        tracking_ok=tracking_ok,
        tracking_quality=tracking_quality,
        reprojection_error=reprojection_error,
        feature_count=feature_count,
    )
