# 即刻 (Jike) 帖子

## 正文

我让 AI 写一个安装说明，它自信地输出了一个不存在的命令。

然后我发现 AI 做研究报告时有 5 种固定的错误模式，不是随机的，是每次都会犯的：

1️⃣ 单位错误：$4.2B → $4,200B。跨语言研究（亿 vs billion）特别容易出
2️⃣ 编造数据：图表 6 个点只有 2 个有来源，其他是 AI 自己补的
3️⃣ 混淆指标：GMV 当 revenue 写，名字像但不是一回事
4️⃣ 过期数据：2023 的数据当 2025 的最新的
5️⃣ 来源洗白：博客被引用成 SEC 文件，二级来源伪装成一级

做了 EFC 专门抓这 5 种：
• CLI：pip install 一行搞定
• GitHub Action：PR 自动 fact-check
• 一个 Markdown 文件版：任何 AI agent 都能用

最好用的功能：不只是检查链接能不能打开，而是抓取页面看你引用的数字是否真的在里面。

这个 repo 自己发版前会先 fact-check 自己，因为第一版就踩了 AI 编命令的坑 😂

🔗 github.com/Nlai741533/EFC-Plugin
🔗 github.com/Nlai741533/EFC-standalone

#AI #FactCheck #数据质量 #LLM #开源
