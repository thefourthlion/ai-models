#!/usr/bin/env python3
"""
Animal Image Downloader Script
Downloads images of various animals from web search results with size verification and standardization
"""

import os
import time
import json
import random
import requests
import urllib.parse
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PIL import Image
import io
from tqdm import tqdm


import random

def generate_search_terms(subject, num_terms):
    """Generate diverse search terms for a given subject with size specifications"""
    base_terms = [
        # High quality descriptors
        f"{subject} high resolution photo",
        f"{subject} detailed photograph",
        f"{subject} professional picture",
        f"{subject} 4K image",
        f"{subject} high definition",
        f"{subject} clear detailed shot",
        
        # Environments and contexts
        f"{subject} in natural habitat",
        f"{subject} outdoors",
        f"{subject} in the wild",
        f"{subject} close up",
        f"{subject} full body shot",
        
        # Different angles and compositions
        f"{subject} profile view",
        f"{subject} front view",
        f"{subject} side angle",
        f"{subject} from above",
        
        # Different lighting and settings
        f"{subject} daylight",
        f"{subject} studio lighting",
        f"{subject} nature background",
        
        # Actions and behaviors
        f"{subject} moving",
        f"{subject} standing",
        f"{subject} eating",
        f"{subject} resting",
        
        # Life stages and varieties
        f"{subject} adult",
        f"{subject} young",
        f"{subject} different varieties",
        f"{subject} common types",
        
        # Photography styles
        f"{subject} wildlife photography",
        f"{subject} nature documentary",
        f"{subject} stock photo",
        f"{subject} educational image"
    ]
    
    # Add specific contexts based on animal categories
    if any(x in subject.lower() for x in ["dog", "cat", "rabbit", "horse", "hamster", "guinea pig"]):
        pet_terms = [
            f"{subject} pet portrait",
            f"{subject} domestic",
            f"{subject} breed varieties",
            f"{subject} with owner",
            f"{subject} pet care"
        ]
        base_terms.extend(pet_terms)
    
    if any(x in subject.lower() for x in ["chicken", "cow", "sheep", "goat", "pig", "cattle", "duck", "turkey"]):
        farm_terms = [
            f"{subject} farm animal",
            f"{subject} livestock",
            f"{subject} farming",
            f"{subject} agricultural",
            f"{subject} farmyard"
        ]
        base_terms.extend(farm_terms)
    
    if any(x in subject.lower() for x in ["mouse", "rat", "squirrel", "chipmunk", "vole", "mole"]):
        rodent_terms = [
            f"{subject} rodent",
            f"{subject} small mammal",
            f"{subject} foraging",
            f"{subject} burrowing",
            f"{subject} nocturnal"
        ]
        base_terms.extend(rodent_terms)
    
    if any(x in subject.lower() for x in ["frog", "toad", "gecko", "fish", "goldfish", "carp", "tilapia", "danio"]):
        aquatic_terms = [
            f"{subject} aquatic",
            f"{subject} in water",
            f"{subject} swimming",
            f"{subject} underwater shot",
            f"{subject} pond"
        ]
        base_terms.extend(aquatic_terms)
        
    if any(x in subject.lower() for x in ["bird", "sparrow", "dove", "pigeon", "crow", "robin", "magpie", "seagull", "starling"]):
        bird_terms = [
            f"{subject} bird flying",
            f"{subject} perched",
            f"{subject} in flight",
            f"{subject} nesting",
            f"{subject} on branch"
        ]
        base_terms.extend(bird_terms)
        
    if any(x in subject.lower() for x in ["raccoon", "fox", "skunk", "coyote", "deer", "bat", "opossum"]):
        wild_terms = [
            f"{subject} wild animal",
            f"{subject} nocturnal",
            f"{subject} forest",
            f"{subject} urban wildlife",
            f"{subject} mammal"
        ]
        base_terms.extend(wild_terms)
        
    if any(x in subject.lower() for x in ["ant", "fly", "mosquito", "cockroach", "housefly"]):
        insect_terms = [
            f"{subject} insect macro",
            f"{subject} close up detailed",
            f"{subject} bug",
            f"{subject} macro photography",
            f"{subject} arthropod"
        ]
        base_terms.extend(insect_terms)
    
    # Always add size specifications to help meet requirements
    for i in range(len(base_terms)):
        if random.random() < 0.5:  # 50% chance to add size specification
            base_terms[i] += " large size"
    
    # Randomize and take only the needed number
    random.shuffle(base_terms)
    return base_terms[:num_terms] 

