"""

The goal of this program is to extract information like Phone number, Email, Skills from resume and match with Job description to analyze the best fit.
Input source can be in Text, Word, PDF or scanned images (Jpg or Png)

Working concept using Machine Learning - NLP & OCR

Objective: By analyzing resume and job post, the program can analyze whether candidate can be a best fit for the open position.

Gokul - 7-Apr-2025, created the basics for text, word and PDF as part of learning.
11-Apr-2025, optimized the extraction.
12-Apr-2025, added OCR for Image
15-Apr-2025, Finalized with score part
16-Apr-2025, Added OCR quality and confidence
"""

import os # interact with the operating system. folders, file paths
import re # for Regular Expressions — used for pattern matching in strings

import pdfplumber # Used to extract text, tables, and metadata from PDF file
from docx import Document # From the python-docx package, to read and write .docx Word documents
from PIL import Image # From the Pillow library for Images

import phonenumbers #  for parsing, formatting, and validating international phone numbers, Based on Google’s libphonenumber library.

import spacy # for natural language processing
from spacy.matcher import PhraseMatcher # for spotting key skills or terms in resumes or job descriptions.

import pytesseract # OCR (Optical Character Recognition) tool
from rapidfuzz import fuzz # fast string matching library for fuzzy matching and comparison

import json

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Provide the tesseract executable location explicitly
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Predefined key skills
skills_list = [
    "Python", "Java", "JavaScript", "C++", "SQL", "Machine Learning", "Data Analysis", "Deep Learning",
    "Artificial Intelligence", "Angular", 
    "Project Management", "Teamwork", "Communication", "Leadership", "Problem Solving", "Agile",
    "Cloud Computing", "AWS", "Azure", "React", "Node.js", "Git", "Docker", "Excel", "Tableau"
]

# Abbreviations normalization map
skill_aliases = {
    "js": "JavaScript",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "sql db": "SQL",
    "nlp": "Natural Language Processing"
}

soft_skills = [
    "Teamwork", "Communication", "Leadership", "Problem Solving", "Time Management", "Creativity",
    "Adaptability", "Critical Thinking", "Decision Making"
]

# Convert to lowercase for better matching
skills_list = [skill.lower() for skill in skills_list]

# Create PhraseMatcher with custom skills
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp(skill.lower()) for skill in skills_list]
matcher.add("SKILLS", patterns)

# -------- File Parsing --------

# --- Extract from PDF ---
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return " ".join([page.extract_text() or "" for page in pdf.pages])

# --- Extract from DOCX ---
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# --- Extract from TXT ---
def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()

# --- Extract from Image (OCR) ---
#def extract_text_from_image(image_path):
#    image = Image.open(image_path)
#    return pytesseract.image_to_string(image)

# With confidence level to determine the quality of image

def extract_text_from_image(image_path):
    image = Image.open(image_path)

    # Run OCR with detailed output (for confidence evaluation)
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    # Collect confidence values, safely converting to integers and ignoring bad/confidence -1 values
    confidences = []
    for conf in ocr_data['conf']:
        try:
            conf_val = int(conf)
            if conf_val > 0:  # Ignore -1 and 0 confidence
                confidences.append(conf_val)
        except (ValueError, TypeError):
            continue

    average_conf = sum(confidences) / len(confidences) if confidences else 0

    # Get plain OCR text output
    text = pytesseract.image_to_string(image)

    # Evaluate quality based on average confidence
    quality = 'good' if average_conf >= 60 else 'poor'
    message = '' if quality == 'good' else 'The uploaded image appears to be of low quality. Please upload a clearer image.'

    return json.dumps({
        'text': text.strip(),
        'quality': quality,
        'confidence': round(average_conf, 2),
        'message': message
    })

# --- Unified Resume Extractor ---
def extract_resume_text(file_path):
    file_path = file_path.lower()

    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path), None
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path), None
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path), None
    elif file_path.endswith((".png",".jpg", ".jpeg")):
        #return extract_text_from_image(file_path)
        image_data_json = extract_text_from_image(file_path)
        image_data = json.loads(image_data_json)
        return image_data.get("text", ""), image_data
    else:
        raise ValueError("Unsupported file format. Please upload PDF, DOCX, TXT, or an image.")
    
