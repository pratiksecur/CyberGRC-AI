# ==========================================================
# Stage 1 — Build React application
# ==========================================================

FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# API URL used by the browser
ARG VITE_API_URL=http://localhost:8000/api/v1

ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ==========================================================
# Stage 2 — Nginx
# ==========================================================

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]