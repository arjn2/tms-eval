import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { LoginService } from '../auth/login.service';

@Injectable({
  providedIn: 'root',
})
export class BackendService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient, private login: LoginService) {}

  // Method without type constraints - returns Observable<any>
  request(
    userType: 'employee' | 'manager' | 'admin',
    method: 'GET' | 'POST' | 'PUT' | 'PATCH',
    endpoint: string,
    data: any = null,
    queryParams?: Record<string, any>,
    id?: number
  ): Observable<any> {
    return this.requestTyped<any>(userType, method, endpoint, data, queryParams, id);
  }

  // Keep the original typed version in case you need it in the future
  requestTyped<T = any>(
    userType: 'employee' | 'manager' | 'admin',
    method: 'GET' | 'POST' | 'PUT' | 'PATCH',
    endpoint: string,
    data: any = null,
    queryParams?: Record<string, any>,
    id?: number
  ): Observable<T> {
    const headers = this.login.getHeaders();
    let url = `${this.baseUrl}/${userType}/${endpoint}/`;
    if (id) url += `${id}/`;

    let params = new HttpParams();
    
    if (queryParams && Object.keys(queryParams).length > 0) {  
      const shouldApplyParams = userType === 'manager'; // Add more conditions if needed
      
      if (shouldApplyParams) {
        Object.entries(queryParams).forEach(([key, value]) => {
          if (value !== null && value !== undefined && value !== '') { // Avoid empty values
            params = params.set(key, value);
          }
        });
      }
    }
    
    let request$: Observable<T>;

    switch (method) {
      case 'GET':
        request$ = this.http.get<T>(url, { headers, params });
        break;
      case 'POST':
        request$ = this.http.post<T>(url, data, { headers });
        break;
      case 'PUT':
        request$ = this.http.put<T>(url, data, { headers });
        break;
      case 'PATCH':
        request$ = this.http.patch<T>(url, data, { headers });
        break;
      default:
        return throwError(() => new Error('Unsupported HTTP method'));
    }

    return request$.pipe(
      tap((response) => console.log(`Response from ${url}:`, response)),
      catchError((error) => {
        console.error(`Error in ${method} request to ${url}:`, error);
        return throwError(() => new Error(`Request failed`));
      })
    );
  }
}

