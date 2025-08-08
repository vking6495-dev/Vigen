import { Component, OnInit } from '@angular/core';
import { AppSettingsService, AppSettings } from '../services/app-settings.service';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-settings-dialog',
  standalone: true,
  imports: [
    MatDialogModule,
    MatIconModule,
    MatDividerModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    FormsModule
  ],
  templateUrl: './settings-dialog.component.html',
  styleUrls: ['./settings-dialog.component.css']
})
export class SettingsDialogComponent implements OnInit {
  settings: AppSettings = { brandName: '', logoUrl: '', primaryColor: '' };
  loading = false;
  error = '';
  logoPreview: string = '';
  brandName: string = '';
  primaryColor: string = '#1976d2';

  constructor(private appSettingsService: AppSettingsService) {}

  ngOnInit() {
    this.loadSettings();
  }

  loadSettings() {
    this.loading = true;
    this.appSettingsService.getSettings().subscribe({
      next: (settings: AppSettings) => {
        this.settings = settings;
        this.logoPreview = settings.logoUrl;
        this.brandName = settings.brandName;
        this.primaryColor = settings.primaryColor;
        this.loading = false;
      },
      error: (err: any) => {
        this.error = 'Failed to load settings';
        this.loading = false;
      }
    });
  }

  onLogoSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.appSettingsService.uploadLogo(file).subscribe({
        next: (res: any) => {
          this.logoPreview = res.logoUrl;
          this.settings.logoUrl = res.logoUrl;
        },
        error: () => {
          this.error = 'Logo upload failed';
        }
      });
    }
  }

  saveSettings() {
    this.loading = true;
    // Only include logoUrl if it is non-empty
    const updatedSettings: any = {
      brandName: this.brandName,
      primaryColor: this.primaryColor
    };
    if (this.logoPreview && this.logoPreview.trim() !== '') {
      updatedSettings.logoUrl = this.logoPreview;
    }
    this.appSettingsService.updateSettings(updatedSettings).subscribe({
      next: (_: any) => {
        this.appSettingsService.settingsChanged$.next(updatedSettings);
        this.loading = false;
      },
      error: (_: any) => {
        this.error = 'Failed to save settings';
        this.loading = false;
      }
    });
  }

  openSavedSettingsDialog() {
    // Implement dialog open logic in component
  }

  resetSettings() {
    this.loadSettings();
  }

  // getUserId() removed, static userId is used in service
}