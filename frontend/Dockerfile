# Frontend Dockerfile - builds React app and serves via nginx
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --silent
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
# Expose standard HTTP port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
