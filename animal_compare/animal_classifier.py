# Import required libraries
from fastai.vision.all import *
import os
import requests
import time
from pathlib import Path
import multiprocessing  # Add this import

# Function to search for images on DuckDuckGo


def search_images_ddg(term, max_images=500, retry_delay=5):
    """Search for images with retry mechanism and better error handling"""
    url = 'https://duckduckgo.com/'
    params = {'q': term}

    # Add retry logic
    for attempt in range(3):  # Try 3 times
        try:
            res = requests.post(url, data=params)
            search_obj = re.search(r'vqd=([\d-]+)\&', res.text)

            if not search_obj:
                print(
                    f"Token not found on attempt {attempt+1}, waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Increase delay for next attempt
                continue

            token = search_obj.group(1)

            urls = []
            headers = {
                'authority': 'duckduckgo.com',
                'accept': 'application/json',
                'sec-fetch-dest': 'empty',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'referer': 'https://duckduckgo.com/',
                'accept-language': 'en-US,en;q=0.9'
            }
            params = {'l': 'us-en', 'o': 'json', 'q': term,
                      'vqd': token, 'f': ',,,', 'p': '1', 'v7exp': 'a'}

            for i in range(max_images//100):
                try:
                    params['q'] = term
                    res = requests.get(
                        url + 'i.js', headers=headers, params=params)
                    data = res.json()
                    urls += [x['image'] for x in data['results']]
                    if "next" not in data:
                        break
                    params['s'] = data['next']
                    time.sleep(0.5)  # Be more polite to the server
                except Exception as e:
                    print(f"Error in search loop: {e}")
                    break

            return urls[:max_images]

        except Exception as e:
            print(f"Search attempt {attempt+1} failed: {e}")
            time.sleep(retry_delay)
            retry_delay *= 2

    # If all attempts fail, return an empty list
    print(f"All search attempts for '{term}' failed. Skipping.")
    return []

# Main function to run all the code


def main():
    "Train a 5‑class animal classifier and export it as *animal_classifier.pkl*"

    path = Path('images')               # images/cats, images/dogs, …

    classes = ['cats', 'dogs', 'goats', 'horses', 'pigs']

    # ---------- NEW: show how many you actually have ----------
    counts = {c: len(list((path/c).glob('*'))) for c in classes}
    print('📷  images per class →', counts)

    # (optional) fail only if *zero* images are missing
    for c, n in counts.items():
        if n == 0:
            raise ValueError(f'No images found for {c} in {path/c}')

    # -------------------- DataBlock ----------------------------
    animals = DataBlock(
        blocks     = (ImageBlock, CategoryBlock),
        get_items  = get_image_files,
        splitter   = RandomSplitter(valid_pct=0.2, seed=42),
        get_y      = parent_label,
        item_tfms  = Resize(460),
        batch_tfms = [*aug_transforms(size=224, min_scale=0.75),
                      Normalize.from_stats(*imagenet_stats)]
    )

    dls = animals.dataloaders(path, bs=32)

    # ------------------- training ------------------------------
    learn = vision_learner(dls, resnet34, metrics=accuracy)
    learn.fine_tune(15, base_lr=3e-3)        # still 15 epochs

    learn.export('animal_classifier.pkl')
    print('✅  exported to  animal_classifier.pkl')


# This is the critical fix for multiprocessing on Windows
if __name__ == '__main__':
    multiprocessing.freeze_support()  # Required for Windows
    main()