# CONFIGURATION - Edit these variables
SUBJECTS = [
    # Domesticated & Farm Animals
    "Chicken", "Cattle", "Cow", "Sheep", "Goat", "Pig", "Dog", "Cat", "Horse", 
    "Duck", "Turkey", "Donkey", "Rabbit", "Pigeon", "Camel", "Water buffalo",
    
    # Rodents & Small Mammals
    "Mouse", "Rat", "Squirrel", "Guinea pig", "Hamster", "Mole", "Vole", "Chipmunk",
    
    # Common Birds
    "House sparrow", "Rock dove", "Starling", "Crow", "Magpie", "Seagull", 
    "Blackbird", "Robin",
    
    # Reptiles, Amphibians, and Fish
    "House gecko", "Common frog", "American bullfrog", "Common toad", "Goldfish", 
    "Carp", "Tilapia", "Zebra danio",
    
    # Urban and Wild Mammals
    "Raccoon", "Fox", "Red fox", "Skunk", "Coyote", "Deer", "Bat", "Opossum",
    
    # Insects & Other Ubiquitous Species
    "Ant", "Fly", "Housefly", "Mosquito", "Cockroach"
]

MAIN_OUTPUT_FOLDER = "images/animals"  # Root folder for all animal images
IMAGES_PER_SUBJECT = 1200  # Will download this many per subject
SEARCH_TERMS_PER_SUBJECT = 6  # Number of search terms per subject to increase variety

# Image size requirements
MIN_WIDTH = 512  # Minimum width in pixels
MIN_HEIGHT = 512  # Minimum height in pixels
TARGET_SIZE = (512, 512)  # Target size for resizing (width, height)
RESIZE_IMAGES = True  # Set to True to resize all images to TARGET_SIZE

# Maximum number of parallel downloads
MAX_WORKERS = 5

# User agent to mimic a browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def generate_search_terms(subject, num_terms):
    """Generate search terms for a given subject with size specifications"""
    base_terms = [
        f"{subject} photo large",
        f"{subject} high resolution picture",
        f"{subject} high quality image",
        f"{subject} in wild clear photo",
        f"{subject} close up detailed",
        f"{subject} high definition picture",
        f"{subject} high resolution photo",
        f"{subject} clear image",
        f"{subject} detailed photo",
        f"{subject} professional photograph",
    ]
    
    # Add some specific terms based on the subject
    if any(x in subject.lower() for x in ["dog", "cat", "rabbit", "horse"]):
        base_terms.extend([
            f"{subject} pet high resolution",
            f"{subject} cute high quality",
            f"{subject} breed detailed photo"
        ])
    
    if any(x in subject.lower() for x in ["chicken", "cow", "sheep", "goat", "pig"]):
        base_terms.extend([
            f"{subject} farm high resolution",
            f"{subject} livestock detailed photo"
        ])
    
    if any(x in subject.lower() for x in ["frog", "toad", "gecko", "fish"]):
        base_terms.extend([
            f"{subject} aquatic high quality",
            f"{subject} water detailed photo"
        ])
        
    if any(x in subject.lower() for x in ["bird", "sparrow", "dove", "pigeon", "crow"]):
        base_terms.extend([
            f"{subject} flying high resolution",
            f"{subject} perched detailed photo"
        ])
    
    # Randomize and take only the needed number
    random.shuffle(base_terms)
    return base_terms[:num_terms]

def search_duckduckgo(query, max_results=20):
    """Search for images using DuckDuckGo with size preference"""
    try:
        # Modify the query to prefer larger images
        size_query = f"{query} large"
        
        # DuckDuckGo search URL
        vqd_param = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz-_', k=7))
        url = f"https://duckduckgo.com/i.js?q={urllib.parse.quote(size_query)}&o=json&vqd={vqd_param}&f=,,,&p=1"
        
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://duckduckgo.com/",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            results = response.json().get("results", [])
            image_urls = [result.get("image") for result in results if result.get("image")]
            return image_urls[:max_results]
        else:
            print(f"DuckDuckGo search failed with status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error in DuckDuckGo search: {str(e)}")
        return []

