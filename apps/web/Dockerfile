# Multi-stage Dockerfile for React frontend

FROM node:20-alpine as base
WORKDIR /app

# Install dependencies
FROM base as dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Development stage
FROM base as development
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

# Build stage
FROM base as build
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production stage (nginx)
FROM nginx:alpine as production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
