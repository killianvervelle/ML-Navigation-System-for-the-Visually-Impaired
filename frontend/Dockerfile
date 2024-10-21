FROM node:lts-alpine AS frontend

ARG VITE_GATEWAY_URL

WORKDIR /frontend
#ensures only the necessary files for installing dependencies are available before running yarn
COPY package.json ./
COPY yarn.lock ./
RUN yarn
COPY . ./
RUN yarn run build

FROM nginx:alpine

#all html, css and js files into webserver image nginx
COPY --from=frontend /frontend/dist /usr/share/nginx/html  

