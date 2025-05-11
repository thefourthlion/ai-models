"""
Train a multi‑class skin‑condition classifier and export it as
`skin_condition_classifier.pkl`.
The script assumes the following layout

    skin_condition/
    └─ images/
       ├─ train/
       │   ├─ Acne/
       │   ├─ Actinic_Keratosis/
       │   └─ ...
       └─ (optionally valid/  or test/)

If there is no explicit *valid* folder the script performs a random
20% split.
"""
from fastai.vision.all import *
from pathlib import Path
import multiprocessing
import torch

def main():
    # ------------------------------------------------------------------
    # 1. locate dataset and collect class names
    # ------------------------------------------------------------------
    path = Path('images/train')      # <- adjust only if you move folders
    classes = sorted([p.name for p in path.ls() if p.is_dir()])
    
    counts = {c: len((path/c).ls()) for c in classes}
    print('📷  images per class →', counts)

    # basic sanity‑check
    empty = [c for c, n in counts.items() if n == 0]
    if empty:
        raise ValueError(f'No images found for {empty}')

    # ------------------------------------------------------------------
    # 2. build a DataLoaders object
    # ------------------------------------------------------------------
    dblock = DataBlock(
        blocks     = (ImageBlock, CategoryBlock),
        get_items  = get_image_files,
        splitter   = RandomSplitter(valid_pct=0.2, seed=42),
        get_y      = parent_label,
        item_tfms  = Resize(460),
        batch_tfms = [*aug_transforms(size=224, min_scale=0.75),
                      Normalize.from_stats(*imagenet_stats)]
    )

    dls = dblock.dataloaders(path, bs=32)   # bump bs up/down if you OOM

    # ------------------------------------------------------------------
    # 3. create learner & train
    # ------------------------------------------------------------------
    learn = vision_learner(dls, resnet34, metrics=accuracy)
    device = next(learn.model.parameters()).device
    print(f'Training on → {device}')      # e.g. "cuda:0"  or "cpu"
    learn.fine_tune(15, base_lr=3e-3)

    # ------------------------------------------------------------------
    # 4. export for inference
    # ------------------------------------------------------------------
    learn.export('skin_condition_classifier.pkl')
    print('✅  exported to  skin_condition_classifier.pkl')

    print(torch.cuda.is_available())   # → True  (means CUDA was found)
    print(torch.cuda.get_device_name())# → "NVIDIA GeForce RTX 3060" (example)

    learn = load_learner(args.model, cpu=False)   # gpu if possible
    # or
    learn = load_learner(args.model, cpu=True)    # always cpu

# ----------------------------------------------------------------------
# windows‑multiprocessing guard
# ----------------------------------------------------------------------
if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
