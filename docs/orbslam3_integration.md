# ORB-SLAM3 Integration Guide

This project can consume real ORB-SLAM3 trajectories in `.kitti.txt` format.

## 1. Prepare one raw KITTI sequence for ORB-SLAM3

From the repository root:

```bash
python scripts/prepare_orbslam3_kitti.py --sequence-id 2011_09_26_drive_0009_sync --max-frames 100
```

This creates:

- `slam/prepared/2011_09_26_drive_0009_sync/image_0/`
- `slam/prepared/2011_09_26_drive_0009_sync/image_1/`
- `slam/prepared/2011_09_26_drive_0009_sync/times.txt`
- `slam/prepared/2011_09_26_drive_0009_sync/settings.yaml`

## 2. Build ORB-SLAM3 in WSL

```bash
wsl -d Ubuntu-22.04 -- bash -lc 'cd /mnt/c/Users/Qurban/Documents/GitHub/VLM && bash scripts/wsl_build_orbslam3.sh'
```

Note:
This build uses vendored `slam/Pangolin` and `slam/ORB_SLAM3`. If extra Linux packages are missing, you may still need to install them in WSL.

## 3. Run ORB-SLAM3 and export trajectory

```bash
wsl -d Ubuntu-22.04 -- bash -lc 'cd /mnt/c/Users/Qurban/Documents/GitHub/VLM && bash scripts/wsl_run_orbslam3_kitti.sh 2011_09_26_drive_0009_sync'
```

Expected output:

- `slam/2011_09_26_drive_0009_sync.kitti.txt`

## 4. Use exported trajectory in the Python pipeline

```bash
python scripts/run_pipeline.py --dataset-root dataset --output-root outputs --slam-backend trajectory_file --trajectory-root slam --strict-trajectory-matching --vlm-backend qwen_vl --vlm-model-name Qwen/Qwen2.5-VL-3B-Instruct --max-sequences 1 --max-frames 100
```

## Current limitations

- ORB-SLAM3 stereo example expects KITTI-style `image_0`, `image_1`, and `times.txt`.
- This repo prepares those from the raw synced dataset using `image_00` and `image_01` by default.
- If grayscale pair results are poor, try adapting the prep script to use `image_02` and `image_03` with an adjusted YAML.
