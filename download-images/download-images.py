# Import required libraries
import os
import requests
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
import random
import urllib.parse
import json

# CONFIGURATION - Edit these variables
SEARCH_SUBJECT = "horse"  # Change this to whatever you want to search for
OUTPUT_FOLDER = f"images/{SEARCH_SUBJECT}"  # Will create a folder with the subject name
NUM_IMAGES_PER_TERM = 100  # Number of images to try downloading per search term
TOTAL_DESIRED_IMAGES = 1200  # Approximate total number of images desired

# Generate animal-specific search terms
def generate_search_terms(subject="pig", num_terms=12):
    """Generate diverse search terms specifically for pigs, goats, horses, or other animals"""
    
    pig_specific_terms = [
        "domestic pig",
        "piglet",
        "farm pig",
        "potbellied pig",
        "wild boar",
        "pink pig",
        "spotted pig",
        "baby pigs",
        "pig in mud",
        "pig farm",
        "pig close up",
        "cute pig",
        "miniature pig",
        "pet pig",
        "pig breeds",
        "pig family",
        "black pig",
        "happy pig",
        "pig portrait",
        "pig wallpaper",
        "pig in nature",
        "Yorkshire pig",
        "Duroc pig",
        "Hampshire pig",
        "Berkshire pig",
        "Gloucestershire Old Spot pig",
        "Kunekune pig"
    ]
    
    goat_specific_terms = [
        "domestic goat",
        "baby goat",
        "kid goat",
        "farm goat",
        "mountain goat",
        "pygmy goat",
        "Nigerian Dwarf goat",
        "Alpine goat",
        "Nubian goat",
        "Boer goat",
        "Angora goat",
        "goat herd",
        "goat farm",
        "goat close up",
        "cute goat",
        "goat breeds",
        "goat family",
        "black goat",
        "white goat",
        "spotted goat",
        "goat portrait",
        "dairy goat",
        "meat goat",
        "goat in field",
        "goat climbing",
        "goat in nature",
        "funny goat",
        "LaMancha goat",
        "Fainting goat",
        "Kiko goat"
    ]
    
    horse_specific_terms = [
        "domestic horse",
        "wild horse",
        "thoroughbred horse",
        "arabian horse",
        "quarter horse",
        "draft horse",
        "clydesdale horse",
        "appaloosa horse",
        "paint horse",
        "mustang horse",
        "friesian horse",
        "andalusian horse",
        "foal",
        "mare and foal",
        "stallion",
        "horse herd",
        "horse running",
        "horse galloping",
        "horse portrait",
        "horse close up",
        "horse farm",
        "horse in field",
        "horse in stable",
        "horse jumping",
        "dressage horse",
        "beautiful horse",
        "horse head shot",
        "horse in nature",
        "bay horse",
        "palomino horse",
        "black horse",
        "white horse",
        "pinto horse",
        "racing horse",
        "show horse"
    ]
    
    # If the subject is "pig", use pig-specific terms
    if subject.lower() == "pig":
        return random.sample(pig_specific_terms, min(num_terms, len(pig_specific_terms)))
    
    # If the subject is "goat", use goat-specific terms
    elif subject.lower() == "goat":
        return random.sample(goat_specific_terms, min(num_terms, len(goat_specific_terms)))
    
    # If the subject is "horse", use horse-specific terms
    elif subject.lower() == "horse":
        return random.sample(horse_specific_terms, min(num_terms, len(horse_specific_terms)))
    
    # For other subjects, fall back to the original function logic
    else:
        # Templates for search term variety (original function logic)
        templates = [
            "{subject} photography",
            "{subject} in the wild",
            "cute {subject}",
            "{subject} close up",
            "{subject} portrait",
            "professional {subject} photo",
            "{subject} outdoors",
            "different types of {subject}",
            "funny {subject}",
            "beautiful {subject}",
            "{subject} in nature",
            "rare {subject}",
            "{subject} breeds",
            "exotic {subject}",
            "{subject} pictures"
        ]
        
        # Randomly select templates to create diversity
        selected_templates = random.sample(templates, min(num_terms, len(templates)))
        return [template.format(subject=subject) for template in selected_templates]

