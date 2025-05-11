# ---------------------------------------------------------------
# Hives / Urticaria image‑scraper
# ---------------------------------------------------------------
import os, re, json, time, random, urllib.parse
from pathlib import Path
from typing import List
import requests, bs4, PIL.Image as _PIL

# ---------------- CONFIG -----------------
SEARCH_SUBJECT        = "hives"
OUTPUT_FOLDER         = f"images/{SEARCH_SUBJECT}"
NUM_IMAGES_PER_TERM   = 80
TOTAL_DESIRED_IMAGES  = 1200
SEARCH_DELAY_SECONDS  = 10
# -----------------------------------------


def _ascii(txt:str)->str:
    return txt.translate({0x2010:"-",0x2011:"-",0x2012:"-",
                          0x2013:"-",0x2014:"-"})


def generate_search_terms(n:int=30)->List[str]:
    base = [
        "hives", "urticaria", "chronic urticaria", "acute urticaria",
        "spontaneous urticaria", "physical urticaria", "pressure urticaria",
        "dermographism", "cold urticaria", "solar urticaria",
        "cholinergic urticaria", "angioedema", "hives rash", "hives welts",
        "allergic hives", "urticarial rash", "hives close‑up",
        "wheal and flare reaction"
    ]
    sites = [
        "site:dermnetnz.org urticaria", "DermNet hives images",
        "site:aad.org urticaria", "AAD hives pictures",
        "site:mayoclinic.org hives", "Mayo Clinic urticaria",
        "site:nhs.uk hives", "site:wikipedia.org urticaria",
        "site:shutterstock.com hives", "site:alamy.com urticaria"
    ]
    terms = base + sites
    banned = ("baby", "infant", "kid", "child", "children",
              "toddler", "cradle cap")
    terms  = [t for t in terms if not any(b in t.lower() for b in banned)]
    random.shuffle(terms)
    return terms[:min(n, len(terms))]


def _bing(term, m=100):
    term = _ascii(term)
    urls, agent = [], ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/118 Safari/537.36")
    for off in range(0, m, 35):
        try:
            r = requests.get(f"https://www.bing.com/images/search?q={urllib.parse.quote(term)}&first={off+1}",
                             headers={"User-Agent": agent}, timeout=10)
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            for tag in soup.find_all("a", class_="iusc"):
                try:
                    urls.append(json.loads(tag["m"])["murl"])
                except: pass
            time.sleep(0.35)
        except Exception as e:
            print(f"Bing error: {e}")
        if len(urls) >= m:
            break
    return urls[:m]


def _ddg(term, m=100):
    term, base = _ascii(term), "https://duckduckgo.com/"
    try:
        token = re.search(r'vqd=([\d-]+)&',
                          requests.post(base, data={'q': term}).text).group(1)
    except Exception:
        return []
    urls, params = [], {
        'l':'us-en','o':'json','q':term,'vqd':token,
        'f':',,,','p':'1','v7exp':'a'
    }
    while len(urls) < m:
        try:
            data = requests.get(base+"i.js", params=params,
                                headers={'User-Agent':'Mozilla/5.0'}).json()
            urls += [x['image'] for x in data['results']]
            if "next" not in data:
                break
            params['s'] = data['next']
            time.sleep(0.35)
        except Exception as e:
            print(f"DDG loop error: {e}")
            break
    return urls[:m]


def _dl(terms):
    p = Path(OUTPUT_FOLDER); p.mkdir(parents=True, exist_ok=True)
    g = len(list(p.glob("*.jpg"))); total = 0
    for i, t in enumerate(terms, 1):
        print(f"\n[{i}/{len(terms)}] {t}")
        urls = _bing(t, NUM_IMAGES_PER_TERM)
        if len(urls) < 10:
            urls = max(urls, _ddg(t, NUM_IMAGES_PER_TERM), key=len)
        print(f"  {len(urls)} URLs")

        for u in urls:
            try:
                r = requests.get(u, timeout=4)
                if r.status_code != 200:
                    continue
                fn = f"{SEARCH_SUBJECT}_{g+1:04d}.jpg"
                path = p / fn
                path.write_bytes(r.content)
                try:
                    _PIL.open(path).verify()
                    g += 1; total += 1; print(f"    saved {fn}", end="\r")
                except:
                    path.unlink(missing_ok=True)
            except Exception as e:
                print(f"    ✗ {e}")
        print(f"\n  → {g} total")
        if g >= TOTAL_DESIRED_IMAGES:
            break
        if i < len(terms):
            time.sleep(SEARCH_DELAY_SECONDS)
    return total


def main():
    terms = generate_search_terms()
    print("=== Hives / Urticaria Downloader ===")
    for n, t in enumerate(terms, 1):
        print(f"{n:2d}. {t}")
    if input("Continue? (y/n): ").lower() != "y":
        return
    st = time.time()
    tot = _dl(terms)
    print(f"\nDone: {tot} images in {OUTPUT_FOLDER}")
if __name__ == "__main__":
    import time; main() 