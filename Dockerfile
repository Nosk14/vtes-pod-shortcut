FROM nginx:1.17.8
COPY index.html /usr/share/nginx/html
COPY data.js /usr/share/nginx/html