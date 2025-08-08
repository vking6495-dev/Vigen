import { CommonModule } from '@angular/common';
import { AppSettingsService } from '../../services/app-settings.service';
import { Component, Inject, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-saved-settings-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatSnackBarModule,
    MatCardModule,
    MatDialogModule,
  ],
  templateUrl: './saved-settings-dialog.component.html',
})
export class SavedSettingsDialogComponent implements OnInit {
  savedSettingsList: Array<{ id: string; brandName: string; logoUrl: string; primaryColor: string }> = [];

  constructor(
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<SavedSettingsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { currentSettings: any },
    private appSettingsService: AppSettingsService
  ) { }

  ngOnInit() {
    this.loadSavedSettingsList();
  }

  loadSavedSettingsList() {
    const userId = localStorage.getItem('userId') || '';
    this.appSettingsService.getSavedSettings(userId).subscribe({
      next: (list: any[]) => {
        this.savedSettingsList = list;
      },
      error: () => {
        this.snackBar.open('Failed to load saved settings', 'Close', { duration: 2000 });
      }
    });
  }

  deleteSavedSetting(index: number) {
    const userId = localStorage.getItem('userId') || '';
    const settingId = this.savedSettingsList[index].id;
    this.appSettingsService.deleteSavedSetting(userId, settingId).subscribe({
      next: () => {
        this.snackBar.open('Deleted saved setting!', 'Close', { duration: 2000 });
        this.savedSettingsList.splice(index, 1);
      },
      error: () => {
        this.snackBar.open('Failed to delete setting', 'Close', { duration: 2000 });
      }
    });
  }

  applySavedSetting(index: number) {
    const setting = this.savedSettingsList[index];
    localStorage.setItem('uiPersonalizationSettings', JSON.stringify(setting));
    this.snackBar.open('Applied saved setting!', 'Close', { duration: 2000 });
    this.dialogRef.close({ applied: true, settings: setting });
  }

  closeDialog() {
    this.dialogRef.close();
  }
}
