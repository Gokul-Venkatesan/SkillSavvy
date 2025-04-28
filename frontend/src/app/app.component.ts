
//Gokul - 15th and 16th Apr 2025, UI to capture custom skills, Job post and resume upload
  //to compare the skills and produce match score.
  //Played around with UI to bring it more easy to view
//Gokul, 20-Apr-2025, 21-Apr-2025, added Resume feedback and loading message
//Gokul, 22-Apr to 23-Apr - File upload restriction, SSL enaled, RWD enabled, Improvised parsing
// Identified a major issue in skills capture utilization & fixed
// Added Env variable, 26-Apr-2025

import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Injectable } from '@angular/core';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, HttpClientModule, CommonModule, RouterModule],
  templateUrl: './app.component.html',
})

//const protocol = window.location.protocol; // 'https:' or 'http:'
//const port = protocol === 'https:' ? '8001' : '8000';
//const url = `${protocol}//localhost:${port}/analyze-resume`;

export class AppComponent {
  title = 'SkillSavvy - AI-Powered Resume Analyzer'; 
  resumeFile: File | null = null;
  jobDescription: string = '';
  skillsList: string = '';
  softSkills: string = '';
  result: any = null;
  experienceYears: number = 5;
  isLoading: boolean = false;
  selectedFileName: string = 'No file selected';
   
  constructor(private http: HttpClient) { }

  onExperienceInput(event: any) {
    let value = event.target.value;

    if (value.length < 1) {
      event.target.value = 5
    }

    if (value.length > 2) {
      value = value.slice(0, 2);
      event.target.value = value;
    }

    const num = parseInt(value, 10);
    if (num > 75) {
      this.experienceYears = 75;
    } else {
      this.experienceYears = isNaN(num) ? 5 : num;
    }
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];

    if (file) {
      this.selectedFileName = file.name;
    } else {
      this.selectedFileName = 'No file selected';
    }

    if (!file) {
      // ✅ User cleared file input
      this.resumeFile = null;
      return;
    }

    const maxSizeMB = 2;

    if (file && file.size > maxSizeMB * 1024 * 1024) {
      alert(`❌ Your file is too large. The maximum file size allowed is ${maxSizeMB} MB. Please upload a smaller file.`);
      this.resumeFile = null;
      return;
    }

    const allowedExtensions = ['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    if (!fileExtension || !allowedExtensions.includes(fileExtension)) {
      alert('❌ Sorry, the file format is unsupported. Please upload a file in one of these formats: PDF, DOCX, TXT, JPG or PNG');
      this.resumeFile = null;
      return;
    }

    this.resumeFile = file;
  }

  analyzeResume() {
    this.result = null;

    if (!this.resumeFile) {
      alert('⚠️ Please upload a valid file. Ensure the file is in an acceptable format and meets the size requirements');
      return;
    }

    if (this.jobDescription.length > 1000 ||
      this.skillsList.length > 1000 ||
      this.softSkills.length > 1000) {
      alert('⚠️ Text inputs must be 1000 characters or less. Please reduce the length of your text.');
      return;
    }

    if (this.experienceYears < 1 || this.experienceYears > 75) {
      alert('⚠️ Please enter a valid experience between 1 and 75 years.');
      return;
    }

    const formData = new FormData();
    formData.append('resume_file', this.resumeFile, this.resumeFile.name);
    formData.append('job_description', this.jobDescription);
    formData.append('skills_list', this.skillsList);
    formData.append('soft_skills', this.softSkills);
    formData.append('years_of_experience', this.experienceYears.toString());

    this.isLoading = true;
    
    this.http.post(`${environment.apiUrl}/analyze-resume`, formData).subscribe({
      next: (data) => {
        this.result = data;
        this.isLoading = false;
        console.log('Analysis result:', data);
      },
      error: (error) => {
        console.error('Error analyzing resume:', error);
        this.isLoading = false;

        if (error.status === 429) {
          alert(error.error?.detail || 'You have exceeded the rate limit. Please try again later');
        } else {
          alert('Oops! Something went wrong. Please try again.');
        }
      }
    });
  }

}
