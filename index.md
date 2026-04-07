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

### Ruby 语言介绍

Ruby 是松本行弘在 1995 年创造的，设计理念是让编程变得简单愉快。但 Ruby 不只是一门语言，它体现了一种编程哲学。

#### Ruby 的核心特性

**一切皆对象**
在 Ruby 中，一切都是对象，包括数字和字符串。你可以在任何东西上调用方法：

```ruby
irb(main):001:0> "Hello World".length
=> 11
irb(main):002:0> 3.to_s
=> "3"
```

**动态类型和鸭子类型**
Ruby 是动态类型语言，不需要声明变量类型。更重要的是，它遵循"鸭子类型"：如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子。

```ruby
irb(main):003:0> a = 3 ** 2
=> 9
irb(main):004:0> b = "hello"
=> "hello"
```

**模块系统**
Ruby 用模块来组织代码，模块就像工具箱，把相关的方法放在一起：

```ruby
irb(main):005:0> Math.sqrt(9)
=> 3.0
irb(main):006:0> Math.sin(3.14159 / 2)
=> 1.0
```

#### 在 Jekyll 项目中的 Ruby 应用

**运行环境**: Jekyll 本身就是 Ruby 程序，没有 Ruby 解释器它根本跑不起来

**依赖管理**: 通过 RubyGems 安装 Jekyll 和各种插件，就像 npm 之于 Node.js。

Gemfile 定义项目依赖：

```ruby
source 'https://rubygems.org'
gem 'github-pages'
gem 'jekyll-sitemap'
```

**模板处理**: Ruby 负责把 Liquid 模板和 Markdown 转成最终的 HTML。Jekyll 使用 ERB 或 Liquid 模板引擎：

```ruby
# 在 _config.yml 中
markdown: kramdown
highlighter: rouge
```

**构建过程**: 执行 `jekyll build` 或 `jekyll serve` 命令时，Ruby 在幕后做所有重活。它读取 Markdown 文件，应用模板，生成静态 HTML。

**插件系统**: Jekyll 的插件都是 Ruby 程序，可以扩展功能：

```ruby
# _plugins/custom_filter.rb
module Jekyll
  module CustomFilter
    def reverse_string(input)
      input.reverse
    end
  end
end

Liquid::Template.register_filter(Jekyll::CustomFilter)
```

#### Ruby 的版本管理挑战

Ruby 的版本管理确实是个坑。不同版本的 Jekyll 需要不同版本的 Ruby，gem 依赖也经常冲突。这也是为什么我最后选择用 Docker 来解决这些问题。

Ruby 使用语义化版本，每个主版本可能有破坏性变化。GitHub Pages 对 Ruby 版本有特定要求，本地开发版本必须匹配。

#### 为什么选择 Ruby 而不是其他语言

你可能问，为什么 Jekyll 不用 Python 或 JavaScript？原因很简单：

1. **历史原因**: Jekyll 诞生时 Ruby 正流行，Rails 生态成熟
2. **模板优势**: Ruby 的 DSL 能力让配置文件更简洁
3. **生态完整**: RubyGems 有丰富的插件生态
4. **GitHub 支持**: GitHub 原生支持 Ruby，集成度高

有意思的是，虽然整个开发过程都离不开 Ruby，但最终生成的网站却是纯静态的，部署到服务器上根本不需要 Ruby 环境。这就像盖房子，施工时需要各种工具和设备，但盖好后住户只需要享受成果就行。

## 参考资源

- [Ruby 官方网站](https://www.ruby-lang.org/)
- [Jekyll 官方文档](https://jekyllrb.com/docs/)
- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [Docker 官方文档](https://docs.docker.com/)
