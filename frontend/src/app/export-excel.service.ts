// Gokul, 02-May, for export to excel Service

import { Injectable } from '@angular/core';

import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

@Injectable({
  providedIn: 'root'
})

export class ExportExcelService {
  exportToExcel(data: any[], filename: string): void {
    // Convert JSON data to worksheet
    const worksheet: XLSX.WorkSheet = XLSX.utils.json_to_sheet(data);

    // Create a workbook
    const workbook: XLSX.WorkBook = {
      Sheets: { 'Resume Analysis': worksheet },
      SheetNames: ['Resume Analysis']
    };

    // Generate Excel buffer
    const excelBuffer: any = XLSX.write(workbook, {
      bookType: 'xlsx',
      type: 'array'
    });

    // Create Blob and save
    const blob = new Blob([excelBuffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });

    saveAs(blob, `${filename}.xlsx`);
  }
}
