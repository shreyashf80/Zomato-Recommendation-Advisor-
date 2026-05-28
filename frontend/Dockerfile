# ── Frontend Dockerfile ──────────────────────────────────────────────────────
# Multi-stage build: build the React/Vite SPA then serve it with Nginx.

# Stage 1 – build the static bundle
FROM node:20-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# VITE_API_BASE_URL must be injected at build time as a build-arg so that
# Vite can inline it into the static bundle (import.meta.env.VITE_API_BASE_URL).
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build


# Stage 2 – serve with Nginx
FROM nginx:stable-alpine AS runtime

# Remove the default Nginx placeholder
RUN rm -rf /usr/share/nginx/html/*

# Copy the built SPA
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom Nginx config that redirects all routes to index.html (SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