def search_bing(query, max_results=20):
    """Search for images using Bing with size preference"""
    try:
        # Modify to include size parameter
        size_param = "&qft=+filterui:imagesize-large"
        search_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}{size_param}&form=HDRSC2&first=1"
        
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract image URLs
            image_urls = []
            for img in soup.select('.mimg'):
                if img.has_attr('src') and img['src'].startswith('http'):
                    image_urls.append(img['src'])
            
            # Alternative method if the above doesn't work
            if not image_urls:
                pattern = r'murl&quot;:&quot;(.*?)&quot;'
                image_urls = re.findall(pattern, response.text)
            
            return image_urls[:max_results]
        else:
            print(f"Bing search failed with status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error in Bing search: {str(e)}")
        return []

def search_images(query, max_results=10):
    """Search for images using multiple search engines with fallback"""
    print(f"Searching for '{query}'...")
    
    # Try DuckDuckGo first
    image_urls = search_duckduckgo(query, max_results)
    
    # If DuckDuckGo doesn't return enough results, try Bing
    if len(image_urls) < max_results:
        print(f"DuckDuckGo returned only {len(image_urls)} results. Trying Bing...")
        bing_results = search_bing(query, max_results - len(image_urls))
        image_urls.extend(bing_results)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in image_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    # If we still don't have enough results
    if len(unique_urls) < max_results:
        print(f"Could only find {len(unique_urls)} images for '{query}'")
    
    return unique_urls[:max_results]

