import pdfplumber
from typing import Optional, Dict
from ..utils import clean_text
import os

class PDFScraper:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self, path: Optional[str] = None) -> Optional[str]:
        """
        Extract text from a PDF and clean it.
        """
        pdf_path = path or self.file_path
        out = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        out.append(clean_text(text))
        except Exception as e:
            print(f"[ERROR] Could not read {pdf_path}: {e}")
            return None

        return "\n".join(out) if out else None

    def extract_sections(self, path: Optional[str] = None) -> Dict[str, str]:
        """
        Extract structured sections (abstract, introduction, conclusion) from the PDF text.
        """
        full = self.extract_text(path)
        if not full:
            raise ValueError(f"No text could be extracted from {path or self.file_path}")

        lower = full.lower()
        sections = {"abstract": "", "introduction": "", "conclusion": "", "full": full}

        def get_between(start_kw, end_kws):
            i = lower.find(start_kw)
            if i == -1:
                return ""
            start = i
            end = len(full)
            for kw in end_kws:
                j = lower.find(kw, start + 10)
                if j != -1 and j < end:
                    end = j
                    break
            return full[start:end].strip()

        sections["abstract"] = get_between(
            "abstract", ["introduction", "1. introduction", "background"]
        )
        sections["introduction"] = get_between(
            "introduction", ["conclusion", "results", "related work", "experiments"]
        )
        sections["conclusion"] = get_between(
            "conclusion", ["references", "acknowledgments"]
        )

        return sections

if __name__ == "__main__":
    scraper = PDFScraper("data/papers/sample.pdf")
    sections = scraper.extract_sections("data/papers/sample.pdf")

    output_dir = "data/papers/"
    base_name = "sample_extracted_from_pdf.txt"
    output_path = os.path.join(output_dir, base_name)

    # Combine sections into a single text file
    full_text = ""
    for name, content in sections.items():
        full_text += f"\n\n===== {name.upper()} =====\n"
        full_text += (content or "No content found.") + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text.strip())

    print(f"✅ Extracted text saved to {output_path}")
