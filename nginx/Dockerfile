FROM nginx:1.13.8

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY natomas.conf /etc/nginx/conf.d/

EXPOSE 80
EXPOSE 443
