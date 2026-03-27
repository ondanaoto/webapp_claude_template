# ---- dev: Vite dev server with hot-reload ----
FROM node:22-alpine AS dev

WORKDIR /app

COPY package.json package-lock.json ./

ENTRYPOINT ["sh", "-c", "npm ci --ignore-scripts && npx buf generate && exec \"$0\" \"$@\""]
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ---- build: compile frontend assets ----
# Build context must be the project root so packages/proto is accessible.
FROM node:22-alpine AS build

WORKDIR /workspace/apps/web

# Install dependencies
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci

# Copy proto definitions (buf.gen.yaml references ../../packages/proto)
COPY packages/proto /workspace/packages/proto
COPY apps/web/buf.gen.yaml ./

# Generate TypeScript from protobuf
RUN npx buf generate

# Copy source and build
COPY apps/web/ ./

RUN npm run build

# ---- prod: nginx static serving ----
FROM nginx:alpine AS prod

COPY --from=build /workspace/apps/web/dist /usr/share/nginx/html
COPY infrastructure/docker/web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
