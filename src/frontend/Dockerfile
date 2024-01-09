ARG NODE_VERSION=21.5.0
FROM node:${NODE_VERSION}-alpine

WORKDIR /usr/src/app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
