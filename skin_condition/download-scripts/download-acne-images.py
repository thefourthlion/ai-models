# ----------------------------------------------
# Acne Vulgaris image‑scraper
# ----------------------------------------------
import os, re, json, time, random, urllib.parse
from pathlib import Path
from typing   import List
import requests
from bs4 import BeautifulSoup
from PIL import Image                 # for validation

# -------------------- CONFIG -------------------
SEARCH_SUBJECT        = "acne"        # used for folder & filenames
OUTPUT_FOLDER         = f"images/{SEARCH_SUBJECT}"
NUM_IMAGES_PER_TERM   = 80            # 30 × 80 ≈ 2 400 raw URLS → stop at 1 200
TOTAL_DESIRED_IMAGES  = 1200
SEARCH_DELAY_SECONDS  = 10
# ----------------------------------------------


# -------------- helpers -----------------
def ascii_hyphens(text: str) -> str:
    """
    Replace common 'fancy' hyphens (– — ‑) with the normal ASCII hyphen‑minus
    so they won't choke URL quoting or header building.
    """
    return text.translate({
        0x2010: "-", 0x2011: "-", 0x2012: "-",
        0x2013: "-", 0x2014: "-",
    })


# -------- acne‑centric search terms --------
def generate_search_terms(num_terms: int = 30) -> List[str]:
    """
    Build a randomised list of Bing/DDG‑friendly acne search phrases,
    mixing generic terms with site‑scoped queries to help source
    high‑quality clinical photos.
    """
    base_terms = [
        "acne", "acne vulgaris", "facial acne", "back acne", "chest acne",
        "cystic acne", "nodulocystic acne", "baby acne", "hormonal acne",
        "whiteheads", "blackheads", "comedonal acne", "inflammatory acne",
        "acne papules", "acne pustules", "acne nodules", "acne scarring",
        "acne scars", "post‑acne hyperpigmentation", "acne close‑up",
    ]

    site_terms = [
        # DermNet NZ
        "site:dermnetnz.org acne", "DermNet acne images",
        "DermNet facial acne", "DermNet back acne", "DermNet acne scarring",

        # Mayo Clinic
        "site:mayoclinic.org acne", "Mayo Clinic acne types",
        "Mayo Clinic cystic acne",

        # GoodRx
        "site:goodrx.com acne", "GoodRx hormonal acne images",
        "GoodRx acne scarring",

        # Wikipedia (often hosts public‑domain clinical images)
        "site:wikipedia.org acne vulgaris",

        # Stock / awareness days
        "site:shutterstock.com acne", "World Acne Day photos",
    ]

    all_terms = base_terms + site_terms

    # ── filter out minors‑related phrases ───────────────────────
    banned = ("baby", "infant", "kid", "child", "children",
              "toddler", "cradle cap")
    all_terms = [t for t in all_terms
                 if not any(b in t.lower() for b in banned)]
    # ------------------------------------------------------------

    random.shuffle(all_terms)
    return all_terms[:min(num_terms, len(all_terms))]
# ----------------------------------------------


# -------------- IMAGE SEARCH ENGINES ----------
def search_images_bing(term, max_images=100):
    """Return up to max_images image‑urls from Bing Images"""
    term  = ascii_hyphens(term)
    urls  = []
    agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/118.0 Safari/537.36")

    for offset in range(0, max_images, 35):
        url = (f"https://www.bing.com/images/search?"
               f"q={urllib.parse.quote(term)}&first={offset+1}")
        try:
            r = requests.get(url, timeout=10,
                             headers={"User-Agent": agent})
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup.find_all("a", class_="iusc"):
                m = tag.get("m")
                if not m:
                    continue
                try:
                    data = json.loads(m)
                    urls.append(data["murl"])
                except Exception:
                    pass
            time.sleep(0.35)
        except Exception as e:
            print(f"Bing error: {e}")
        if len(urls) >= max_images:
            break
    return urls[:max_images]


def search_images_ddg(term, max_images=100):
    """DuckDuckGo image search as fallback."""
    term = ascii_hyphens(term)
    base = "https://duckduckgo.com/"
    try:
        token = re.search(r'vqd=([\d-]+)&',
                          requests.post(base, data={'q': term}).text).group(1)
    except Exception:
        return []

    urls, params = [], {
        'l': 'us-en', 'o': 'json', 'q': term, 'vqd': token,
        'f': ',,,', 'p': '1', 'v7exp': 'a'
    }
    agent = "Mozilla/5.0"
    while len(urls) < max_images:
        try:
            res = requests.get(base + "i.js", params=params,
                               headers={'User-Agent': agent})
            data = res.json()
            urls += [x['image'] for x in data['results']]
            if "next" not in data:
                break
            params['s'] = data['next']
            time.sleep(0.35)
        except Exception as e:
            print(f"DDG loop error: {e}")
            break
    return urls[:max_images]
# ----------------------------------------------


# ----------------- DOWNLOADER -----------------
def download_images(terms: List[str], output_dir: str, subject: str):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    global_counter   = len(list(out_path.glob("*.jpg")))
    total_downloaded = 0

    for idx, term in enumerate(terms, 1):
        print(f"\n[{idx}/{len(terms)}] term => '{term}'")

        # collect URLs (Bing then fallback DDG)
        print("  → Bing search ...")
        urls = search_images_bing(term, NUM_IMAGES_PER_TERM)
        if len(urls) < 10:
            print(f"  ↳ only {len(urls)} hits, trying DuckDuckGo …")
            urls = max(urls, search_images_ddg(term, NUM_IMAGES_PER_TERM),
                       key=len)

        print(f"  → {len(urls)} URLs found")

        # download
        for url in urls:
            try:
                r = requests.get(url, timeout=4)
                if r.status_code != 200:
                    continue

                filename = f"{subject}_{global_counter+1:04d}.jpg"
                img_path = out_path / filename
                img_path.write_bytes(r.content)

                # quick validity test
                try:
                    Image.open(img_path).verify()
                    global_counter   += 1
                    total_downloaded += 1
                    print(f"    saved {filename}", end="\r")
                except Exception:
                    img_path.unlink(missing_ok=True)
            except Exception as e:
                print(f"    ✗ {e}")

        print(f"\n  → {global_counter} total so far")

        # early exit once target reached
        if global_counter >= TOTAL_DESIRED_IMAGES:
            break

        if idx < len(terms):
            print(f"  sleeping {SEARCH_DELAY_SECONDS}s …")
            time.sleep(SEARCH_DELAY_SECONDS)

    return total_downloaded
# ----------------------------------------------


# --------------------- MAIN --------------------
def main():
    terms = generate_search_terms(30)
    print("=== Acne Image‑Downloader ===")
    for i, t in enumerate(terms, 1):
        print(f" {i:2d}. {t}")
    print(f"Images folder : {OUTPUT_FOLDER}")
    print(f"Target count  : {TOTAL_DESIRED_IMAGES}\n")

    if input("Continue? (y/n): ").lower() != "y":
        return

    start = time.time()
    total = download_images(terms, OUTPUT_FOLDER, SEARCH_SUBJECT)
    elapsed = time.time() - start

    print("\n----------- DONE -----------")
    print(f"Downloaded : {total}")
    print(f"Saved to   : {OUTPUT_FOLDER}")
    print(f"Elapsed    : {elapsed/60:.1f} min")
    print("-----------------------------")


if __name__ == "__main__":
    main() 