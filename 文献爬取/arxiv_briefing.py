import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from google import genai
from google.genai import errors as genai_errors


# 讲解时可以先看这里：这些是整个程序的主要配置。
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = "gemini-flash-latest"
MAX_PAPERS = 5
CACHE_DIR = os.path.join(BASE_DIR, ".cache")
ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_QUERY = (
    "cat:astro-ph OR cat:astro-ph.EP OR cat:astro-ph.SR OR "
    "cat:astro-ph.GA OR cat:astro-ph.CO OR cat:astro-ph.HE"
)
ARXIV_USER_AGENT = os.getenv("ARXIV_USER_AGENT", "arxiv-briefing/1.0 (personal research briefing)")


def setup() -> None:
    """准备运行环境：修复 Windows 控制台编码，并读取 .env 配置。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    env_file = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_file):
        return

    # .env 每行形如 KEY=VALUE，用来放 API Key 和代理配置。
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


def clean_text(text: str) -> str:
    """把 Arxiv 返回的换行和多余空格压成普通句子。"""
    return re.sub(r"\s+", " ", text or "").strip()


def clean_markdown(text: str) -> str:
    """保留 Markdown 换行，只去掉行尾空格和过多空行。"""
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    lines = [line.rstrip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def fetch_arxiv_papers(max_results: int) -> list[dict]:
    """从 Arxiv 获取论文。遇到 429 限流时等待后重试。"""
    params = {
        "search_query": ARXIV_QUERY,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    headers = {"User-Agent": ARXIV_USER_AGENT}

    print("正在请求 Arxiv...")
    response = None
    for attempt in range(4):
        response = requests.get(ARXIV_API_URL, params=params, headers=headers, timeout=30)
        if response.status_code != 429:
            break

        retry_after = response.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            wait_seconds = int(retry_after)
        else:
            wait_seconds = min(180, 60 * (attempt + 1))

        print(f"Arxiv 返回 429 Too Many Requests，等待 {wait_seconds} 秒后重试...")
        time.sleep(wait_seconds)

    if response is None:
        raise RuntimeError("Arxiv 请求未发出")
    if response.status_code == 429:
        raise RuntimeError("Arxiv 仍在限流：请稍后再试，或检查是否有代理/多任务共享同一个出口 IP")

    response.raise_for_status()

    # Arxiv API 返回 Atom XML，所以这里用 ElementTree 解析。
    root = ET.fromstring(response.content)
    papers = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
        summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", "")
        link = entry.findtext("{http://www.w3.org/2005/Atom}id", "")
        published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")
        updated = entry.findtext("{http://www.w3.org/2005/Atom}updated", "")
        authors = [
            clean_text(author.findtext("{http://www.w3.org/2005/Atom}name", ""))
            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
        ]
        categories = [
            category.attrib.get("term", "")
            for category in entry.findall("{http://www.w3.org/2005/Atom}category")
        ]

        papers.append(
            {
                "title": clean_text(title),
                "summary": clean_text(summary),
                "link": link.strip(),
                "published": published[:10],
                "updated": updated[:10],
                "authors": [author for author in authors if author],
                "categories": [category for category in categories if category],
            }
        )

    print(f"获取到 {len(papers)} 篇论文")
    return papers


def load_or_fetch_papers() -> list[dict]:
    """优先读取当天缓存；没有缓存时才请求 Arxiv。"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    cache_file = os.path.join(CACHE_DIR, f"arxiv_papers_{today}.json")

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            papers = json.load(f)
        print(f"已读取缓存：{cache_file}")
        return papers

    papers = fetch_arxiv_papers(max_results=MAX_PAPERS * 3)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    return papers


def summary_cache_path(paper: dict) -> str:
    """用 Arxiv id 生成稳定的摘要缓存文件名。"""
    paper_id = paper["link"].rstrip("/").split("/")[-1].replace(":", "_")
    return os.path.join(CACHE_DIR, f"summary_{paper_id}.md")


def extract_response_text(response) -> str:
    """只读取 Gemini 响应中的文本部分，避开 SDK 对 thought_signature 的警告。"""
    texts = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            text = getattr(part, "text", None)
            if text:
                texts.append(text)
    return "\n".join(texts).strip()


def summarize_with_gemini(client: genai.Client, paper: dict) -> str:
    """调用 Gemini，把英文摘要改写成中文简报。"""
    cache_file = summary_cache_path(paper)
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    prompt = f"""请用中文总结以下论文，要求：
1. 使用 Markdown 格式
2. 严格按下面三个小节输出：
   - **一句话概括**
   - **主要贡献**
   - **创新点**
3. “主要贡献”和“创新点”必须使用项目符号列表
4. 总字数控制在 250 字以内
5. 不要输出额外标题，不要重复“中文总结”

论文标题：{paper["title"]}

论文摘要：
{paper["summary"]}

中文总结："""

    print(f"正在总结：{paper['title'][:50]}...")
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        time.sleep(1)
        summary = clean_markdown(extract_response_text(response))
        if not summary:
            summary = fallback_summary(paper)
    except genai_errors.ClientError as e:
        print(f"Gemini 调用失败，使用原始摘要兜底：{short_error_message(e)}")
        summary = fallback_summary(paper)
    except Exception as e:
        print(f"Gemini 网络或代理异常，使用原始摘要兜底：{short_error_message(e)}")
        summary = fallback_summary(paper)

    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(summary)
    return summary


