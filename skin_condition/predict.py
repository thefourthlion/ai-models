from fastai.vision.all import *
import argparse, pathlib

def main():
    parser = argparse.ArgumentParser(
        description='Skin‑condition image classifier'
    )
    parser.add_argument(
        'image',
        type=pathlib.Path,
        help='Path to the image you want to classify'
    )
    parser.add_argument(
        '--model',
        default='skin_condition_classifier.pkl',
        help='Path to the exported learner (*.pkl) file'
    )
    args = parser.parse_args()

    learn = load_learner(args.model)
    img   = PILImage.create(args.image)

    pred, _, probs = learn.predict(img)
    print(f'\nPrediction →  {pred}\n')
    for cls, p in zip(learn.dls.vocab, probs):
        print(f'{cls:>25}: {p:.4f}')

if __name__ == '__main__':
    main() 