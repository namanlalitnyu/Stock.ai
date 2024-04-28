FROM node:20 as builder

COPY stockai-app /stockai-app

WORKDIR /stockai-app

RUN npm install -g @angular/cli
RUN npm install
RUN npx ng build LENR-app   

RUN ls -la dist/LENR-app/browser/


FROM nginx

COPY --from=builder /stockai-app/dist/LENR-app/browser /usr/share/nginx/html

# COPY nginx.conf /etc/nginx/nginx.conf


EXPOSE 80