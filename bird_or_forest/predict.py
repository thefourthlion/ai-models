from fastai.vision.all import *

# Load the model
learn = load_learner('bird_classifier2.0.pkl')

# Path to your test image
test_image = './bird.jpg'
img = PILImage.create(test_image)

# Make prediction
pred, pred_idx, probs = learn.predict(img)
print(f"Prediction: {pred}")

# Display the probability for the predicted class
bird_idx = 0 if pred == 'birds' else 1
bird_prob = probs[bird_idx].item()
print(f"Confidence it's a {pred}: {bird_prob:.6f}") 