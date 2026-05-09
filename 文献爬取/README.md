# Arxiv 论文每日简报系统

一个专注于 GAIA 望远镜和观测星表相关论文的每日简报生成系统，使用官方 Google Gemini AI 生成中文摘要。

## ✨ 功能特点

- 🎯 **专注天体物理**：自动搜索 GAIA、系外行星、恒星物理等相关论文
- 🤖 **AI 中文摘要**：使用官方 Gemini Flash 模型生成 Markdown 中文简报
- 📅 **每日更新**：获取最新提交的论文
- 🔍 **智能去重**：避免重复论文
- 💾 **自动保存**：生成的文件自动保存到本地
- 🛡️ **错误处理**：完善的异常处理机制

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

**方法1：环境变量（推荐）**

**Windows:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY=your_api_key_here
```

也可以在项目根目录创建本地 `.env` 文件：

```text
GEMINI_API_KEY=your_api_key_here
HTTP_PROXY=http://127.0.0.1:7897
HTTPS_PROXY=http://127.0.0.1:7897
ARXIV_REQUEST_DELAY=6
```

`.env` 已加入 `.gitignore`，不会提交到版本库。未设置 API Key 时仍会生成简报，但会使用论文原始英文摘要。

程序会把当天获取到的 Arxiv 论文元数据缓存到 `.cache/`，同一天重复运行会优先使用缓存，减少触发 Arxiv 限流的概率。

### 3. 运行系统

```bash
python arxiv_briefing.py
```

**Windows 用户也可以：**
```cmd
run_briefing.bat
```

## 📋 输出示例

```
【Arxiv 每日论文简报】2025-10-03
==================================================

📄 论文 1:
标题：Bremsstrahlung emission from nuclear reactions in compact stars
链接：http://arxiv.org/abs/1912.12092v1
发表日期：2019-12-27
总结：该论文研究了致密星体（如白矮星和中子星）内部核反应中产生的韧致辐射现象...

--------------------------------------------------

（以上内容由 AI 自动生成，请注意核实）
生成时间：2025-10-03 14:18:34
```

## 🔍 搜索范围

系统会自动搜索以下 Arxiv 分类的最新论文：

- **astro-ph**: 天体物理
- **astro-ph.EP**: 系外行星
- **astro-ph.SR**: 恒星物理
- **astro-ph.GA**: 星系天文学
- **astro-ph.CO**: 宇宙学
- **astro-ph.HE**: 高能天体物理

重点关注：
- GAIA 望远镜相关研究
- 观测星表和恒星数据
- 系外行星发现
- 恒星演化和自转
- 星系形成和演化

## 📁 项目结构

```
arxiv_work_flow/
├── arxiv_briefing.py      # 主程序
├── requirements.txt       # 依赖包列表
├── run_briefing.bat      # Windows 批处理文件
├── README.md             # 说明文档
└── arxiv_briefing_*.md   # 生成的 Markdown 简报文件
```

## ⚙️ 自定义配置

你可以修改 `arxiv_briefing.py` 中的以下参数：

```python
# 搜索查询列表
queries = [
    "cat:astro-ph",        # 天体物理
    "cat:astro-ph.EP",     # 系外行星
    "cat:astro-ph.SR",     # 恒星物理
    # 添加更多查询...
]

# 最大论文数量
max_papers = 5

# 每个查询的最大结果数
max_results_per_query = 2
```

## 🛠️ 技术实现

- **Arxiv API**: 使用官方 XML API 获取论文数据
- **Gemini AI**: 使用官方 `google-genai` 库调用 Gemini Flash 模型
- **Python 3.9+**: 支持现代 Python 特性
- **错误处理**: 完善的异常处理和重试机制

## 📊 性能特点

- ⚡ **快速响应**: 每个查询 2 篇论文，避免 API 限制
- 🔄 **智能去重**: 自动识别重复论文
- ⏱️ **延迟控制**: 自动添加请求延迟避免频率限制
- 💾 **文件管理**: 自动生成带时间戳的文件名

## 🔧 故障排除

### 常见问题

1. **API Key 错误**
   ```
   ❌ 错误：需要提供 API Key
   ```
   - 检查 API Key 是否正确设置
   - 确认 API Key 有效且有足够配额

2. **网络连接问题**
   ```
   ❌ 获取 Arxiv 数据时出错: Connection timeout
   ```
   - 检查网络连接
   - 确认可以访问 arxiv.org

3. **论文数量不足**
   ```
   今日未找到相关论文
   ```
   - 调整搜索查询
   - 增加搜索范围

### 调试模式

在代码中添加调试信息：

```python
# 在 fetch_arxiv_papers 方法中添加
print(f"API URL: {url}")
print(f"参数: {params}")
print(f"响应状态: {response.status_code}")
```

## 🚀 扩展功能

### 邮件发送

可以扩展系统发送邮件：

```python
import smtplib
from email.mime.text import MIMEText

def send_email(briefing):
    # 邮件发送逻辑
    pass
```

### 定时任务

使用 Windows 任务计划程序或 Linux cron 设置定时运行：

```bash
# Linux/Mac cron 示例
0 9 * * * cd /path/to/project && python arxiv_briefing.py
```

### 数据库存储

可以扩展将论文数据存储到数据库：

```python
import sqlite3

def save_to_database(papers):
    # 数据库存储逻辑
    pass
```

## 📝 更新日志

- **v1.0.0** (2025-10-03)
  - 初始版本发布
  - 支持 Arxiv 论文获取
  - 集成 Gemini AI 中文摘要
  - 自动文件保存

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请查看：
1. 检查网络连接
2. 验证 API Key 有效性
3. 查看错误日志
4. 提交 Issue 描述问题

---

**注意**: 生成的摘要仅供参考，请核实重要信息。系统使用官方 Google Gemini API，请遵守相关使用条款。
