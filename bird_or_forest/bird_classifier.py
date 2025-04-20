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
                print(f"Token not found on attempt {attempt+1}, waiting {retry_delay} seconds...")
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
            params = {'l': 'us-en', 'o': 'json', 'q': term, 'vqd': token, 'f': ',,,', 'p': '1', 'v7exp': 'a'}
            
            for i in range(max_images//100):
                try:
                    params['q'] = term
                    res = requests.get(url + 'i.js', headers=headers, params=params)
                    data = res.json()
                    urls += [x['image'] for x in data['results']]
                    if "next" not in data: break
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
    # Create directories for storing images
    path = Path('images')
    if not path.exists():
        path.mkdir(parents=True)

    # Download bird and non-bird images - COMMENTED OUT
    # Modified search terms to be more reliable
    '''
    searches = [
        'bird photography', 'wild birds', 'colorful birds', 'birds in flight', 'bird portrait',
        'landscape photography', 'forest scene', 'city buildings', 'car photography', 'mountain view'
    ]
    paths = [
        'images/birds', 'images/birds', 'images/birds', 'images/birds', 'images/birds',
        'images/forest', 'images/forest', 'images/forest', 'images/forest', 'images/forest'
    ]
    
    # Add a delay between search terms to avoid being blocked
    search_delay = 10  # seconds
    
    for idx, (search, dest_path) in enumerate(zip(searches, paths)):
        dest = Path(dest_path)
        if not dest.exists():
            dest.mkdir(parents=True)
        
        # Only download if directory is empty or has fewer than target number
        target_count = 400
        current_count = len(list(dest.iterdir()))
        
        if current_count < target_count:
            print(f"Searching for '{search}' ({idx+1}/{len(searches)})...")
            # Reduce max_images to improve reliability
            urls = search_images_ddg(search, max_images=200)
            print(f"Found {len(urls)} '{search}' images")
            
            if len(urls) == 0:
                print(f"Skipping '{search}' due to search failure")
                time.sleep(search_delay)
                continue
            
            # Calculate starting index to avoid overwriting existing files
            start_idx = current_count
            
            for i, url in enumerate(urls):
                try:
                    print(f"Downloading image {i+1}/{len(urls)} for '{search}'", end="\r")
                    response = requests.get(url, timeout=4)
                    img_path = dest/f"{start_idx + i}.jpg"
                    img_path.write_bytes(response.content)
                    # Basic validation - skip if can't open
                    try:
                        img = PILImage.create(img_path)
                    except:
                        print(f"Error opening {img_path}, removing...")
                        img_path.unlink()
                except Exception as e:
                    print(f"Error downloading {url}: {e}")
            
            print(f"\nCompleted downloading for '{search}'")
            # Wait between search terms to avoid being rate limited
            if idx < len(searches) - 1:
                print(f"Waiting {search_delay} seconds before next search...")
                time.sleep(search_delay)
    '''

    # Define paths directly since we're skipping the download part
    bird_path = 'images/birds'
    forest_path = 'images/forest'

    # Verify we have images
    bird_files = get_image_files(bird_path)
    not_bird_files = get_image_files(forest_path)
    print(f"Bird images: {len(bird_files)}, Non-bird images: {len(not_bird_files)}")

    # Create DataLoaders
    birds = DataBlock(
        blocks=(ImageBlock, CategoryBlock),
        get_items=get_image_files,
        splitter=RandomSplitter(valid_pct=0.2, seed=42),
        get_y=parent_label,
        item_tfms=Resize(224)
    )

    # Load data with augmentation
    dls = birds.dataloaders(path, batch_size=32, item_tfms=Resize(224),
                          batch_tfms=aug_transforms(size=224, min_scale=0.75))

    # Train the model - using ResNet34 for better accuracy
    learn = vision_learner(dls, resnet34, metrics=error_rate)
    learn.fine_tune(10)  # Train for 10 epochs for better accuracy

    # Save the model
    learn.export('bird_classifier.pkl')

    # Example of using the model on a new image
    test_image_path = 'images/birds/0.jpg'  # Example path, using first bird image
    img = PILImage.create(test_image_path)

    # Make prediction
    pred, _, probs = learn.predict(img)
    print(f"Prediction: {pred}")
    print(f"Probability: {probs[1].item():.6f}")

    print("Model training complete. Saved as 'bird_classifier.pkl'")

# This is the critical fix for multiprocessing on Windows
if __name__ == '__main__':
    multiprocessing.freeze_support()  # Required for Windows
    main() 