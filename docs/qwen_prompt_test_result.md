# Qwen Multimodal Prompt Test Result

This file stores a verified direct multimodal test result from the local project environment.

## Test Setup

- backend: qwen_vl
- model: Qwen/Qwen2.5-VL-3B-Instruct
- image: [dataset/2011_09_26_drive_0009_sync/2011_09_26/2011_09_26_drive_0009_sync/image_02/data/0000000000.png](../dataset/2011_09_26_drive_0009_sync/2011_09_26/2011_09_26_drive_0009_sync/image_02/data/0000000000.png)

## Result Returned by Qwen

- Scene caption: 1) The scene shows a street with parked cars on both sides, trees lining the sidewalk, and a building in the background
- Explanation: Generated localization/safety reasoning from the provided prompt and metrics
- Hazards: ['safety constraint violation', 'weak visual observability']

## Notes

- This result confirms that image + prompt multimodal inference is working in the local environment.
- Full multi-sequence pipeline runs with Qwen can be slower on CPU-only torch builds.
