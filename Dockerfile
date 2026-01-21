# Backend setup
FROM devopsworks/golang-upx:latest as backend-builder

ENV DEBIAN_FRONTEND noninteractive
WORKDIR /app
COPY ./backend /app
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o whishper . && \
    upx whishper
RUN chmod a+rx whishper

# Frontend setup
FROM node:20-alpine as frontend
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY ./frontend /app
WORKDIR /app

FROM frontend AS frontend-prod-deps
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --no-frozen-lockfile

FROM frontend AS frontend-build
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --no-frozen-lockfile
ENV BODY_SIZE_LIMIT=0
RUN pnpm run build

# Base container
FROM python:3.11-slim as base

RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends \
    ffmpeg mpack nodejs nginx supervisor build-essential python3-dev python3-pip libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN python3 -m pip install --no-cache-dir --break-system-packages yt-dlp

# Python service setup
COPY ./transcription-api /app/transcription
WORKDIR /app/transcription
RUN python3 -m pip install --no-cache-dir --break-system-packages --upgrade pip && \
    python3 -m pip install --no-cache-dir --break-system-packages torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    python3 -m pip install --no-cache-dir --break-system-packages python-multipart

# Node.js service setup
ENV BODY_SIZE_LIMIT=0
ENV NODE_ENV=production
WORKDIR /app/frontend-build
COPY --from=frontend-build /app/build ./build
COPY --from=frontend-build /app/package.json ./package.json
COPY --from=frontend-build /app/node_modules ./node_modules

# Golang service setup
COPY --from=backend-builder /app/whishper /bin/whishper 
RUN chmod a+rx /bin/whishper

WORKDIR /app
RUN mkdir -p uploads models

# Nginx setup
COPY ./nginx.conf /etc/nginx/nginx.conf

# Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/* ~/.cache /var/cache

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

EXPOSE 80