# --- Email and Phone Extractor ---
def extract_contact_info(text):

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' #RegEx
    
    #phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}' # US Pattern
    #indian_mobile_pattern = r'\b(?:\+91[-\s]?|0)?[7-9]\d{9}\b' # India

    #phone_pattern = r'\b(?:\+?\d{1,4}[-.\s]?)?(?:\(?\d{2,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}\b' #Universal Pattern for complete number ##
    #phones = re.findall(phone_pattern, text) #With above pattern ##
    #Reconstruct full phone numbers from groups
    #cleaned_phones = ["".join(groups) for groups in phones if any(groups)] ##


    emails = re.findall(email_pattern, text)
    phones = extract_valid_phone_numbers(text)
    
    return list(set(emails)), list(set(phones))

#  more accurate than trying to extract phone numbers with regex
def extract_valid_phone_numbers(text):
    valid_numbers = set()
    
    #PhoneNumberMatcher matches all phone numbers, regardless of region
    for match in phonenumbers.PhoneNumberMatcher(text, None):  # No region specified
        number = match.number
        if phonenumbers.is_valid_number(number):  # Check if the number is valid
            formatted_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            valid_numbers.add(formatted_number)

    return list(valid_numbers)

def normalize_skill(word):
    #word = word.lower()
    return skill_aliases.get(word.lower(), word)

def normalize_text(text):
    text = text.lower()
    for alias, full_form in skill_aliases.items():
        # Improved regex to match alias even if surrounded by punctuation or spaces
        pattern = rf'(?<!\w){re.escape(alias.lower())}(?!\w)'
        text = re.sub(pattern, full_form.lower(), text)
    return text

def fuzzy_match_skills(text, skill_list, threshold=85):
    found = set()
    text_normalized = normalize_text(text)
    
    for skill in skill_list:
        normalized_skill = normalize_skill(skill)
        # Use fuzz.partial_ratio for more lenient matching
        ratio = fuzz.partial_ratio(normalized_skill, text_normalized)
        if ratio >= threshold:
            # Store matched skill in title case to avoid duplicates like 'communication' and 'Communication'
            found.add(normalized_skill.title())

    return found

# -------- Dynamic Keyword Extraction --------
def extract_keywords_from_job(job_text):
    doc = nlp(job_text)
    return list({
        chunk.text.strip().lower()
        for chunk in doc.noun_chunks
        if 2 <= len(chunk.text.strip()) <= 40
    })

# -------- Combined Skill Extraction --------
def extract_skills(text, job_desc=None, custom_skills=[], custom_soft_skills=[]):
    dynamic_keywords = extract_keywords_from_job(job_desc) if job_desc else []
    
    all_tech = set(skills_list + custom_skills + dynamic_keywords)
    all_soft = set(soft_skills + custom_soft_skills)

    tech_matches = fuzzy_match_skills(text, all_tech)
    soft_matches = fuzzy_match_skills(text, all_soft)

    return sorted(tech_matches), sorted(soft_matches)

def compare_resume_to_job(resume_text, job_text, custom_skills=[], custom_soft_skills=[]):
    resume_tech, resume_soft = extract_skills(resume_text, job_text, custom_skills, custom_soft_skills)
    job_tech, job_soft = extract_skills(job_text)

    total = set(job_tech + job_soft)
    matched = set(resume_tech + resume_soft).intersection(total)

    score = (len(matched) / len(total)) * 100 if total else 0
    return round(score, 2), sorted(matched)

# Define your folder and file name
#folder = "Resume"
#filename = "Sample-Resume.txt" # try with .pdf, .docx, .txt, .png etc.

#job_text = """Looking for a candidate with skills in Python, Machine Learning, AI, communication, and project management."""

# Combine them into a full path
#resume_path = os.path.join(folder, filename)
#resume_text = extract_resume_text(resume_path)

#emails, phones = extract_contact_info(resume_text)

#extracted_skills = extract_skills(resume_text)
#print("Extracted Skills: ", extracted_skills)

#match_score, matched_skills = compare_resume_to_job(resume_text, job_text)
#print(f"Match Score: {match_score}%")
#print("Matched Skills: ", matched_skills)

#print("✅ model.py loaded")

"""
print("\n📄 Extracted Resume Text (preview):")
print(resume_text[:1000])
print("\n📧 Emails: ", emails)
print("📱 Phone Numbers: ", phones)
"""

