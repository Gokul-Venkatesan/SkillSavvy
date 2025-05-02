📄 Resume Analyzer Tool
A smart resume analyzer that blends Python (FastAPI), Natural Language Processing (NLP), and Angular to parse and assess resumes against job descriptions. It supports multiple file formats, including images, and uses OCR and fuzzy matching to intelligently extract and compare key information.
Beyond parsing, the tool gives detailed feedback on your resume — evaluating its length in relation to your experience, analyzing your use of action verbs and key nouns, and providing skill alignment suggestions.
It also enables real-time job matching using fuzzy skill logic, helping users tailor their resumes more effectively. The responsive web design (RWD) ensures smooth usage across all devices.
🔒 Security
Basic security features are implemented, including:
•	SSL (HTTPS)
•	File size limits (max 2MB)
•	API rate limiting (via slowapi)
•	UUID-based file paths to maintain privacy
________________________________________
🚀 Features
•	📧 Extracts emails, phone numbers, technical, and soft skills
•	📄 Supports .txt, .pdf, .docx, .jpg, .png formats
•	🖼️ Analyzes image quality using OCR confidence scores
•	🧠 Performs fuzzy logic-based resume-to-job matching
•	⚙️ Angular frontend with real-time feedback and interactive file upload
•	📝 Provides resume feedback relative to your experience
•	📁 Handles **multiple files** simultaneously and processes them all  
•	📤 **Exports analyzed results to Excel**  
•	📐 **Checks resume formatting** before processing  
•	🎨 Enhanced **CSS styling**, replacing inline styles for better maintainability
________________________________________
🧠 Tech Stack
🔧 Backend
•	Python, FastAPI, SlowAPI (rate limiting)
•	NLP: spaCy, PhraseMatcher
•	OCR: Tesseract (pytesseract), pdfplumber, python-docx
•	Fuzzy Matching: rapidfuzz
•	Regex, phonenumbers, uuid
💻 Frontend
•	Angular 16 (Standalone Components)
•	Dynamic file upload, skill input, and match score display	
•	Grid layout with scrollable view similar to Excel  
•	Optimized views for **mobile and desktop**  
________________________________________
🧪 Sample Use Case
1.	Upload your resume (.pdf, .docx, or image file) — now supports **multiple files**
2.	Paste a job description or manually enter skills
3.	Review extracted details:
o	📬 Email & phone number
o	🧑‍💻 Technical and soft skills
o	📊 Match score (%)
o	🖼️ OCR confidence level (for image-based resumes)
o	✅ Matched & ❌ Missing skills
o	📝 Feedback on resume length, action verbs, and key noun usage
4.	If image quality is low, the system will skip it and notify you
5.	Export the result to **Excel for further analysis**
________________________________________
📁 Project Structure
├── backend/
│   ├── main.py            # FastAPI routes and endpoints
│   ├── model.py           # Core logic for NLP, OCR, skill extraction
│   └── requirements.txt   # Backend Python dependencies
├── frontend/
│   └── [Angular source code]
└── README.md
________________________________________
⚠️ Challenges Tackled
•	🖼️ Dealing with low-quality image inputs using OCR confidence scoring
•	🔍 Matching abbreviations and alternate spellings
•	📄 Consistent parsing across varied formats
•	💡 Synonym and fuzzy skill matching
•	🔒 Enforcing rate limiting to protect the API from abuse
•	🌐 Enabling SSL (HTTPS) for secure communication
•	📁 Handling **multiple file uploads and batch processing**  
•	📐 Implementing **resume formatting checks**  
•	🧾 Supporting **Excel-style UI with grid scrolling**  
•	📱 Improving **UX for both mobile and desktop views**  
________________________________________
💡 Motivation & Learning
This project was a deep dive into integrating multiple technologies:
•	🔍 Accurate extraction from PDFs, DOCX, and images
•	📌 Skill matching using spaCy’s PhraseMatcher and rapidfuzz
•	🖼️ OCR validation via confidence thresholds
•	⚙️ Real-time fuzzy logic scoring
•	🌐 Building a modern Angular frontend with Standalone Components
•	🌐 Creating a responsive Angular frontend using standalone components
•	🔐 Implementing rate limiting (via slowapi) and HTTPS for basic API security
•	📤 Managing **multiple resume inputs** and **Excel export logic**  
•	🎨 Deepening knowledge of **CSS layouts** and handling **scrollable grids**  
•	📱 Enhancing UI/UX for **cross-platform usability** (Windows, Mobile)

🛠️ Setup & Installation
🔧 Backend
bash
CopyEdit
cd backend
pip install -r requirements.txt

🌱 Environment Setup
Create two environment files:
•	dev.env:
env
CopyEdit
ENVIRONMENT=development
API_URL=http://localhost:8000
•	prod.env:
env
CopyEdit
ENVIRONMENT=production
API_URL=https://yourdomain.com
✅ Tip: Use a library like python-dotenv to load environment variables automatically from these files.

▶️ Run the API
Development
bash
CopyEdit
uvicorn main:app --reload
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Production
bash
CopyEdit
uvicorn main:app --host 0.0.0.0 --port 8000 \
  --ssl-keyfile=certs/server.key \
  --ssl-certfile=certs/server.crt
✅ Important: For production, always serve the API behind an HTTPS-enabled reverse proxy.

🔐 Generating SSL Certificate with OpenSSL (for local HTTPS)

💻 Frontend
bash
CopyEdit
npm install
npm install xlsx
ng serve
# or for local HTTPS
ng serve --ssl true --ssl-key certs/server.key --ssl-cert certs/server.crt
🌐 Ensure the frontend accesses the backend via https://localhost:8000 or your configured domain.
