---
layout: lecture
title: "邮件客户端的配置和使用"
date: 2026-03-24
ready: true
sync: true
syncdate: 2026-03-24
typora-root-url: ./..
---

工作了之后发现互联网上正经交流主要靠邮件，不管是公司事项通知、申请、或是开源项目如 Linux 内核等等的合作开发，都要用邮件来沟通，之前因为不知道可以自己配置，下载了好几个邮件客户端，打开起来非常费劲，并且很多都是垃圾邮件，所以兴趣不大，偶然间用到 apple 的邮件 app 以及看到 `hackermail` 这个项目，才开始正经的用上邮件，`hackermail` 是由一些内核黑客为了方便邮件交流开发出来的终端邮件客户端，官方链接：https://github.com/sjp38/hackermail

![interactive list](/../static/media/hkml_interactive_list_demo-20260324230600146.gif)

使用 `hackmail` 需要首先初始化

```bash
./hkml init
```

它会首先探测 manifest，并从 lore.kernel.ory 下载邮件索引，成功后会生成 .hkm/ 目录，这是本地的邮件数据库。

常用命令：

```bash
./hkml list damon
```

进入交互式界面，可以浏览邮件，在列表里按 Enter 即可进入，其中有个 Thread 表示邮件里的楼中楼，按 t 可以进入，同时按 r 可以进入回复邮件的模式，最后可以用 send 编辑新邮件发送，fetch 拉取最新。

