"""

The goal of this API is to call the extract skills that will extract information like Phone number, Email, Skills from resume and match with Job description
to analyze the best fit. Input source can be in Text, Word, PDF or scanned images (Jpg or Png)

Objective: By analyzing resume and job post, the program can analyze whether candidate can be a best fit for the open position.

Gokul - 15-Apr-2025, created API call using FastAPI to call the model
16-Apr-2025, added OCR confidence & quality
20-Apr-2025, 21-Apr-2025, added Resume feedback
22-Apr to 23-Apr - File upload restriction, SSL enaled, Improvised parsing, Identified a major issue in skills capture utilization & fixed
UUID & Rate limit for API implementation
26-Apr-2025, added ENV variable
"""

import os
import uuid
import tempfile

from fastapi import FastAPI, UploadFile, File, Form, Request # main class used to create your API app
from pydantic import BaseModel # Pydantic is a data validation library used heavily in FastAPI
from typing import List, Optional # Python standard typing features

from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from slowapi.util import get_remote_address

import model  # full import so we can access all functions
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

#Initiate FastAPI
app = FastAPI()

# Determine which environment to load
ENV = os.getenv("ENVIRONMENT", "development")  # Default to 'development' if not set
env_file = "dev.env" if ENV == "development" else "prod.env"

#print(f"Loading .env file: {env_file}")  # Debug print
load_dotenv(dotenv_path=env_file)

#ENV = os.getenv("ENVIRONMENT")
API_URL = os.getenv("API_URL")

#print(f"ENVIRONMENT is: {ENV}")
#print(f"API_URL is: {API_URL}")
#print(f"Current working directory: {os.getcwd()}")

if ENV == "production":
        app.add_middleware(
        CORSMiddleware,
        origins = API_URL,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        #allow_origins=["https://localhost:55397/"],  # Angular default dev port
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

limiter = Limiter(key_func=get_remote_address)  # Use IP address for limiting

# Add rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def ratelimit_error(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "You have exceeded the rate limit. Please try again later"}
    )

# Apply the limiter to FastAPI app
app.state.limiter = limiter

# Default values for job description, skills, and soft skills
DEFAULT_JOB_DESCRIPTION = "Looking for a candidate with skills in Python, Machine Learning, AI, nlp, and project management."
DEFAULT_SKILLS_LIST = "Python, Machine Learning, Artificial Intelligence, Angular, AWS, Git, NLP"
DEFAULT_SOFT_SKILLS = "Teamwork, Communication, Leadership"
DEFAULT_EXPERIENCE_YEARS = 10  # Default value for years of experience

class ResumeMatchResponse(BaseModel):
    emails: List[str]
    phone_numbers: List[str]
    tech_skills: List[str]
    soft_skills: List[str]
    match_score: Optional[float] = None
    matched_skills: Optional[List[str]] = []
    missing_skills: Optional[List[str]] = []
    total_required: Optional[int] = None
    total_matched: Optional[int] = None
    feedback: Optional[List[str]] = []
    image_quality: Optional[str] = None
    ocr_confidence: Optional[float] = None
    ocr_message: Optional[str] = None

#class CustomSkillInput(BaseModel):
#    skills_list: Optional[List[str]] = []
#    soft_skills: Optional[List[str]] = []

# Define your folder and file
folder = "Resume"
filename = "Sample-Resume.txt" # try with .pdf, .docx, .txt, .png etc.

# Combine them into a full path
file_path = os.path.join(folder, filename)

#job_text = "Looking for a candidate with skills in Python, Machine Learning, AI, nlp, and project management."

#async def optional_file_dependency(resume_file: Optional[UploadFile] = File(default=None)):
#    return resume_file

@app.post("/analyze-resume", response_model=ResumeMatchResponse)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def analyze_resume(
    request: Request,  # ✅ Required by slowapi to extract IP
    resume_file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    skills_list: Optional[str] = Form(None),  # comma-separated
    soft_skills: Optional[str] = Form(None),   # comma-separated
    years_of_experience: Optional[int] = Form(DEFAULT_EXPERIENCE_YEARS)  # Defaulting to 10 if not provided
):

    # Fallback to default values if inputs are not provided
    job_description = job_description or DEFAULT_JOB_DESCRIPTION
    skills_list = skills_list or DEFAULT_SKILLS_LIST
    soft_skills = soft_skills or DEFAULT_SOFT_SKILLS

    #resume_text = model.extract_skills(resume_file)
    #if job_description == "":
    #    job_description = job_text
    #else:
    #    job_description = job_text + " Please add these skills too - " + job_description
    
    #If file is uploaded, save it temporarily and extract text
    if resume_file is None:
        # If no file is uploaded, fallback to sample resume
        if not os.path.exists(file_path):
            return {"detail": f"Sample resume file not found at {resume_path}"}
        resume_text, image_meta = model.extract_resume_text(file_path)
    else:
        contents = await resume_file.read()

        #file_path = f"temp_{resume_file.filename}" #To change to UUID, below 4 lines added
        
        # Create a secure temporary file with UUID in system temp dir
        file_ext = os.path.splitext(resume_file.filename)[1]  # Preserve the original extension
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        # Run your model logic
        resume_text, image_meta = model.extract_resume_text(file_path)

        # Clean up
        os.remove(file_path)
   
    emails, phones = model.extract_contact_info(resume_text)
    
    # Split comma-separated skills and soft skills lists
    user_skills = skills_list.split(",") if skills_list else []
    user_soft_skills = soft_skills.split(",") if soft_skills else []

    tech_skills_found, soft_skills_found = model.extract_skills(
        resume_text, job_desc=job_description, custom_skills=user_skills, custom_soft_skills=user_soft_skills
    )

    match_score = None
    matched_skills = []
    missing_skills = []
    total_required = None
    total_matched = None
    feedback = []

    
    if job_description:
        #match_score, matched_skills, missing_skills, total_required, total_matched, feedback = model.compare_resume_to_job(
        #    resume_text, job_description, years_of_experience, custom_skills=user_skills, custom_soft_skills=user_soft_skills

        if skills_list or soft_skills:
            job_description += "\n\nAlso focus on these skills:\n"
            if skills_list:
                job_description += skills_list + "\n"
            if soft_skills:
                job_description += soft_skills

        result_data = model.compare_resume_to_job(
        resume_text, job_description, years_of_experience,
        custom_skills=user_skills, custom_soft_skills=user_soft_skills
        )

        match_score = result_data["score"]
        matched_skills = result_data["matched_skills"]
        missing_skills = result_data["missing_skills"]
        total_required = result_data["total_required"]
        total_matched = result_data["total_matched"]
        feedback = result_data["feedback"]

    return ResumeMatchResponse(
        emails=emails,
        phone_numbers=phones,
        tech_skills=tech_skills_found,
        soft_skills=soft_skills_found,
        match_score=match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        total_required=total_required,
        total_matched=total_matched,
        feedback=feedback,
        image_quality=image_meta.get("quality") if image_meta else None,
        ocr_confidence=image_meta.get("confidence") if image_meta else None,
        ocr_message=image_meta.get("message") if image_meta else None
    )

"""
@app.get("/health")
def health_check():
    return {"status": "Resume analyzer API is running 🚀"}
"""
