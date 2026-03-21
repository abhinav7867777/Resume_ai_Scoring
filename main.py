# ============================================================
# main.py — Resume Analyzer
# Original code ki tarah hi hai — sirf better HTML template
# PDF Upload → Text Extract → OpenRouter AI → Results
# ============================================================

from doctest import debug

from flask import Flask, request, render_template
import fitz  # PyMuPDF — PDF text extract karta hai
from analyse_pdf import analyse_resume_gemini
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ── PDF se text nikalna (same as original) ──
def extract_text_from_resume(pdf_path):
    """
    PyMuPDF (fitz) use karke PDF ka text extract karta hai.
    Har page ka text leke ek saath return karta hai.
    """
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


# ── Main Route ──
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume_file     = request.files.get("resume")
        job_description = request.form.get("job_description", "").strip()

        # Validation
        if not resume_file or not resume_file.filename.endswith(".pdf"):
            return render_template("index.html",
                result=None,
                error="Please upload a valid PDF file.")

        if not job_description:
            return render_template("index.html",
                result=None,
                error="Please enter the job description.")

        # PDF save karo
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
        resume_file.save(pdf_path)

        # PDF se text nikalo
        resume_content = extract_text_from_resume(pdf_path)

        if not resume_content.strip():
            return render_template("index.html",
                result=None,
                error="PDF mein text nahi mila. Scanned PDF try mat karo.")

        # OpenRouter AI se analyze karao
        result = analyse_resume_gemini(resume_content, job_description)

        # Uploaded file ka naam bhi bhejo
        filename = resume_file.filename

        return render_template("index.html",
            result=result,
            filename=filename,
            error=None)

    return render_template("index.html", result=None, error=None)


if __name__ == "__main__":
    print("=" * 50)
    print("  Resume Analyzer — OpenRouter API")
    print("  URL: http://localhost:5000")
    print("  Model: nvidia/nemotron-3-super-120b-a12b:free")
    print("=" * 50)
    app.run(debug=True)