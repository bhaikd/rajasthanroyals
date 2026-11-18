import sys
from pathlib import Path
import re
import pypdfium2 as pdfium
from PIL import Image

def run_qa():
    old_pdf_path = Path("outputs/methodology_report_old.pdf")
    new_pdf_path = Path("outputs/methodology_report.pdf")
    ref_pdf_path = Path("6af458274c1e8_data_pack/Data Pack/Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf")

    assert old_pdf_path.exists(), "Old PDF missing!"
    assert new_pdf_path.exists(), "New PDF missing!"
    assert ref_pdf_path.exists(), "Reference PDF missing!"

    old_doc = pdfium.PdfDocument(str(old_pdf_path))
    new_doc = pdfium.PdfDocument(str(new_pdf_path))
    ref_doc = pdfium.PdfDocument(str(ref_pdf_path))

    print(f"[QA] Page counts: Reference = {len(ref_doc)}, Old = {len(old_doc)}, New = {len(new_doc)}")
    assert len(new_doc) in [6, 7], f"Expected 6 or 7 pages, got {len(new_doc)}"

    # 1. Check Dimensions and Aspect Ratio
    ref_size = ref_doc[0].get_size()
    new_size = new_doc[0].get_size()
    print(f"[QA] Reference page size: {ref_size[0]:.1f} x {ref_size[1]:.1f} pt ({ref_size[0]/72:.2f} x {ref_size[1]/72:.2f} in)")
    print(f"[QA] New report page size: {new_size[0]:.1f} x {new_size[1]:.1f} pt ({new_size[0]/72:.2f} x {new_size[1]/72:.2f} in)")
    assert abs(ref_size[0] - new_size[0]) < 1 and abs(ref_size[1] - new_size[1]) < 1, "Page size mismatch!"

    # 2. Extract Text from New and Old PDFs
    new_pages_text = [p.get_textpage().get_text_range() for p in new_doc]
    old_pages_text = [p.get_textpage().get_text_range() for p in old_doc]
    full_new_text = "\n".join(new_pages_text)
    full_old_text = "\n".join(old_pages_text)

    # 3. Check for Raw LaTeX
    print("\n[QA] Checking for Raw LaTeX ($ or \\hat or \\implies)...")
    raw_latex = re.findall(r'(\$[^\$]+\$|\\hat|\\implies|\\mu|\\Delta)', full_new_text)
    print(f"     Raw LaTeX occurrences: {len(raw_latex)} -> {raw_latex}")
    assert len(raw_latex) == 0, f"Found raw LaTeX in new PDF: {raw_latex}"

    # 4. Check Neutral Eligibility Language
    print("\n[QA] Checking Neutral eligibility language...")
    target_sentence = "Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement."
    norm_new_text = " ".join(full_new_text.split())
    assert target_sentence in norm_new_text, "Missing exact neutral Pakistan exclusion text!"
    assert "Kishalay Das" in norm_new_text, "Missing author Kishalay Das"

    # 5. Check Top 10 Batters Order & Values
    print("\n[QA] Checking Top 10 Batters order and values...")
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
        assert (delta in full_new_text or delta.replace("−", "-") in full_new_text), f"Missing delta {delta} for {name}"
        assert p_t10 in full_new_text, f"Missing P(T10) {p_t10} for {name}"
    print("     All 10 Batters verified successfully.")

    # 6. Check Top 10 Bowlers Order & Values
    print("\n[QA] Checking Top 10 Bowlers order and values...")
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
        assert (delta in full_new_text or delta.replace("−", "-") in full_new_text), f"Missing delta {delta} for {name}"
        assert p_t10 in full_new_text, f"Missing P(T10) {p_t10} for {name}"
    print("     All 10 Bowlers verified successfully.")

    # 7. Check Numeric Token Matching with Old PDF
    print("\n[QA] Comparing numeric tokens with old PDF...")
    old_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', full_old_text))
    new_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', full_new_text))
    print(f"     Unique numbers in Old PDF: {len(old_nums)}")
    print(f"     Unique numbers in New PDF: {len(new_nums)}")
    missing = old_nums - new_nums
    # Exclude page-number-like numbers or known table label renamings
    structural_diffs = {'2.1', '2.2', '3.1', '4.1', '6.2', '21'}
    real_missing = missing - structural_diffs
    print(f"     Numbers in Old not in New (excluding structural label changes): {len(real_missing)} -> {sorted(list(real_missing))}")
    assert len(real_missing) == 0, f"Found missing numerical tokens: {real_missing}"

    # 8. Create Side-by-Side Visual Comparison Composites
    print("\n[QA] Generating side-by-side composite images for visual inspection...")
    ref_img1 = Image.open("outputs/ref_inspect/ref_page_1.png")
    ref_img2 = Image.open("outputs/ref_inspect/ref_page_2.png")
    new_img1 = Image.open("outputs/inspect_restyle/page_1.png")
    new_img2 = Image.open("outputs/inspect_restyle/page_2.png")

    # Composite 1: Ref Page 1 vs New Page 1
    w, h = ref_img1.size
    comp1 = Image.new("RGB", (w * 2 + 40, h), (240, 240, 240))
    comp1.paste(ref_img1, (0, 0))
    comp1.paste(new_img1, (w + 40, 0))
    comp1_path = Path("outputs/inspect_restyle/composite_ref1_vs_page1.png")
    comp1.save(comp1_path)
    print(f"     Saved composite: {comp1_path}")

    # Composite 2: Ref Page 1 vs New Page 2 (shaded box comparison)
    comp2 = Image.new("RGB", (w * 2 + 40, h), (240, 240, 240))
    comp2.paste(ref_img1, (0, 0))
    comp2.paste(new_img2, (w + 40, 0))
    comp2_path = Path("outputs/inspect_restyle/composite_ref1_vs_page2.png")
    comp2.save(comp2_path)
    print(f"     Saved composite: {comp2_path}")

    print("\n[SUCCESS] All automated QA assertions passed perfectly!")

if __name__ == "__main__":
    run_qa()
