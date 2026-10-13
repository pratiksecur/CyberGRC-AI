# ============================================================
# Stage 1 — Frontend build
# ============================================================
FROM node:26-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=http://localhost:8000/api/v1
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ============================================================
# Stage 2 — Nginx runtime
# ============================================================
FROM nginx:alpine

ARG VITE_API_ORIGIN=http://localhost:8000

# Remove default server configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy production Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Inject API origin
RUN sed -i "s|__API_ORIGIN__|${VITE_API_ORIGIN}|g" /etc/nginx/nginx.conf

# Copy built frontend
COPY --from=builder /app/dist /usr/share/nginx/html

# Prepare directories for the unprivileged nginx user (UID 101)
RUN mkdir -p \
        /tmp/nginx/client_temp \
        /tmp/nginx/proxy_temp \
        /tmp/nginx/fastcgi_temp \
        /tmp/nginx/uwsgi_temp \
        /tmp/nginx/scgi_temp \
    && chown -R 101:101 /tmp/nginx \
    && chown -R 101:101 /usr/share/nginx/html \
    && chmod -R 755 /usr/share/nginx/html

EXPOSE 80

# Run the container as the nginx user.
USER 101:101

CMD ["nginx", "-g", "daemon off;"]