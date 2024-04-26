import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root',
})
export class UtilsService {
    constructor() { }

    public processStreamData(stream: string) {
        if (!stream) return stream;

        const str = stream.replace(/(?:\r\n|\r|\n)/g, '</br>');
        return str;
    }
}