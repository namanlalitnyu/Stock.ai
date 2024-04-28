FROM node:20 as builder

COPY stockai-app /stockai-app

WORKDIR /stockai-app

RUN npm install -g @angular/cli
RUN npm install
RUN npx ng build stockai-app   

RUN ls -la dist/stockai-app/browser/


FROM nginx

COPY --from=builder /stockai-app/dist/stockai-app/browser /usr/share/nginx/html

EXPOSE 80