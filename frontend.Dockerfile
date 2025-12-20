# Frontend Dockerfile (Vite/React)
FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy frontend source
COPY frontend/ .

# Expose Vite port
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
