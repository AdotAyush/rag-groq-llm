import os
from bs4 import BeautifulSoup
import requests
from typing import Optional, List
from src.utils import clean_text

class WebCrawler:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch visible text content from a given URL and clean it.
        """
        try:
            response = requests.get(url, timeout=self.timeout, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Could not fetch {url}: {e}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove non-visible elements
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        texts = [t.get_text(separator=' ', strip=True) for t in soup.find_all(text=True)]
        visible = " ".join(texts)
        return clean_text(visible)
    

if __name__ == "__main__":
    # ✅ Create output folder
    output_dir = "data/web_pages"
    os.makedirs(output_dir, exist_ok=True)

    # ✅ List of URLs to scrape
    urls = [
        "https://arxiv.org/",
        "https://en.wikipedia.org/wiki/Large_language_model",
        "https://www.ibm.com/topics/what-is-rag",
    ]

    crawler = WebCrawler()
    
    for url in urls:
        print(f"\n[+] Fetching {url}...")
        text = crawler.fetch(url)
        if text:
            # Generate safe filename from URL
            file_name = url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_")
            output_path = os.path.join(output_dir, f"{file_name}.txt")
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"✅ Saved extracted text to {output_path}")
        else:
            print(f"⚠️ Skipped {url} due to fetch error.")
