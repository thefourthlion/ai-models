# Bird or Forest Image Classifier

A deep learning model that classifies images as either birds or forest/landscape scenes using FastAI and ResNet34.

## Overview

This project implements a binary image classifier that can determine whether a given image contains a bird or a forest/landscape scene. It uses transfer learning with a pre-trained ResNet34 model and is built using the FastAI library.

## Project Structure

- `bird_classifier.py` - Main script for training the model
- `predict.py` - Script for making predictions on new images
- `images/` - Directory containing training images
  - `birds/` - Bird images for training
  - `forest/` - Forest/landscape images for training
- `bird_classifier.pkl` - The trained model file

## Features

- Image scraping from DuckDuckGo for dataset creation
- Data augmentation for better model generalization
- Transfer learning using ResNet34 architecture
- Binary classification (birds vs forest scenes)
- Simple prediction interface

## Usage

### Training the Model

To train a new model:

1. Install dependencies:

   ```bash
   pip install fastai pandas duckduckgo-search-python
   ```

2. Run the training script:
   ```bash
   python bird_classifier.py
   ```

### Making Predictions

To make predictions on new images:

1. Install dependencies:

   ```bash
   pip install fastai pandas duckduckgo-search-python
   ```

2. Run the prediction script:
   ```bash
   python predict.py
   ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [FastAI](https://fastai.io/) - Deep learning library
- [DuckDuckGo](https://duckduckgo.com/) - Image search engine
- [ResNet34](https://arxiv.org/abs/1512.03385) - Transfer learning model architecture  

