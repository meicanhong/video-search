# 使用 Node.js 作为基础镜像
FROM node:18-alpine

WORKDIR /app

# 复制项目文件
COPY package*.json ./
COPY tsconfig*.json ./
COPY public/ public/
COPY src/ src/
COPY vite.config.ts ./
COPY index.html ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# 安装依赖
RUN npm install

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "run", "dev"]