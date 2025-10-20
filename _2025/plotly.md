---
layout: lecture
title: "Plotly & HTML"
details: fig and web learn again
date: 2025-10-20
ready: true
sync: true
syncdate: 2025-10-20
---

Plotly 是一个 Python 的可交互的画图库，它画的图能根据点击变化。目前主要是需要把它的图进行特定样式的美化，因此重点学习模版和对应格式，以下是散点图示例，可以看到非常简洁。官方链接：[https://plotly.com/python/line-and-scatter/](https://plotly.com/python/line-and-scatter/)

```python
# x and y given as DataFrame columns
import plotly.express as px
df = px.data.iris() # iris is a pandas DataFrame
fig = px.scatter(df, x="sepal_width", y="sepal_length")
fig.show()
```

完整示例如下，HTML 网页展示 Plotly 散点图

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plotly Bootstrap Example</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Plotly JS -->
    <script src="https://cdn.plot.ly/plotly-2.29.1.min.js"></script>
    <style>
        body, html {
            height: 100%;
            margin: 0;
        }
        #sidebar {
            background-color: #343a40;
            color: white;
            min-height: 100vh;
        }
        #sidebar a {
            color: white;
            text-decoration: none;
        }
        #sidebar a:hover {
            color: #adb5bd;
        }
        #plot {
            width: 100%;
            height: 90vh;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- 左侧侧边栏 -->
            <nav id="sidebar" class="col-md-2 d-none d-md-block sidebar p-3">
                <h4>Menu</h4>
                <ul class="nav flex-column">
                    <li class="nav-item"><a href="#" class="nav-link">Home</a></li>
                    <li class="nav-item"><a href="#" class="nav-link">Scatter Plot</a></li>
                    <li class="nav-item"><a href="#" class="nav-link">Settings</a></li>
                    <li class="nav-item"><a href="#" class="nav-link">About</a></li>
                </ul>
            </nav>

            <main class="col-md-10 ms-sm-auto col-lg-10 px-md-4 d-flex justify-content-center align-items-center" style="min-height: 100vh;">
                <div style="position: relative; width: 100%; max-width: 100%; height: 0; padding-bottom: 50%;">
                    <iframe src="scatter.html" style="position:absolute; top:0; left:0; width:100%; height:100%; border:none;"></iframe>
                </div>
            </main>

        </div>
    </div>

</body>



</html>
```

```python
import plotly.express as px

df = px.data.iris()

fig = px.scatter(
    df,
    x="sepal_width",
    y="sepal_length",
    color="species",
    size="petal_length",
    hover_data=["petal_width"],
    template="plotly_white"
)

fig.update_layout(
    font=dict(
        family="Consolas",
        size=22,
        color="#000000"
    ),
    title=dict(
        text="Iris Scatter",
        x=0.5,
        xanchor="center"
    ),
    xaxis=dict(
        title="Width (cm)",
        showline=True,
        title_font=dict(size=22),
        linecolor="black",
        linewidth=2,
        mirror=True,
    ),
    yaxis=dict(
        title="Length (cm)",
        showline=True,
        title_font=dict(size=22),
        linecolor="black",
        linewidth=2,
        mirror=True,
    ),
    legend=dict(
        title_text="",
        font=dict(size=22),
        orientation="h",
        yanchor="top",
        y=-0.25,
        xanchor="center",
        x=0.5
    )
)

# 响应式 HTML
fig.write_html(
    "scatter.html",
    include_plotlyjs="cdn",
    full_html=True,
    config={"responsive": True}
)

```