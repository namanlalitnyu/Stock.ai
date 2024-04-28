import { Injectable } from '@angular/core';
import { APP_CONSTANTS } from '../constants/app.constants';
import OpenAI from 'openai';

@Injectable({
    providedIn: 'root',
})
export class ChatService {

    private openai = new OpenAI({
        apiKey: APP_CONSTANTS.openAIKey,
        dangerouslyAllowBrowser: true
    });

    constructor() {}

    async getResult(text: string) {
        text = "stock market";
        return await this.openai.chat.completions.create({
            model: "gpt-3.5-turbo-0125",
            messages: [{ role: 'user', content: text}],
            max_tokens: 5
        });
    }
  }