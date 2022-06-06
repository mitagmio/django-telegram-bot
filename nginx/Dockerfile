FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./default.conf /etc/nginx/conf.d
COPY ./fullchain1.pem /etc/ssl/nginx/cert.pem
COPY ./privkey1.pem /etc/ssl/nginx/key.pem


