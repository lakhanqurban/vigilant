# Sensor Fusion (EKF)

`vision_language_localization/sensor_fusion/ekf_fusion.py` implements the
Phase-2 sensor fusion from the original project idea: fuse camera pose, GPS, and
IMU-derived information so that localization is more robust than any single
source.

## Design

The default `EkfFusion` runs an Extended Kalman Filter over the state
`[px, py, pz, vx, vy, vz]` with a constant-velocity motion model. Every frame,
three measurements are applied sequentially:

1. **GPS position** — OXTS lat/lon/alt converted to the local ENU frame
   (`kitti_loader.latlon_to_local_xy`).
2. **SLAM position** — the visual estimate, with adaptive measurement noise that
   grows as tracking quality degrades (and very large when tracking is lost).
3. **IMU-derived velocity** — `[speed*cos(yaw), speed*sin(yaw), 0]` from OXTS,
   a weak pseudo-measurement (default noise `3.0 m/s`).

### Frame registration

External SLAM exports (e.g. ORB-SLAM3 KITTI-format trajectories) are written in
an arbitrary visual frame that is rigidly offset from the GPS frame — often by
hundreds of meters. Before filtering, `EkfFusion` estimates a similarity
(Umeyama) transform from the first `registration_window` frames with
`tracking_quality >= 0.5` and maps the whole SLAM trajectory into the GPS frame
(`sensor_fusion/alignment.py`). This makes the two sources consistent so the
filter can genuinely fuse them. Registration is causal: it uses only the start
of the sequence.

### Measurement gating

An optional Mahalanobis innovation gate (`gate_chi2 > 0`) rejects outlier
measurements. It is **disabled by default** because on short, low-noise windows
it can lock the filter onto a stale state and reject subsequent valid
measurements.

## Parameters

Set via `PipelineConfig` or the CLI where exposed:

| Config field | CLI | Default | Meaning |
|---|---|---|---|
| `fusion_method` | `--fusion-method` | `ekf` | `ekf` or `blend` (legacy weighted baseline) |
| `fusion_gps_noise_m` | - | `1.5` | GPS position noise (m) |
| `fusion_slam_noise_m` | - | `1.0` | SLAM position noise (m) at full tracking quality |
| `fusion_dead_reckoning_noise_mps` | - | `3.0` | IMU velocity pseudo-measurement noise (m/s) |
| `fusion_process_noise_accel_mps2` | - | `2.0` | Process acceleration noise density |
| `fusion_align_slam_to_gps` | - | `True` | Register SLAM to GPS frame before filtering |
| `fusion_registration_window` | - | `50` | Frames used for registration |
| `fusion_gate_chi2` | - | `0.0` | Innovation gate threshold (0 disables) |

## Results on the real ORB-SLAM3 trajectories

| Sequence | SLAM ATE (m) | Fusion ATE (m) | SLAM Drift (m) | Fusion Drift (m) |
|---|---|---:|---:|---:|---:|
| 2011_09_26_drive_0009_sync | 303.074 | 4.586 | 445.672 | 1.718 |
| 2011_09_26_drive_0015_sync | 293.076 | 2.250 | 529.582 | 3.533 |
| 2011_09_26_drive_0023_sync | 225.065 | 4.895 | 394.961 | 0.613 |
| 2011_09_26_drive_0036_sync | 353.131 | 4.909 | 650.552 | 1.255 |
| 2011_09_26_drive_0093_sync | 255.319 | 12.731 | 381.687 | 6.488 |

Caveats:

- The ground-truth reference is itself derived from the same OXTS GPS data used
  as a fusion input, so the fusion result is partly self-consistent with the
  reference. This is inherent to KITTI, whose reference poses are GPS/IMU-based.
- Rigidly aligned, the raw ORB trajectories already achieve sub-meter ATE; the
  raw numbers in the README intentionally report the *unaligned* exports, and
  the EKF resolves that offset via registration.
