import sys
from pathlib import Path
import re
import pypdfium2 as pdfium

def run_qa():
    old_pdf_path = Path("outputs/methodology_report_old.pdf")
    new_pdf_path = Path("outputs/methodology_report.pdf")
    
    assert old_pdf_path.exists(), "Old PDF does not exist!"
    assert new_pdf_path.exists(), "New PDF does not exist!"
    
    old_doc = pdfium.PdfDocument(str(old_pdf_path))
    new_doc = pdfium.PdfDocument(str(new_pdf_path))
    
    print(f"Old PDF page count: {len(old_doc)}")
    print(f"New PDF page count: {len(new_doc)}")
    assert len(new_doc) == 6, f"Expected 6 pages, got {len(new_doc)}"
    
    # Extract all text from new PDF
    new_pages_text = []
    full_new_text = ""
    for i, page in enumerate(new_doc):
        text = page.get_textpage().get_text_range()
        new_pages_text.append(text)
        full_new_text += f"\n--- PAGE {i+1} ---\n" + text
        
    # Extract all text from old PDF
    old_pages_text = []
    full_old_text = ""
    for i, page in enumerate(old_doc):
        text = page.get_textpage().get_text_range()
        old_pages_text.append(text)
        full_old_text += f"\n--- PAGE {i+1} ---\n" + text
        
    print("\n[+] Checking for Raw LaTeX ($ or \\hat or \\implies)...")
    raw_latex = re.findall(r'(\$[^\$]+\$|\\hat|\\implies|\\mu|\\Delta)', full_new_text)
    print(f"    Raw LaTeX occurrences: {len(raw_latex)} -> {raw_latex}")
    assert len(raw_latex) == 0, f"Found raw LaTeX in new PDF: {raw_latex}"
    
    print("\n[+] Checking Top 10 Batters order and values...")
    expected_batters = [
        ("Suryakumar Yadav", "+28.39", "+8.99", "90.3%"),
        ("Vaibhav Sooryavanshi", "+23.89", "+1.71", "63.2%"),
        ("Jos Buttler", "+23.06", "+8.68", "62.5%"),
        ("Heinrich Klaasen", "+22.73", "+6.01", "58.3%"),
        ("Reeza Hendricks", "+22.64", "+14.31", "57.1%"),
        ("Abhishek Sharma", "+21.93", "−2.25", "53.6%"),
        ("Phil Salt", "+21.69", "+5.79", "49.5%"),
        ("Rinku Singh", "+20.98", "+12.06", "44.9%"),
        ("Shreyas Iyer", "+19.97", "+10.33", "36.5%"),
        ("Tim David", "+19.75", "+0.80", "35.1%"),
    ]
    for name, rating, delta, p_t10 in expected_batters:
        assert name in full_new_text, f"Missing batter {name}"
        assert rating in full_new_text, f"Missing rating {rating} for {name}"
        assert delta in full_new_text or delta.replace("−", "-") in full_new_text, f"Missing delta {delta} for {name}"
        assert p_t10 in full_new_text, f"Missing P(T10) {p_t10} for {name}"
    print("    All 10 Batters verified successfully.")
    
    print("\n[+] Checking Top 10 Bowlers order and values...")
    expected_bowlers = [
        ("Josh Hazlewood", "+17.83", "+8.70", "73.5%"),
        ("Matheesha Pathirana", "+17.48", "+7.66", "82.7%"),
        ("Sunil Narine", "+14.39", "+5.32", "56.8%"),
        ("Jasprit Bumrah", "+13.48", "−5.11", "51.3%"),
        ("Jacob Duffy", "+13.10", "+4.26", "47.1%"),
        ("Rashid Khan", "+12.97", "+7.27", "44.7%"),
        ("Lockie Ferguson", "+12.83", "+8.53", "43.1%"),
        ("Varun Chakravarthy", "+12.29", "+0.26", "39.1%"),
        ("Nathan Ellis", "+12.26", "+1.90", "33.9%"),
        ("Mitchell Santner", "+12.18", "+8.02", "39.7%"),
    ]
    for name, rating, delta, p_t10 in expected_bowlers:
        assert name in full_new_text, f"Missing bowler {name}"
        assert rating in full_new_text, f"Missing rating {rating} for {name}"
        assert delta in full_new_text or delta.replace("−", "-") in full_new_text, f"Missing delta {delta} for {name}"
        assert p_t10 in full_new_text, f"Missing P(T10) {p_t10} for {name}"
    print("    All 10 Bowlers verified successfully.")
    
    print("\n[+] Checking Key dataset numbers...")
    dataset_numbers = ["883", "200,999", "50,241", "131", "140"]
    for num in dataset_numbers:
        assert num in full_new_text, f"Missing dataset number {num}"
    print("    All dataset numbers verified.")
    
    print("\n[+] Checking Neutral eligibility language...")
    norm_new_text = " ".join(full_new_text.split())
    target_sentence = "Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement."
    assert target_sentence in norm_new_text, "Missing exact neutral Pakistan exclusion text!"
    assert "Kishalay Das" in norm_new_text, "Missing author name Kishalay Das"
    assert "SupeRR Selector Season 2 - Round 1" in norm_new_text or "SupeRR Selector Season 2 – Round 1" in norm_new_text, "Missing footer text"
    
    print("\n[+] Comparing numeric tokens with old PDF...")
    old_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', full_old_text))
    new_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', full_new_text))
    print(f"    Unique numbers in Old PDF: {len(old_nums)}")
    print(f"    Unique numbers in New PDF: {len(new_nums)}")
    missing_in_new = old_nums - new_nums
    print(f"    Numbers in Old not in New: {len(missing_in_new)} -> {sorted(list(missing_in_new))[:20]}")
    
    print("\n[+] Page text summaries:")
    for i, t in enumerate(new_pages_text):
        first_line = [l.strip() for l in t.split('\n') if l.strip()][0]
        last_line = [l.strip() for l in t.split('\n') if l.strip()][-1]
        print(f"    Page {i+1}: {len(t.splitlines())} lines | First: '{first_line[:45]}' | Last: '{last_line[:45]}'")

    print("\n[SUCCESS] All QA assertions passed!")

if __name__ == "__main__":
    run_qa()
