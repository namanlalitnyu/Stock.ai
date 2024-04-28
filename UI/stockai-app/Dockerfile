FROM node:8 as builder

COPY StockAi-app/StockAi-app

WORKDIR /StockAi-app

RUN npm install
RUN $(npm bin)/ng build


FROM nginx

COPY --from=builder /StockAi-app/dist/* /usr/share/nginx/html/

EXPOSE 80