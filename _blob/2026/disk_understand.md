---
layout: lecture
title: "Disk Understand"
date: 2026-01-09
ready: true
sync: true
syncdate: 2026-01-10
---

```
echo hello
```

完成！添加了详细的中文注释解释了整个流程：

✅ Front Matter 部分：

layout: page 表示使用模板
permalink: /blob/ 最终访问地址
phony: true 标记为索引页
✅ Jekyll Liquid 模板部分：

site['blob'] 自动读取 _blob 文件夹下的所有 .md 文件
从 URL 中提取文件夹名作为分类标签
生成 HTML 标签和文章列表
✅ JavaScript 交互部分：

绑定点击事件
点击标签时过滤显示相应分类的文章
实现前端动态效果
现在你可以看到从 文件结构 → Jekyll 处理 → HTML 生成 → JavaScript 交互 的完整流程了！