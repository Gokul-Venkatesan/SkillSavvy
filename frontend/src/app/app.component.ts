
  //Gokul - 15th and 16th Apr 2025, UI to capture custom skills, Job post and resume upload
  //to compare the skills and produce match score.
  //Played around with UI to bring it more easy to view


import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, HttpClientModule, CommonModule, RouterModule],
  templateUrl: './app.component.html',
})

export class AppComponent {
  title = 'Resume Analyzer'; 
  resumeFile: File | null = null;
  jobDescription: string = '';
  skillsList: string = '';
  softSkills: string = '';
  result: any = null;
  //isLoading: boolean = false;

  constructor(private http: HttpClient) { }

  onFileSelected(event: any) {
    this.resumeFile = event.target.files[0] || null;
  }

  analyzeResume() {

    const formData = new FormData();
    this.result = null;
    
    if (this.resumeFile) {

      const allowedExtensions = ['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'];
      const fileExtension = this.resumeFile.name.split('.').pop()?.toLowerCase();

      if (!fileExtension || !allowedExtensions.includes(fileExtension)) {
        alert('❌ Unsupported file format. Please upload a file in PDF, DOCX, TXT, JPG, or PNG format.');
        //event.target.value = ''; // Reset file input
        this.resumeFile = null;
        return;
      }
      formData.append('resume_file', this.resumeFile, this.resumeFile.name);
    }
    else {
      this.result = null;
      return;
    }

    formData.append('job_description', this.jobDescription);
    formData.append('skills_list', this.skillsList);
    formData.append('soft_skills', this.softSkills);

    //this.isLoading = true;

    this.http.post('http://localhost:8000/analyze-resume', formData).subscribe({
      next: (data) => {
        this.result = data;
        //this.isLoading = false;
        console.log('Analysis result:', data);
      },
      error: (error) => {
        console.error('Error analyzing resume:', error);
        //this.isLoading = false;
      }
    });
  }
}
