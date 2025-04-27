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
20-Apr-2025, 21-Apr-2025, added Resume feedback
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

import shutil
print("✅ Tesseract path (should NOT be None):", shutil.which("tesseract"))

# Specify the path to the Tesseract binary
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

try:
    tesseract_version = pytesseract.get_tesseract_version()
    print(f"Tesseract Version: {tesseract_version}")
except Exception as e:
    print(f"Error: Tesseract is not installed or not accessible. {str(e)}")
    
# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Explicitly set Tesseract's path to the correct location (adjust path if needed)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Path for Linux (Render)

# Predefined key skills
skills_list = [
    "Python", "Machine Learning", "Artificial Intelligence", "Angular", "Natural Language Processing",
    "AWS", "Git"
]

# Abbreviations normalization map
skill_aliases = {
    "js": "JavaScript",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "sql db": "SQL"
}

soft_skills = [
    "Teamwork", "Communication", "Leadership"
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
    
    #all_tech = set(skills_list + custom_skills + dynamic_keywords)
    #all_soft = set(soft_skills + custom_soft_skills)

    all_tech = set([normalize_skill(s).lower().strip() for s in skills_list + custom_skills + dynamic_keywords])
    all_soft = set([s.lower().strip() for s in soft_skills + custom_soft_skills])

    tech_matches = fuzzy_match_skills(text, all_tech)
    soft_matches = fuzzy_match_skills(text, all_soft)

    #return sorted(tech_matches), sorted(soft_matches)
    return sorted([s.title() for s in tech_matches]), sorted([s.title() for s in soft_matches])

def compare_resume_to_job(resume_text, job_text, years_of_experience, custom_skills=[], custom_soft_skills=[]):
    resume_tech, resume_soft = extract_skills(resume_text, job_text, custom_skills, custom_soft_skills)
    job_tech, job_soft = extract_skills(job_text)

    total = set(job_tech + job_soft)
    matched = set(resume_tech + resume_soft).intersection(total)
    missing_skills = total - matched

    score = (len(matched) / len(total)) * 100 if total else 0
    #return round(score, 2), sorted(matched)

    # Extra analyses
    length_info = analyze_resume_length(resume_text)
    verbs_used, verb_count = extract_action_verbs(resume_text)
    
    feedback = generate_resume_feedback(length_info["word_count"], verb_count, years_of_experience)

    return {
        "score": round(score, 2),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing_skills),
        "total_required": len(total),
        "total_matched": len(matched),
        #"resume_skills": sorted(set(resume_tech + resume_soft)),
        #"required_skills": sorted(total),
        #"word_count": length_info["word_count"],
        #"paragraph_count": length_info["paragraph_count"],
        #"action_verbs_used": verbs_used,
        #"action_verb_count": verb_count,
        "feedback": feedback
        }

# Experience in years → Recommended word count range
experience_ranges = [
    (0, 2, (250, 500)),     # Freshers
    (3, 7, (350, 800)),     # Early career
    (8, 15, (500, 1200)),   # Mid-career
    (16, 25, (700, 1500)),  # Senior
    (26, 75, (900, 1700)),  # Executive
]

def analyze_resume_length(resume_text):
    words = resume_text.split()
    paragraphs = [p for p in resume_text.split("\n") if p.strip()]
    return {
        "word_count": len(words),
        "paragraph_count": len(paragraphs)
    }

action_verbs = [
    "developed", "led", "managed", "designed", "implemented", "created", "initiated",
    "analyzed", "built", "increased", "reduced", "solved", "engineered", "launched",
    "improved", "organized", "collaborated", "coordinated", "executed", "delivered"
]

def extract_action_verbs(resume_text):
    words = re.findall(r'\b\w+\b', resume_text.lower())
    verbs_used = [verb for verb in action_verbs if verb in words]
    return sorted(set(verbs_used)), len(verbs_used)

def generate_resume_feedback(word_count, verb_count, years_of_experience):
    feedback = []

    # Determine appropriate range
    ideal_min, ideal_max = 500, 900  # default
    for min_exp, max_exp, (min_words, max_words) in experience_ranges:
        if min_exp <= years_of_experience <= max_exp:
            ideal_min, ideal_max = min_words, max_words
            break

    # Length feedback
    if word_count < ideal_min:
        feedback.append(f"📄 The resume may be too short for {years_of_experience} years of experience. Consider expanding with more achievements.")
    elif word_count > ideal_max:
        feedback.append(f"📝 The resume is quite long for {years_of_experience} years of experience. Consider trimming older or less relevant content.")
    else:
        feedback.append("✅ Resume length looks appropriate for your experience level.")

    # Verb usage feedback
    if verb_count < 5:
        feedback.append("⚠️ Very few action verbs detected. Use strong verbs like 'developed', 'managed', or 'led' to highlight accomplishments.")
    elif verb_count < 10:
        feedback.append("👍 Moderate use of action verbs. Adding more impactful verbs could improve readability.")
    else:
        feedback.append("✅ Great use of action verbs to describe achievements.")

    return feedback


### Testing manually ###

#job_text = """Looking for a candidate with skills in Python, Machine Learning, AI, communication, and project management."""

"""
# Define your folder and file name
folder = "Resume"
filename = "Sample-Resume.txt" # try with .pdf, .docx, .txt, .png etc.
#Sample-Resume.txt
#Gokul_Venkatesan.PDF

# Combine them into a full path
resume_path = os.path.join(folder, filename)
resume_text = extract_resume_text(resume_path)
resume_text = resume_text[0]

emails, phones = extract_contact_info(resume_text)
print(emails, phones)

extracted_skills = extract_skills(resume_text)
print("Extracted Skills: ", extracted_skills)

match_score, matched_skills = compare_resume_to_job(resume_text, job_text)
print(f"Match Score: {match_score}%")
print("Matched Skills: ", matched_skills)
"""
"""
print("\n📄 Extracted Resume Text (preview):")
print(resume_text[:1000])
print("\n📧 Emails: ", emails)
print("📱 Phone Numbers: ", phones)
"""

