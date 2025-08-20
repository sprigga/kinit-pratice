# 使用 Nginx 作為基礎映像
FROM nginx:stable-alpine

# 設置工作目錄（非必需）
WORKDIR /usr/share/nginx/html

# 複製 Vue 打包後的 dist 目錄
COPY dist-pro/ /usr/share/nginx/html/kinit-admin/dist-pro

# 複製自定義的 Nginx 配置文件
COPY default.conf /etc/nginx/conf.d/default.conf

# 暴露 80 端口
EXPOSE 80

# 啟動 Nginx
CMD ["nginx", "-g", "daemon off;"]
