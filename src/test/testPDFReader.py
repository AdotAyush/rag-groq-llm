import pdfplumber
with pdfplumber.open("data/papers/Attention-is-all-you-need-Paper.pdf") as pdf:
    first_page = pdf.pages[0]
    text = first_page.extract_text()
    print(text)