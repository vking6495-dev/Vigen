import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';

export interface AppSettings {
  brandName: string;
  logoUrl: string;
  primaryColor: string;
  logoFile?: File;
}

@Injectable({ providedIn: 'root' })
export class AppSettingsService {
  private apiBase = '/api'; // Adjust if needed
  private staticUserId = 'user123';
  // Subject to broadcast settings changes
  public settingsChanged$ = new Subject<AppSettings>();

  constructor(private http: HttpClient) {}

  private getAuthHeaders() {
    return { headers: { 'X-User-Id': this.staticUserId } };
  }

  getSettings(): Observable<AppSettings> {
    return this.http.get<AppSettings>(`${this.apiBase}/settings/${this.staticUserId}`, this.getAuthHeaders());
  }

  updateSettings(settings: AppSettings): Observable<any> {
    // Validate primaryColor before sending
    const validHex = /^#[0-9A-Fa-f]{6}$/;
    let color = settings.primaryColor;
    if (!color || !validHex.test(color)) {
      color = '#1976d2';
    }
    // Prepare FormData for backend
    const formData = new FormData();
    formData.append('brand_name', settings.brandName || '');
    formData.append('color', color);
    formData.append('user_id', this.staticUserId);
    // If logo file is present, append it
    if (settings.logoFile) {
      formData.append('logo_file', settings.logoFile);
    }
    return new Observable(observer => {
      this.http.post(`${this.apiBase}/ui_settings/update_settings`, formData, this.getAuthHeaders()).subscribe({
        next: (res: any) => {
          // Ensure the response matches AppSettings shape
          const updated: AppSettings = {
            brandName: res.brand_name ?? settings.brandName,
            logoUrl: res.logo_url ?? settings.logoUrl ?? '',
            primaryColor: res.color ?? settings.primaryColor,
          };
          this.settingsChanged$.next(updated);
          observer.next(updated);
          observer.complete();
        },
        error: (err) => observer.error(err)
      });
    });
  }

  getSavedSettings(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiBase}/saved-settings/${this.staticUserId}`, this.getAuthHeaders());
  }

  saveSetting(settings: AppSettings): Observable<any> {
    return this.http.post(`${this.apiBase}/saved-settings/${this.staticUserId}`, settings, this.getAuthHeaders());
  }

  deleteSavedSetting(settingId: string): Observable<any> {
    return this.http.delete(`${this.apiBase}/saved-settings/${this.staticUserId}/${settingId}`, this.getAuthHeaders());
  }

  uploadLogo(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return new Observable(observer => {
      this.http.post<any>(`${this.apiBase}/upload-logo/${this.staticUserId}`, formData, this.getAuthHeaders()).subscribe({
        next: (res) => {
          this.settingsChanged$.next({ brandName: '', logoUrl: res.logoUrl, primaryColor: '' });
          observer.next(res);
          observer.complete();
        },
        error: (err) => observer.error(err)
      });
    });
  }
}
