---
layout: page
title: 河边的西瓜
---

# The Missing Semester of Your CS Education 中文版总结

The Missing Semester of Your CS Education是一个非常全面的技术工具课程，包括Shell、Vim、数据整理等等，十分适合新手对计算机产生兴趣、科研测试以及高效率的工作，作者本人受其影响，决定再加工、整理一下，以便可以快速上手这些工具。这个网页也是基于Missing一课的模板改的，这是基于Jellky的Github Page，仅需关注前端布局，由Github自动托管部署。

当前目标：
* 学习每一章节的课程，把核心内容总结至该网站。
* 优化网站排版，引入分类和搜索。


<!-- 关于 [开设此课程的动机](/about/)。 -->

<!-- {% comment %}

# Registration

Sign up for the IAP 2025 class by filling out this [registration form](https://forms.gle/TD1KnwCSV52qexVt9).
{% endcomment %} -->

<!-- # 日程 <span style="float:right"><img src = "https://img.shields.io/badge/文档同步时间-2021--04--24-blue"></span> -->

<ul>
{% assign lectures = site['2025'] | sort: 'date' %}
{% for lecture in lectures %}
    {% if lecture.phony != true and lecture.solution !=true  %}
        <li>
        <strong>{{ lecture.date | date: '%-m/%d' }}</strong>:
        <!-- {% if lecture.ready%} -->
            <a href="{{ lecture.url }}">{{ lecture.title }}</a><span style="float:right">{{lecture.syncdate}}</span>
        <!-- {% else %} -->
             <!-- <a href="{{ lecture.url }}">{{ lecture.title }}  {% if lecture.noclass %}[no class]{% endif %}</a><span style="float:right"><img src = "https://img.shields.io/badge/Chinese-✘-orange"></span> -->
        <!-- {% endif %} -->
        <!-- {% if lecture.sync %}
           <span style="float:right"><img src = "https://img.shields.io/badge/Update-✔-green"></span>
        {% else %}
           <span style="float:right"><img src = "https://img.shields.io/badge/Update-✘-orange"></span> -->
        <!-- {% endif %}
        {% if lecture.solution.ready%}
        <span style="float:right"><a href="{{site.url}}/{{site.solution_url}}/{{lecture.solution.url}}"><img src = "https://img.shields.io/badge/Solution-✔-green"></a></span>
            {% else %}
            <span style="float:right"><img src = "https://img.shields.io/badge/Solution-✘-orange"></span>
            {% endif %} -->
        </li>
    {% endif %}
{% endfor %}
</ul>

<!-- 讲座视频可以在 [
YouTube](https://www.youtube.com/playlist?list=PLyzOVJj3bHQuloKGG59rS43e29ro7I57J) 上找到。

# 关于本课程

**教员**：本课程由 [Anish](https://www.anishathalye.com/)、[Jon](https://thesquareplanet.com/) 和 [Jose](http://josejg.com/) 讲授。

**问题**：请通过 [missing-semester@mit.edu](mailto:missing-semester@mit.edu) 联系我们。

# 在 MIT 之外

我们也将本课程分享到了 MIT 之外，希望其他人也能受益于这些资源。您可以在下面这些地方找到相关文章和讨论。

 - [Hacker News](https://news.ycombinator.com/item?id=22226380)
 - [Lobsters](https://lobste.rs/s/ti1k98/missing_semester_your_cs_education_mit)
 - [/r/learnprogramming](https://www.reddit.com/r/learnprogramming/comments/eyagda/the_missing_semester_of_your_cs_education_mit/)
 - [/r/programming](https://www.reddit.com/r/programming/comments/eyagcd/the_missing_semester_of_your_cs_education_mit/)
 - [Twitter](https://twitter.com/jonhoo/status/1224383452591509507)
 - [YouTube](https://www.youtube.com/playlist?list=PLyzOVJj3bHQuloKGG59rS43e29ro7I57J)

# 译文

- [繁体中文](https://missing-semester-zh-hant.github.io/)
- [Japanese](https://missing-semester-jp.github.io/)
- [Korean](https://missing-semester-kr.github.io/)
- [Portuguese](https://missing-semester-pt.github.io/)
- [Russian](https://missing-semester-rus.github.io/)
- [Serbian](https://netboxify.com/missing-semester/)
- [Spanish](https://missing-semester-esp.github.io/)
- [Turkish](https://missing-semester-tr.github.io/)
- [Vietnamese](https://missing-semester-vn.github.io/)

注意：上述链接为社区翻译，我们并未验证其内容。

## 致谢

感谢 Elaine Mello, Jim Cain 以及 [MIT Open Learning](https://openlearning.mit.edu/) 帮助我们录制讲座视频。

感谢 Anthony Zolnik 和 [MIT AeroAstro](https://aeroastro.mit.edu/) 提供 A/V 设备。

感谢 Brandi Adams 和 [MIT EECS](https://www.eecs.mit.edu/) 对本课程的支持。

--- -->

<!-- <div class="small center">
<p><a href="https://github.com/missing-semester-cn/missing-semester-cn">Source code</a>.</p>
<p>Licensed under CC BY-NC-SA.</p>
<p>See <a href="/license">here</a> for contribution &amp; translation guidelines.</p>
</div> -->
