# External SLAM Trajectory Ingestion

You can now run the pipeline with external SLAM trajectories instead of the mock SLAM simulator.

## Expected file naming

Place files in the `slam/` folder with this pattern:

- `<sequence_id>.kitti.txt`

Example:
- `slam/2011_09_26_drive_0009_sync.kitti.txt`

## Supported formats

1. KITTI pose rows (12 columns):
   - `r00 r01 r02 tx r10 r11 r12 ty r20 r21 r22 tz`
2. XYZ rows (3+ columns):
   - `x y z ...`

For 3+ columns, the first 3 values are interpreted as position.

## Run command

python scripts/run_pipeline.py --dataset-root dataset --output-root outputs --slam-backend trajectory_file --trajectory-root slam --trajectory-file-suffix .kitti.txt

Use strict checking to fail on missing sequence files:

python scripts/run_pipeline.py --dataset-root dataset --output-root outputs --slam-backend trajectory_file --trajectory-root slam --strict-trajectory-matching

## Scene Description with VLM

To use actual vision-conditioned scene description, run with the local HF backend:

python scripts/run_pipeline.py --dataset-root dataset --output-root outputs --vlm-backend hf_local --vlm-model-name Salesforce/blip-image-captioning-base

The report will include:
- `scene_image_path`
- `vlm.scene_caption`
- `vlm.explanation`

For full Qwen multimodal reasoning:

python scripts/run_pipeline.py --dataset-root dataset --output-root outputs --vlm-backend qwen_vl --vlm-model-name Qwen/Qwen2.5-VL-3B-Instruct
