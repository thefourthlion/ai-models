# ----------------------------------------------
# Rosacea image‑scraper
# ----------------------------------------------
import os, re, json, time, random, urllib.parse
from pathlib import Path
from typing import List
import requests, bs4, PIL.Image as _PIL

SEARCH_SUBJECT="rosacea"; OUTPUT_FOLDER=f"images/{SEARCH_SUBJECT}"
NUM_IMAGES_PER_TERM,TOTAL_DESIRED_IMAGES,SEARCH_DELAY_SECONDS=80,1200,10

def _ascii(t): return t.translate({0x2010:"-",0x2011:"-",0x2012:"-",0x2013:"-",0x2014:"-"})

def generate_search_terms(n:int=30)->List[str]:
    base=[
        "rosacea","facial rosacea","rosacea cheeks","rosacea flare","rosacea pustules",
        "erythematotelangiectatic rosacea","papulopustular rosacea","phymatous rosacea",
        "ocular rosacea","rosacea telangiectasia","rosacea close‑up"
    ]
    site=[
        "site:rosacea.org rosacea","National Rosacea Society photos",
        "site:dermnetnz.org rosacea","DermNet rosacea images",
        "site:aad.org rosacea","AAD rosacea pictures",
        "site:mayoclinic.org rosacea","Mayo Clinic rosacea",
        "site:wikipedia.org rosacea","site:shutterstock.com rosacea",
        "site:alamy.com rosacea"
    ]
    terms = base + site
    banned = ("baby", "infant", "kid", "child", "children",
              "toddler", "cradle cap")
    terms  = [t for t in terms if not any(b in t.lower() for b in banned)]
    random.shuffle(terms)
    return terms[:min(n, len(terms))]

def _bing(term,m=100):
    term=_ascii(term); urls=[]; agent=("Mozilla/5.0 … Chrome/118 Safari/537.36")
    for off in range(0,m,35):
        try:
            r=requests.get(f"https://www.bing.com/images/search?q={urllib.parse.quote(term)}&first={off+1}",
                           headers={"User-Agent":agent},timeout=10)
            soup=bs4.BeautifulSoup(r.text,"html.parser")
            urls+= [json.loads(tag["m"])["murl"] for tag in soup.find_all("a",class_="iusc") if tag.get("m")]
            time.sleep(0.35)
        except Exception as e: print(f"Bing error: {e}")
        if len(urls)>=m: break
    return urls[:m]

def _ddg(term,m=100):
    term=_ascii(term); base="https://duckduckgo.com/"
    try: token=re.search(r'vqd=([\d-]+)&',requests.post(base,data={'q':term}).text).group(1)
    except Exception: return []
    urls=[]; params={'l':'us-en','o':'json','q':term,'vqd':token,'f':',,,','p':'1','v7exp':'a'}
    while len(urls)<m:
        try:
            data=requests.get(base+"i.js",params=params,headers={'User-Agent':'Mozilla/5.0'}).json()
            urls+=[x['image'] for x in data['results']]
            if "next" not in data: break
            params['s']=data['next']; time.sleep(0.35)
        except Exception as e: print(f"DDG error: {e}"); break
    return urls[:m]

def _dl(terms):
    p=Path(OUTPUT_FOLDER); p.mkdir(parents=True,exist_ok=True)
    g=len(list(p.glob("*.jpg"))); tot=0
    for i,t in enumerate(terms,1):
        print(f"\n[{i}/{len(terms)}] {t}"); urls=_bing(t,NUM_IMAGES_PER_TERM)
        if len(urls)<10: urls=max(urls,_ddg(t,NUM_IMAGES_PER_TERM),key=len)
        print(f"   {len(urls)} URLs")
        for u in urls:
            try:
                r=requests.get(u,timeout=4); 
                if r.status_code!=200: continue
                fn=f"{SEARCH_SUBJECT}_{g+1:04d}.jpg"; path=p/fn; path.write_bytes(r.content)
                try:_PIL.open(path).verify(); g+=1; tot+=1; print(f" saved {fn}",end="\r")
                except: path.unlink(missing_ok=True)
            except Exception as e: print(f" ✗ {e}")
        print(f"\n   total {g}")
        if g>=TOTAL_DESIRED_IMAGES: break
        if i<len(terms): time.sleep(SEARCH_DELAY_SECONDS)
    return tot

def main():
    terms=generate_search_terms(); print("=== Rosacea Downloader ===")
    for i,t in enumerate(terms,1): print(f"{i:2d}. {t}")
    if input("Continue? (y/n): ").lower()!="y": return
    st=time.time(); tot=_dl(terms); print(f"\nDone: {tot} images in {OUTPUT_FOLDER}")
if __name__=="__main__":import time; main() 