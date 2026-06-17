# PDF Report Extraction (pdfplumber)

## When to Use

When the user provides a PDF file containing sports analysis, predictions, or
statistical reports that need to be extracted and integrated into the prediction
system.

## Method

```python
import pdfplumber

pdf_path = r"path\to\report.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    
    # Extract all text
    full_text = ""
    for i in range(total_pages):
        page = pdf.pages[i]
        text = page.extract_text()
        if text:
            full_text += f"\n\n--- PAGE_{i+1} ---\n{text}"
    
    # Save full text
    with open("output/report_full_text.txt", 'w', encoding='utf-8') as f:
        f.write(full_text)
```

## Proven Results

- Kimi 2026 World Cup Report: 205 pages, 274,798 characters extracted
- All text content successfully extracted (tables, figures as text)
- Page markers (`--- PAGE_N ---`) enable section-by-section analysis

## Pitfalls

1. **Install pdfplumber first**: `uv pip install pdfplumber pypdf`
2. **Encoding**: Always use `encoding='utf-8'` for Chinese content
3. **Page count verification**: Check `len(pdf.pages)` matches expected
4. **Empty pages**: Some pages may have no extractable text (images only)
5. **Large files**: 200+ page PDFs can produce 200K+ characters; process in chunks
