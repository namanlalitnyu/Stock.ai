import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { Observable, map } from 'rxjs';
import { APP_CONSTANTS } from '../constants/app.constants';
import { DBService } from '../services/db.service';
import { UtilsService } from '../services/utils.service';

export const LLM_MODES = {
  recommendation: "Recommendation System",
  qa: "Question Answering",
  rawLLM: "Raw LLM"
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, FormsModule, NgbDropdownModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  public title: string = "LENR.ai";
  public streamText: string = "";
  public promptText: string = "";
  public llmModes: any = LLM_MODES;
  public selectedMode: string = LLM_MODES.recommendation;
  public sourceDocs: any[] = [];

  public isPristine: boolean = false;
  public isFetchingDocs: boolean = false;
  public isLoading: boolean = false;
  public hasError: boolean = false;
  public hasQAResult: boolean = false;
  public errorMessage: string = "";

  constructor(private db: DBService, private utils: UtilsService) {
    this.isPristine = true;
  }

  get isInTranstion(): boolean {
    return this.isFetchingDocs || this.isLoading;
  }

  get hasResult(): boolean {
    return !this.isInTranstion && !this.isPristine && !this.hasError;
  }

  get isInQAMode(): boolean {
    return this.selectedMode === this.llmModes.qa && this.hasQAResult;
  }

  getAnswer(): void {
    this.streamText = "";
    this.isPristine = false;
    this.hasError = false;
    this.hasQAResult = false;

    if (this.selectedMode == LLM_MODES.rawLLM) {
      this.getStream(this.promptText);
    } else {
      this.isFetchingDocs = true;
      const request = this.selectedMode == LLM_MODES.recommendation ? this.getRecommendation() : this.getQAResponse();
      request.pipe(
        map((data) => {
          this.isFetchingDocs = false;
          if (data.context && data.context.doc_count > 0) {
            this.sourceDocs = data.context.documents.map((doc: any) => doc.metadata);
          }
          return data.prompt;
        })).subscribe({
          next: (prepared_prompt: string) => {
            this.getStream(prepared_prompt);
            /**
             * This is a debug code line
             * Uncomment it to check the output of the DB Server
             */
            // this.streamText = this.utils.processStreamData(prepared_prompt);
          }, error: (err) => {
            console.error("Error from DB call", err);
            this.isFetchingDocs = false;
            this.hasError = true;
            this.errorMessage = "Error in fetching LENR domain documents";
          }
        });
    }
  }

  private getQAResponse(): Observable<any> {
    this.hasQAResult = true;
    return this.db.getQAPrompt(this.promptText);
  }

  private getRecommendation(): Observable<any> {
    return this.db.getRecommendationPrompt(this.promptText);
  }

  private async getStream(prepared_prompt: string) {
    this.isLoading = true;

    try {
      let response = await fetch(APP_CONSTANTS.cppServer + "/completion", {
        method: 'POST',
        body: JSON.stringify({
          prompt: prepared_prompt,
          n_predict: 1024,
          stream: true,
        })
      })

      if (response.status !== 200) {
        throw new Error('Fetch request failed',);
      }

      const reader = response.body?.pipeThrough(new TextDecoderStream()).getReader();

      while (true) {
        const data = await reader?.read();

        let lastLine = data?.value?.split(/\r?\n/);
        let last_array = lastLine?.filter(e => e != '');

        let stop = false;
        last_array?.forEach((str) => {
          this.isLoading = false;
          this.streamText += this.utils.processStreamData(JSON.parse(str).content);
          if (JSON.parse(str)?.stop) {
            stop = true;
          }
        });

        if (stop) {
          this.isLoading = false;
          break;
        }
      }

    } catch (error) {
      this.isLoading = false;
      this.hasError = true;
      this.errorMessage = "Error in fetching the LLM data";
    }
  }

  public changeMode(mode: any) {
    if (mode && this.llmModes[mode]) {
      this.selectedMode = this.llmModes[mode];
    }
  }
}
