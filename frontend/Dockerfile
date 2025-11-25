FROM node:20-alpine AS build
WORKDIR /usr/src/app
COPY package.json tsconfig.json tsconfig.node.json vite.config.ts ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=build /usr/src/app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
