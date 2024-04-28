import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { APP_CONSTANTS } from '../constants/app.constants';

@Injectable({
    providedIn: 'root',
})
export class DBService {
    constructor(private http: HttpClient) { }

    public getRecommendationPrompt(question: string): Observable<any> {
        const url = APP_CONSTANTS.dbServer + '/recommendation';
        return this.http.get(url,{
            params: new HttpParams().set('question', question)
        });
    }

    public getQAPrompt(question: string): Observable<any> {
        const url = APP_CONSTANTS.dbServer + '/qa';
        return this.http.get(url,{
            params: new HttpParams().set('question', question)
        });
    }
}