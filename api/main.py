"""

The goal of this API is to call the extract skills that will extract information like Phone number, Email, Skills from resume and match with Job description
to analyze the best fit. Input source can be in Text, Word, PDF or scanned images (Jpg or Png)

Objective: By analyzing resume and job post, the program can analyze whether candidate can be a best fit for the open position.

Gokul - 15-Apr-2025, created API call using FastAPI to call the model
16-Apr-2025, added OCR confidence & quality
"""

import os
from fastapi import FastAPI, UploadFile, File, Form # main class used to create your API app
from pydantic import BaseModel # Pydantic is a data validation library used heavily in FastAPI
from typing import List, Optional # Python standard typing features

from fastapi.middleware.cors import CORSMiddleware

import model  # full import so we can access all functions

#Initiate FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://127.0.0.1:55397/"],  # Angular default dev port
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeMatchResponse(BaseModel):
    emails: List[str]
    phone_numbers: List[str]
    tech_skills: List[str]
    soft_skills: List[str]
    match_score: Optional[float] = None
    matched_skills: Optional[List[str]] = []
    image_quality: Optional[str] = None
    ocr_confidence: Optional[float] = None
    ocr_message: Optional[str] = None

class CustomSkillInput(BaseModel):
    skills_list: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []

# Define your folder and file
folder = "Resume"
filename = "Sample-Resume.txt" # try with .pdf, .docx, .txt, .png etc.

# Combine them into a full path
file_path = os.path.join(folder, filename)

job_text = "Looking for a candidate with skills in Python, Machine Learning, AI, communication, and project management."

#async def optional_file_dependency(resume_file: Optional[UploadFile] = File(default=None)):
#    return resume_file

@app.post("/analyze-resume", response_model=ResumeMatchResponse)
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    skills_list: Optional[str] = Form(None),  # comma-separated
    soft_skills: Optional[str] = Form(None)   # comma-separated
):
    #resume_text = model.extract_skills(resume_file)
    if job_description == "":
        job_description = job_text
    else:
        job_description = job_text + " Please add these skills too - " + job_description
    
    #If file is uploaded, save it temporarily and extract text
    if resume_file is None:
        # If no file is uploaded, fallback to sample resume
        if not os.path.exists(file_path):
            return {"detail": f"Sample resume file not found at {resume_path}"}
        resume_text, image_meta = model.extract_resume_text(file_path)
    else:
        contents = await resume_file.read()
        file_path = f"temp_{resume_file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        resume_text, image_meta = model.extract_resume_text(file_path)
        os.remove(file_path)
   
    emails, phones = model.extract_contact_info(resume_text)
    
    user_skills = skills_list.split(",") if skills_list else []
    user_soft_skills = soft_skills.split(",") if soft_skills else []

    tech_skills_found, soft_skills_found = model.extract_skills(
        resume_text, job_desc=job_description, custom_skills=user_skills, custom_soft_skills=user_soft_skills
    )

    match_score = None
    matched_skills = []
    if job_description:
        match_score, matched_skills = model.compare_resume_to_job(
            resume_text, job_description, custom_skills=user_skills, custom_soft_skills=user_soft_skills
        )

    return ResumeMatchResponse(
        emails=emails,
        phone_numbers=phones,
        tech_skills=tech_skills_found,
        soft_skills=soft_skills_found,
        match_score=match_score,
        matched_skills=matched_skills,
        image_quality=image_meta.get("quality") if image_meta else None,
        ocr_confidence=image_meta.get("confidence") if image_meta else None,
        ocr_message=image_meta.get("message") if image_meta else None
    )
