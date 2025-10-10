---
layout: page
title: 河边的西瓜
---

这个网页是基于 Missing 一课的模板改的，这是基于 Jellky 的 Github Page，仅需关注前端布局，由 Github 自动托管部署，因 ruby 配置太过麻烦，本人给它搞了个 docker 并美化了一下，主要是字体格式和对齐方式，看着舒服多了

NEED TO DO:

* 把字体的段落格式调一下，两端对齐 ✅
* 写点 blob

<!-- <ul>
{% assign lectures = site['2025'] | sort: 'date' %}
{% for lecture in lectures %}
    {% if lecture.phony != true and lecture.solution !=true  %}
        <li>
        <strong>{{ lecture.date | date: '%-m/%d' }}</strong>:
            <a href="{{ lecture.url }}">{{ lecture.title }}</a><span style="float:right">{{lecture.syncdate}}</span>
        </li>
    {% endif %}
{% endfor %}
</ul> -->