def download_image(url, output_path, subject, image_number):
    """Download an image from a URL to the specified path with size verification and sequential naming"""
    try:
        # Get file extension from URL
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        extension = os.path.splitext(original_filename)[1].lower()
        
        # If no valid extension found, default to .jpg
        if not extension or extension not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            extension = '.jpg'
            
        # Create sequential filename
        filename = f"{subject.lower()}-{image_number}{extension}"
        
        # Full path where the image will be saved
        full_path = os.path.join(output_path, filename)
        
        # Don't redownload if the file already exists
        if os.path.exists(full_path):
            return None
        
        # Download the image
        headers = {"User-Agent": USER_AGENT, "Referer": "https://www.google.com/"}
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        
        if response.status_code == 200:
            # Check image dimensions before saving
            try:
                image_content = response.content
                image = Image.open(io.BytesIO(image_content))
                width, height = image.size
                
                # Skip if image is too small
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    print(f"Skipping small image: {width}x{height} (minimum {MIN_WIDTH}x{MIN_HEIGHT})")
                    return None
                
                # Resize if needed
                if RESIZE_IMAGES:
                    image = image.resize(TARGET_SIZE, Image.LANCZOS)
                    # Save the resized image
                    image.save(full_path)
                else:
                    # Save the original image
                    with open(full_path, 'wb') as f:
                        f.write(image_content)
                
                return full_path
                
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return None
        else:
            print(f"Failed to download image, status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

def download_images(search_terms, output_folder, num_images_per_term=200):
    """Search and download multiple images for a list of search terms"""
    os.makedirs(output_folder, exist_ok=True)
    
    # Keep track of how many successful downloads we've had
    successful_downloads = 0
    max_attempts = num_images_per_term * 3  # Allow for some failures
    attempt_count = 0
    
    # Extract subject from the folder name
    subject = os.path.basename(output_folder)
    
    # Find the current highest image number to continue sequencing
    image_number = 1
    for file in os.listdir(output_folder):
        match = re.search(r'^' + re.escape(subject.lower()) + r'-(\d+)', file)
        if match:
            num = int(match.group(1))
            if num >= image_number:
                image_number = num + 1
    
    for term in search_terms:
        # Target number of images from this term
        target_from_term = min(num_images_per_term, 
                             IMAGES_PER_SUBJECT - successful_downloads)
        
        if target_from_term <= 0:
            break  # We've reached our goal
            
        # Get image URLs - get more than we need since some will fail size requirements
        image_urls = search_images(term, max_results=target_from_term * 2)
        
        # Process images
        term_successful = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            download_tasks = []
            for url in image_urls:
                if attempt_count >= max_attempts:
                    break
                    
                download_tasks.append(
                    executor.submit(download_image, url, output_folder, subject, image_number + successful_downloads)
                )
                attempt_count += 1
            
            # Collect results as they complete
            for future in tqdm(download_tasks, desc=f"Downloading images for '{term}'"):
                downloaded_path = future.result()
                if downloaded_path:
                    term_successful += 1
                    successful_downloads += 1
                    
                    # If we've reached our target, break out
                    if successful_downloads >= IMAGES_PER_SUBJECT:
                        break
        
        print(f"Got {term_successful} images from search term '{term}'")
        
        # If we've reached our target, break out
        if successful_downloads >= IMAGES_PER_SUBJECT:
            print(f"Reached target of {IMAGES_PER_SUBJECT} images for {subject}")
            break
    
    return successful_downloads

def main():
    # Create the main output directory
    main_output_path = Path(MAIN_OUTPUT_FOLDER)
    main_output_path.mkdir(parents=True, exist_ok=True)
    
    # Add PIL dependency check
    try:
        from PIL import Image
        print("PIL/Pillow is installed and ready for image processing")
    except ImportError:
        print("ERROR: PIL/Pillow is required for image processing.")
        print("Please install it with: pip install Pillow")
        return
    
    print(f"=== Animal Image Downloader ===")
    print(f"Going to download images for {len(SUBJECTS)} different animals/species")
    print(f"Target: {IMAGES_PER_SUBJECT} images per subject")
    print(f"Image size requirements: Minimum {MIN_WIDTH}x{MIN_HEIGHT} pixels")
    if RESIZE_IMAGES:
        print(f"All images will be resized to {TARGET_SIZE[0]}x{TARGET_SIZE[1]} pixels")
    print(f"Images will be saved to: {MAIN_OUTPUT_FOLDER}")
    print(f"WARNING: This will download approximately {len(SUBJECTS) * IMAGES_PER_SUBJECT} images")
    print(f"Estimated storage requirement: {(len(SUBJECTS) * IMAGES_PER_SUBJECT * 0.5) / 1024:.1f} GB (at ~0.5MB per image)")
    print("=" * 50)
    
    # Confirm with user
    if input("Continue? (y/n): ").lower() != 'y':
        print("Operation cancelled")
        return
    
    # Download images for each subject
    start_time = time.time()
    total_downloaded = 0
    
    for idx, subject in enumerate(SUBJECTS):
        print(f"\n[{idx+1}/{len(SUBJECTS)}] Processing: '{subject}'")
        
        # Create subject-specific output folder
        subject_folder = main_output_path / subject.lower().replace(" ", "_")
        subject_folder.mkdir(exist_ok=True)
        
        # Generate search terms for this subject
        search_terms = generate_search_terms(subject, SEARCH_TERMS_PER_SUBJECT)
        print(f"Search terms for {subject}:")
        for i, term in enumerate(search_terms):
            print(f"  {i+1}. {term}")
        
        # Download images for this subject
        images_downloaded = download_images(
            search_terms, 
            str(subject_folder), 
            num_images_per_term=IMAGES_PER_SUBJECT // SEARCH_TERMS_PER_SUBJECT
        )
        
        total_downloaded += images_downloaded
        print(f"Downloaded {images_downloaded} images for '{subject}'")
        print(f"Progress: {total_downloaded}/{len(SUBJECTS) * IMAGES_PER_SUBJECT} total images")
        
        # Small delay between subjects to avoid triggering rate limits
        if idx < len(SUBJECTS) - 1:
            delay = 5
            print(f"Waiting {delay} seconds before the next subject...")
            time.sleep(delay)
    
    # Report results
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"Download complete!")
    print(f"Total images downloaded: {total_downloaded}")
    print(f"Images saved to: {MAIN_OUTPUT_FOLDER}")
    print(f"Time taken: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
    print("=" * 50)

if __name__ == "__main__":
    main() 