def fallback_summary(paper: dict) -> str:
    """Gemini 额度不足时，仍输出规范 Markdown 结构。"""
    abstract = clean_text(paper.get("original_summary") or paper.get("summary", ""))
    short_abstract = abstract[:320] + ("..." if len(abstract) > 320 else "")
    return "\n".join(
        [
            "**一句话概括**",
            "",
            short_abstract,
            "",
            "**主要贡献**",
            "",
            "- 原始摘要已保留，建议阅读下方英文摘要确认研究目标、方法和结论。",
            "",
            "**创新点**",
            "",
            "- 当前 AI 摘要暂不可用，暂未自动提取创新点。",
        ]
    )


def short_error_message(error: Exception) -> str:
    """把 SDK 的大段 JSON 错误压成适合控制台展示的一句话。"""
    status_code = getattr(error, "status_code", None)
    message = str(error).splitlines()[0]
    if "RESOURCE_EXHAUSTED" in message:
        return f"{status_code or 429} Gemini 额度或频率受限"
    if "UNAVAILABLE" in message:
        return f"{status_code or 503} Gemini 服务繁忙"
    return message[:120]


def markdown_escape(text: str) -> str:
    """避免标题里的竖线破坏 Markdown 表格。"""
    return clean_text(text).replace("|", "\\|")


def build_briefing(papers: list[dict]) -> str:
    """把论文列表拼成结构化 Markdown 简报。"""
    now = datetime.now()
    lines = [
        f"# Arxiv 每日论文简报",
        "",
        f"> 生成日期：{now.strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> 论文数量：{len(papers)} 篇  ",
        f"> 主题范围：天体物理、系外行星、恒星物理、星系、宇宙学、高能天体物理",
        "",
        "## 今日速览",
        "",
        "| 序号 | 标题 | 分类 | 日期 |",
        "| --- | --- | --- | --- |",
    ]

    for index, paper in enumerate(papers, 1):
        categories = ", ".join(paper.get("categories", [])) or "N/A"
        published = paper.get("published", "")[:10] or "N/A"
        lines.append(
            f"| {index} | {markdown_escape(paper['title'])} | {markdown_escape(categories)} | {published} |"
        )

    lines.extend(["", "## 论文简报", ""])

    for index, paper in enumerate(papers, 1):
        authors = paper.get("authors", [])
        author_text = ", ".join(authors[:6]) if authors else "N/A"
        if len(authors) > 6:
            author_text += f" 等 {len(authors)} 人"

        categories = ", ".join(paper.get("categories", [])) or "N/A"
        published = paper.get("published", "")[:10] or "N/A"
        updated = paper.get("updated", "")[:10] or published
        original_summary = clean_text(paper.get("original_summary") or paper.get("summary", ""))

        lines.extend(
            [
                f"### {index}. {paper['title']}",
                "",
                f"- **Arxiv 链接**：[{paper['link']}]({paper['link']})",
                f"- **发表日期**：{published}",
                f"- **更新日期**：{updated}",
                f"- **作者**：{author_text}",
                f"- **分类**：{categories}",
                "",
                "#### 中文简报",
                "",
                paper["summary"],
                "",
                "#### 建议关注点",
                "",
                "- 这篇论文的核心问题是什么，是否和自己的研究方向有关。",
                "- 它使用的数据、模型或观测手段是否值得复用。",
                "- 结论是否依赖特定假设，后续阅读原文时应重点核查。",
                "",
                "<details>",
                "<summary>原始英文摘要</summary>",
                "",
                original_summary,
                "",
                "</details>",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## 使用说明",
            "",
            "- 中文简报由 Gemini 根据 Arxiv 摘要自动生成，只适合作为快速筛选材料。",
            "- 正式引用、报告或组会分享前，应打开 Arxiv 原文核对方法、数据和结论。",
            "- 如果当天重复运行程序，会优先使用 `.cache/` 中的 Arxiv 元数据缓存，减少触发限流。",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    setup()
    print("Arxiv 论文每日简报系统启动")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("请先在 .env 中设置 GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    papers = load_or_fetch_papers()[:MAX_PAPERS]
    for paper in papers:
        paper["original_summary"] = paper["summary"]
        paper["summary"] = summarize_with_gemini(client, paper)

    briefing = build_briefing(papers)
    filename = os.path.join(BASE_DIR, f"arxiv_briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(briefing)

    print("\n" + briefing)
    print(f"\n简报已保存到文件：{filename}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序运行失败：{e}")
