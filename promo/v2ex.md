# V2EX 帖子

## 节点
分享创造

## 标题
[Show] EFC — 一个给 AI 研究报告做 fact-check 的工具，因为 AI 自己编了一个不存在的安装命令所以写了这个

## 正文

起因：我让 AI 写一个 Claude Code 插件的安装说明，它非常自信地输出了一个 `claude skill add` 命令。这个命令根本不存在。

然后我发现这不是个例——AI 在做研究报告的时候，有 **5 种系统性错误**，不是随机的，是每次都会犯的：

1. **单位错误**：$4.2B → $4,200B。就是单纯的单位换算丢了，跨语言研究（亿 vs billion）特别容易出
2. **编造数据**：图表显示 6 个数据点，其实只有 2 个有来源，其他 4 个是 AI 自己插值补的
3. **混淆指标**：GMV 当 revenue 写，"贸易额" 当 "出口额"，名字像但其实不是一回事
4. **过期数据当最新的**：2023 年的数据在 2025 年的报告里当 "current"
5. **来源洗白**：一个博客文章被引用成 SEC 文件。二级来源伪装成一级来源

所以我做了 EFC (Everything Fact-Checked)，专门抓这 5 种错误：

- **CLI**：`pip install everything-fact-checked`，然后 `efc audit report.md`
- **GitHub Action**：每个 PR 自动 fact-check 里面的 .md 文件
- **Standalone SKILL.md**：就一个 Markdown 文件，丢到任何 AI agent 的 skill 目录里就行，零依赖

最有用的功能是 **source-content verification**——不只是检查链接能不能打开，而是真的去抓取页面内容，看你引用的数字是不是真的出现在页面上。

```bash
$ efc verify evidence.json
✅ C002: found — 来源包含 5 个关键词匹配
🔌 C003: fetch_failed — 来源无法访问
```

全 stdlib Python，无第三方依赖，MIT 协议，72 个测试。

这个 repo 自己发版前会先 fact-check 自己（FACTCHECK.md），因为第一版就踩了 AI 编造命令的坑 🙃

链接：
- 完整版（CLI + Action + 插件）：https://github.com/Nlai741533/EFC-Plugin
- 精简版（一个 SKILL.md 文件，任何 agent 都能用）：https://github.com/Nlai741533/EFC-standalone

欢迎反馈——特别是 5 种 failure mode 的分类，有没有我漏掉的系统性错误模式？
