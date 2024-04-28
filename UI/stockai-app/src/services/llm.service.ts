import { HttpClient } from '@angular/common/http';
import { Injectable, NgZone } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class LlmService {
  constructor(private http: HttpClient, private zone: NgZone) {}
}