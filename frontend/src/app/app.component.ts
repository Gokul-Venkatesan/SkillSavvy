
//Gokul - 15th and 16th Apr 2025, UI to capture custom skills, Job post and resume upload
  //to compare the skills and produce match score.
  //Played around with UI to bring it more easy to view
//Gokul, 20-Apr-2025, 21-Apr-2025, added Resume feedback and loading message
//Gokul, 22-Apr to 23-Apr - File upload restriction, SSL enaled, RWD enabled, Improvised parsing
// Identified a major issue in skills capture utilization & fixed
// Added Env variable, 26-Apr-2025
//Gokul, 29 - Apr till 02 - May - Multiple file upload, Resume format check and Export to excel.
//    More CSS workings and remove inline styles

import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Injectable } from '@angular/core';
import { environment } from '../environments/environment';
import { ExportExcelService } from './export-excel.service';

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

  //Multi File
  multiResumeFiles: File[] = [];
  multiResults: any[] = [];
  selectedMultiFileNames: string[] = [];

  constructor(
    private http: HttpClient,
    private exportService: ExportExcelService
  ) { }

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

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const dropArea = event.currentTarget as HTMLElement;
    dropArea.classList.add('dragover');
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const dropArea = event.currentTarget as HTMLElement;
    dropArea.classList.remove('dragover');
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();

    const dropArea = event.currentTarget as HTMLElement;
    dropArea.classList.remove('dragover');

    if (event.dataTransfer?.files?.length) {
      const fileInput = document.getElementById('multi-upload') as HTMLInputElement;
      const dataTransfer = new DataTransfer();

      Array.from(event.dataTransfer.files).forEach(file => {
        dataTransfer.items.add(file);
      });

      fileInput.files = dataTransfer.files;

      // Now trigger your existing file selection method
      const fakeEvent = { target: fileInput } as any;
      this.onMultipleFilesSelected(fakeEvent);
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

    // Reset the multi-file list when a single file is selected
    this.multiResumeFiles = [];
    this.selectedMultiFileNames = [];

    this.resumeFile = file;
  }

  //Mutile File Handling
  onMultipleFilesSelected(event: any) {
    const files: FileList = event.target.files;

    this.multiResumeFiles = [];
    this.selectedMultiFileNames = [];

    const maxSizeMB = 2;
    const allowedExtensions = ['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileExtension = file.name.split('.').pop()?.toLowerCase();

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

      if (!fileExtension || !allowedExtensions.includes(fileExtension)) {
        //alert(`❌ ${file.name} has an unsupported format.`);
        alert(`❌ Sorry, the file format is unsupported. Please upload a file in one of these formats: PDF, DOCX, TXT, JPG or PNG`);
        this.multiResumeFiles = [];
        this.selectedMultiFileNames = [];
        return;
      }

      if (file.size > maxSizeMB * 1024 * 1024) {
        alert(`❌ One of your file is too large.The maximum file size allowed is ${maxSizeMB} MB per file. Please upload a smaller file.`);
        this.multiResumeFiles = [];
        this.selectedMultiFileNames = [];
        return;
      }

      this.multiResumeFiles.push(file);
      this.selectedMultiFileNames.push(file.name);

      // Reset the single file selection when multiple files are chosen
      this.resumeFile = null;
      this.selectedFileName = 'No file selected';
    }
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

  //Mutile File Handling
  analyzeMultipleResumes() {
    this.multiResults = [];

    if (this.multiResumeFiles.length === 0) {
      alert('⚠️ Please upload a valid file. Ensure the file is in an acceptable format and meets the size requirements');
      return;
    }

    const formData = new FormData();
    this.multiResumeFiles.forEach(file => {
      formData.append('resume_files', file, file.name);
    });

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

    formData.append('job_description', this.jobDescription);
    formData.append('skills_list', this.skillsList);
    formData.append('soft_skills', this.softSkills);
    formData.append('years_of_experience', this.experienceYears.toString());

    this.isLoading = true;

    this.http.post<any>(`${environment.apiUrl}/analyze-resumes`, formData).subscribe({
      next: (response) => {
        this.multiResults = response.results;
        this.isLoading = false;
        console.log('Multi analysis result:', this.multiResults);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Multi-resume analysis failed:', error);

        if (error.status === 429) {
          alert(error.error?.detail || 'You have exceeded the rate limit.Please try again later');
        } else {
          alert('Oops! Something went wrong. Please try again.');
        }
      }
    });
  }

  exportExcel() {

    const formattedData = this.multiResults.map((r, index) => ({
      'S.No': index + 1,
      'Resume File': r.filename,
      Emails: r.emails?.join(', '),
      Phones: r.phone_numbers?.join(', '),
      'Tech Skills': r.tech_skills?.join(', '),
      'Soft Skills': r.soft_skills?.join(', '),
      'Match Score': r.match_score,
      'Matched Skills': r.matched_skills?.join(', '),
      'Missing Skills': r.missing_skills?.join(', '),
      'Total Required': r.total_required,
      'Total Matched': r.total_matched,
      'Feedback': r.feedback?.join(', '),
      'Image Quality': r.image_quality,
      'OCR Confidence': r.ocr_confidence,
      'OCR Message': r.ocr_message
    }));

    this.exportService.exportToExcel(formattedData, 'ResumeAnalysis');

   }
}
