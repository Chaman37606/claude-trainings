FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src/ ./src/
RUN npm run build

COPY public/ ./public/

EXPOSE 3001 3000

ENV MCP_PORT=3001 \
    UI_PORT=3000 \
    SEARCH_PROVIDER=duckduckgo

CMD ["npm", "start"]
