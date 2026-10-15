# Training data and reproduction (scene-aware exposure)

**Photos.** ~1800 JPEGs from Wikimedia Commons categories (night, dusk/sunset, portrait, landscape, street, close-up/indoor, backlit),
only files with CC0, public domain or CC BY licenses (no ShareAlike/NonCommercial/NoDerivatives). The list with authors, licenses and
links is [training_attribution.csv](training_attribution.csv). Images are downloaded at 960 px by `scripts/train/fetch_commons.py`
(polite User-Agent, pauses) into `data/train/` and are **not** part of the repository or of any release.

**Labels.** None are annotated by hand. Every photo is assumed to be a correctly exposed example; the trainer shifts it by a random
number of stops in linear light (with clipping, like a real camera) and the target is the opposite shift. About 40% of the shifts are
near zero so the model learns to leave good frames alone. The scene class comes from the Commons category (noisy by nature).

**Features and model.** DINOv2-small CLS embedding (reduced to 8 principal components) + 22 luminance/colour statistics → MLP 128-64 →
exposure correction (Huber loss) and scene type (7 classes). The PCA and normalisation are folded into the first layer of the exported
ONNX, so the model takes the raw 406-number feature vector.

**Honest limits.** A held-out 20% of photos (split by file name hash) measures consistency with typical photographs, not taste.
Commons skews towards well-exposed, post-processed pictures; dark-by-intent night photos are in the set but the scene label is noisy.
The correction is applied as ordinary sliders, so a wrong guess is easy to undo.

**Reproduce:**
```bash
python scripts/train/fetch_commons.py          # downloads photos + attribution.csv (~25 min)
python scripts/train/build_features.py         # DINOv2 features for synthetic shifts (~20 min, 4 threads)
python scripts/train/train_head.py --export models/exposure_scene.onnx
python scripts/train/benchmark_auto.py         # histogram vs IAT vs the new model on held-out photos
```
(`dinov2_small.onnx` must lie in `models/`; export script: facebook/dinov2-small → pooler_output, opset 17.)
