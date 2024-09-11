import { Component } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface FileElement {
  documentName: string;
  createdDate: string;
  language: string;
  numberOfPages: number;
  fileSize: string;
}

const ELEMENT_DATA: FileElement[] = [
  { documentName: '1.pdf', createdDate: '27/08/2024', language: 'Arabic - English', numberOfPages: 5, fileSize: '3 MB' },
  { documentName: '1.docx', createdDate: '27/08/2024', language: 'Arabic - English', numberOfPages: 5, fileSize: '2 MB' }
  // Add more rows as needed
];

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent {
  displayedColumns: string[] = ['select', 'documentName', 'createdDate', 'language', 'numberOfPages', 'fileSize'];
  dataSource = ELEMENT_DATA;
  showProgressBar = false;
  uploadProgress = 0;

  constructor(private http: HttpClient, private snackBar: MatSnackBar) {}

  // Handle file selection and upload
  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.showProgressBar = true;

      const formData: FormData = new FormData();
      formData.append('file', file, file.name);

      // Send the file to the Flask backend
      this.http.post('/upload', formData, { 
        responseType: 'blob',
        reportProgress: true,
        observe: 'events' 
      }).subscribe(event => {
        if (event.type === HttpEventType.UploadProgress) {
          if (event.total) {
            this.uploadProgress = Math.round(100 * event.loaded / event.total);
          }
        } else if (event.type === HttpEventType.Response) {
          this.showProgressBar = false;
          this.uploadProgress = 0;

          const blob = new Blob([event.body as Blob], { type: file.type });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = file.name.replace(/\.\w+$/, '') + '_translated' + file.name.slice(file.name.lastIndexOf('.'));
          link.click();

          this.snackBar.open('File translated and downloaded successfully', 'Close', {
            duration: 3000,
            verticalPosition: 'top',
            panelClass: ['custom-snackbar']
          });
        }
      }, error => {
        this.showProgressBar = false;
        this.uploadProgress = 0;
        this.snackBar.open('File upload failed', 'Close', {
          duration: 3000,
          verticalPosition: 'top',
          panelClass: ['custom-snackbar']
        });
      });
    }
  }

  // Handle download click (if needed)
  onDownloadClick(): void {
    console.log('Download button clicked');
  }
}
