# 使用 Ruby 2.7 版本（兼容 github-pages 203）
FROM ruby:2.7

# 设置工作目录
WORKDIR /usr/src/app

# 复制 Gemfile 和 Gemfile.lock（提前安装依赖，提高缓存命中率）
COPY Gemfile Gemfile.lock ./

# 安装依赖
RUN gem install bundler -v 2.1.4 && bundle install

# 复制项目文件（网站源码）
COPY . .

# 暴露 Jekyll 默认端口
EXPOSE 4000

# 运行本地服务器
CMD ["bundle", "exec", "jekyll", "serve", "-w", "--host", "0.0.0.0"]