# Function to search for images using Bing
def search_images_bing(term, max_images=100):
    """Search for images using Bing image search"""
    image_urls = []
    
    # Multiple pages to get more images
    for offset in range(0, max_images, 35):
        # Bing images search URL with pagination
        search_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(term)}&form=HDRSC2&first={offset+1}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.bing.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        try:
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find image data in the page
            for img in soup.find_all("a", class_="iusc"):
                m = img.get("m")
                if m:
                    try:
                        data = json.loads(m)
                        if "murl" in data:
                            image_urls.append(data["murl"])
                    except:
                        continue
            
            # Respect the site by waiting briefly
            time.sleep(0.5)
        except Exception as e:
            print(f"Error searching Bing: {e}")
        
        # Break if we have enough URLs
        if len(image_urls) >= max_images:
            break
    
    return image_urls[:max_images]

# Function to search for images using DuckDuckGo (as fallback)
def search_images_ddg(term, max_images=100, retry_delay=5):
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
            
            for i in range(max_images//100 + 1):
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

# Function to download images
def download_images(search_terms, output_folder, num_images_per_term=100):
    """Download images for multiple search terms into organized folders"""
    # Create main output folder
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    total_downloaded = 0
    search_delay = 10  # seconds between searches
    
    for idx, term in enumerate(search_terms):
        print(f"\n[{idx+1}/{len(search_terms)}] Searching for: '{term}'")
        
        # Create safe filename from search term
        safe_term = "".join(c if c.isalnum() else "_" for c in term)
        
        # Count existing images to avoid overwriting
        existing_images = len([f for f in output_path.glob(f"{safe_term}_*.jpg")])
        
        if existing_images >= num_images_per_term:
            print(f"Already have {existing_images} images for '{term}', skipping...")
            total_downloaded += existing_images
            continue
        
        # Search for images - try Bing first, DDG as backup
        print(f"Searching Bing Images for '{term}'...")
        urls = search_images_bing(term, max_images=num_images_per_term)
        
        # If Bing didn't work well, try DuckDuckGo as fallback
        if len(urls) < 10:
            print(f"Bing search returned only {len(urls)} results. Trying DuckDuckGo...")
            ddg_urls = search_images_ddg(term, max_images=num_images_per_term)
            if len(ddg_urls) > len(urls):
                urls = ddg_urls
                
        print(f"Found {len(urls)} images for '{term}'")
        
        if not urls:
            print(f"No images found for '{term}', continuing to next term...")
            if idx < len(search_terms) - 1:
                print(f"Waiting {search_delay} seconds before next search...")
                time.sleep(search_delay)
            continue
        
        # Download images
        term_downloaded = 0
        for i, url in enumerate(urls):
            try:
                img_filename = f"{safe_term}_{existing_images + i}.jpg"
                img_path = output_path / img_filename
                
                print(f"Downloading image {i+1}/{len(urls)}", end="\r")
                
                response = requests.get(url, timeout=4)
                if response.status_code != 200:
                    continue
                
                img_path.write_bytes(response.content)
                
                # Verify image is valid
                try:
                    from PIL import Image
                    img = Image.open(img_path)
                    img.verify()  # Verify it's a valid image
                    term_downloaded += 1
                except Exception as e:
                    print(f"Invalid image: {img_path}, removing... ({e})")
                    img_path.unlink(missing_ok=True)
            except Exception as e:
                print(f"Error downloading {url}: {e}")
        
        print(f"\nSuccessfully downloaded {term_downloaded} images for '{term}'")
        total_downloaded += term_downloaded
        
        # Wait between searches to avoid rate limiting
        if idx < len(search_terms) - 1:
            print(f"Waiting {search_delay} seconds before next search...")
            time.sleep(search_delay)
    
    return total_downloaded

def main():
    # Generate search terms based on the subject
    num_terms = 12  # Fixed at 12 search terms
    search_terms = generate_search_terms(SEARCH_SUBJECT, num_terms)
    
    print(f"=== Image Downloader for '{SEARCH_SUBJECT}' ===")
    print(f"Going to search for the following terms:")
    for i, term in enumerate(search_terms):
        print(f"  {i+1}. {term}")
    print(f"Images will be saved to: {OUTPUT_FOLDER}")
    print(f"Target: ~{TOTAL_DESIRED_IMAGES} images total")
    print("=" * 50)
    
    # Confirm with user
    if input("Continue? (y/n): ").lower() != 'y':
        print("Operation cancelled")
        return
    
    # Download images
    start_time = time.time()
    total_downloaded = download_images(
        search_terms, 
        OUTPUT_FOLDER, 
        NUM_IMAGES_PER_TERM
    )
    
    # Report results
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"Download complete!")
    print(f"Total images downloaded: {total_downloaded}")
    print(f"Images saved to: {OUTPUT_FOLDER}")
    print(f"Time taken: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
    print("=" * 50)

if __name__ == "__main__":
    main() 