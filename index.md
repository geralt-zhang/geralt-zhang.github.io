---
layout: page
title: zhehua's blog
---

这个网页是基于 Missing 一课的模板改的，这是基于 Jellky 的 Github Page，仅需关注前端布局，由 Github 自动托管部署，因 Ruby 配置太过麻烦，本人给它搞了个 Docker 并美化了一下，主要是字体格式和对齐方式，看着舒服多了。

Jekyll 是一个基于 Ruby 的静态网站生成器。选择它的主要原因是 GitHub Pages 原生支持，代码推送后会自动构建和部署。它的工作原理是将 Markdown 文件转换为 HTML，生成静态网站。静态文件的优势是加载速度快，安全性高，因为没有动态内容执行。Jekyll 需要 Ruby 环境，但版本管理比较复杂。

### 文件结构

Jekyll 的目录结构比较清晰：

- `_layouts/` 存放页面模板
- `_includes/` 存放可重用组件
- `_config.yml` 是网站配置文件
- Markdown 文件作为博客内容

每个 Markdown 文件开头可以定义 Front Matter，包含标题、日期、标签等元数据，用于自动生成页面结构。

### 功能改进

为了提升使用体验，在模板中添加了代码复制功能。通过 JavaScript 为每个代码块添加复制按钮，方便读者复制代码示例。

为了解决 Ruby 部署问题，使用了 Docker 容器化开发环境。Docker 配置基于 ruby:2.7 镜像，安装必要的依赖包，暴露 4000 端口。通过 docker-compose 启动后，可以在本地运行完整的 Jekyll 环境。

```yaml
# docker-compose.yml 配置
services:
  jekyll:
    build: .
    ports:
      - "4000:4000"
    volumes:
      - .:/usr/src/app
    command: bundle exec jekyll serve -w --host 0.0.0.0
```

卷挂载功能实现了文件同步，本地修改代码后，容器内的 Jekyll 会自动重新构建页面。

### 工作流程

日常使用流程是：运行 Docker 启动本地环境，编辑 Markdown 文件，浏览器预览效果。完成后推送到 GitHub，自动部署到线上。

这种方式的优点是可以专注于内容写作，技术维护成本低，所有内容都在 Git 版本控制中。
