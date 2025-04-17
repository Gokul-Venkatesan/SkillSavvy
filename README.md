# SkillSavvy - Resume Analyzer

A smart resume analyzer that combines **Python (FastAPI)**, **NLP**, and **Angular** to parse and evaluate resumes against job descriptions. Built to support various file types, including images, and intelligently extract key information using OCR and fuzzy matching.
---
## 🚀 Features

- 📧 Extracts **emails**, **phone numbers**, **technical skills**, and **soft skills**
- 📄 Supports multiple formats: `.txt`, `.pdf`, `.docx`, `.jpg`, `.png`
- 🖼️ Detects **image quality** via OCR confidence score; skips low-quality inputs
- 🧠 Uses **fuzzy logic** to match resumes against job descriptions
- ⚙️ Interactive **Angular frontend** with file upload, dynamic forms, and real-time feedback
---
## 🧠 Tech Stack
**Backend**  
- Python, FastAPI  
- NLP: spaCy, PhraseMatcher  
- OCR: Tesseract, pdfplumber, python-docx  
- Fuzzy Matching: RapidFuzz  
- Regex, phonenumbers

**Frontend**  
- Angular 16 (Standalone Components)  
- File upload, skill input, match score display
---

## 🧪 Sample Use Case

1. Upload your resume (`.pdf`, `.docx`, or image)
2. Paste a job description
3. View extracted:
   - 📬 Contact Info (Email, Phone)
   - 🧑‍💻 Technical & Soft Skills
   - 📊 Match Score (%)
   - 🖼️ OCR Confidence (for image inputs)
4. If the image quality is poor, the app will skip it and provide feedback
---
## 📁 Project Structure

```bash
├── backend/
│   ├── main.py            # FastAPI endpoints
│   ├── model.py           # NLP, OCR, skill extraction logic
│   └── requirements.txt   # Python dependencies
├── frontend/
│   └── [Angular code here]
└── README.md
 
⚠️ Challenges Tackled
•	🖼️ Handling low-quality image inputs with OCR confidence
•	🔍 Extracting and matching abbreviations or alternate spellings
•	📄 Consistent parsing across diverse file formats
•	💡 Skill synonym matching using fuzzy logic
________________________________________
💡 Motivation & Learning
This was a hands-on learning journey combining several advanced technologies:
•	🔍 Accurate text extraction from PDFs, Word files, and images
•	📌 Skill extraction using PhraseMatcher and fuzzy logic
•	🖼️ OCR quality control with confidence-based filtering
•	⚙️ Real-time matching logic with RapidFuzz
•	🌐 Built and connected a modern front-end using Angular standalone components

🛠️ Setup & Installation
Backend
bash
CopyEdit
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Frontend
npm install
ng serve
