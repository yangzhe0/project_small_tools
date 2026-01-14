import requests
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime
from typing import List, Dict
import time

# 使用官方 google-genai 库
from google import genai

class ArxivBriefingGenerator:
    def __init__(self, gemini_api_key: str):
        """初始化简报生成器"""
        self.gemini_api_key = gemini_api_key
        # 设置环境变量
        os.environ['GEMINI_API_KEY'] = gemini_api_key
        # 初始化客户端
        self.client = genai.Client()
        
    def fetch_arxiv_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        从 Arxiv 获取论文数据
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            论文列表，包含标题、摘要、链接等信息
        """
        try:
            # 构建 Arxiv API URL
            url = f'http://export.arxiv.org/api/query'
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            print(f"正在获取 Arxiv 论文数据...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析 XML 响应
            root = ET.fromstring(response.content)
            papers = []
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                try:
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                    link_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                    published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                    
                    if title_elem is not None and summary_elem is not None and link_elem is not None:
                        paper = {
                            'title': title_elem.text.strip(),
                            'summary': summary_elem.text.strip(),
                            'link': link_elem.text.strip(),
                            'published': published_elem.text.strip() if published_elem is not None else 'Unknown'
                        }
                        papers.append(paper)
                        
                except Exception as e:
                    print(f"解析论文条目时出错: {e}")
                    continue
            
            print(f"成功获取 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            print(f"获取 Arxiv 数据时出错: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """清理文本，移除多余的空白字符"""
        if not text:
            return ""
        # 移除多余的空白字符和换行
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def generate_summary(self, abstract: str, title: str = "") -> str:
        """
        使用 Gemini API 生成中文摘要
        
        Args:
            abstract: 论文摘要
            title: 论文标题
            
        Returns:
            中文摘要
        """
        try:
            # 清理文本
            clean_abstract = self.clean_text(abstract)
            clean_title = self.clean_text(title)
            
            # 构建提示词
            prompt = f"""请用中文总结以下论文，要求：
1. 字数控制在200字以内
2. 突出论文的主要贡献和创新点
3. 使用简洁明了的语言
4. 重点关注GAIA望远镜、观测星表、天体物理等相关内容

论文标题：{clean_title}

论文摘要：
{clean_abstract}

中文总结："""

            print(f"正在生成摘要: {clean_title[:50]}...")
            
            # 使用官方 google-genai 库
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # 添加延迟避免API限制
            time.sleep(1)
            
            return response.text.strip()
            
        except Exception as e:
            print(f"生成摘要时出错: {e}")
            return f"摘要生成失败: {str(e)}"
    
    def create_briefing(self, papers: List[Dict]) -> str:
        """
        创建简报内容
        
        Args:
            papers: 论文列表
            
        Returns:
            格式化的简报内容
        """
        if not papers:
            return "【Arxiv 每日论文简报】\n\n今日未找到相关论文。"
        
        date = datetime.now().strftime('%Y-%m-%d')
        briefing = f"【Arxiv 每日论文简报】{date}\n"
        briefing += "=" * 50 + "\n\n"
        
        for i, paper in enumerate(papers, 1):
            briefing += f"📄 论文 {i}:\n"
            briefing += f"标题：{paper['title']}\n"
            briefing += f"链接：{paper['link']}\n"
            briefing += f"发表日期：{paper['published'][:10]}\n"
            briefing += f"总结：{paper['summary']}\n"
            briefing += "-" * 40 + "\n\n"
        
        briefing += "（以上内容由 AI 自动生成，请注意核实）\n"
        briefing += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return briefing
    
    def generate_daily_briefing(self, max_papers: int = 5) -> str:
        """
        生成每日简报
        
        Args:
            max_papers: 最大论文数量
            
        Returns:
            完整的简报内容
        """
        # 构建搜索查询，专注于GAIA和天体物理相关
        queries = [
            "cat:astro-ph",
            "cat:astro-ph.EP", 
            "cat:astro-ph.SR",
            "cat:astro-ph.GA",
            "cat:astro-ph.CO",
            "cat:astro-ph.HE"
        ]
        
        all_papers = []
        
        for query in queries:
            papers = self.fetch_arxiv_papers(query, max_results=2)
            all_papers.extend(papers)
            
            # 避免重复
            if len(all_papers) >= max_papers:
                break
        
        # 去重并限制数量
        seen_titles = set()
        unique_papers = []
        for paper in all_papers:
            if paper['title'] not in seen_titles:
                seen_titles.add(paper['title'])
                unique_papers.append(paper)
                if len(unique_papers) >= max_papers:
                    break
        
        # 为每篇论文生成中文摘要
        print("正在生成中文摘要...")
        for paper in unique_papers:
            paper['summary'] = self.generate_summary(paper['summary'], paper['title'])
        
        # 创建简报
        briefing = self.create_briefing(unique_papers)
        return briefing

def main():
    """主函数"""
    print("🚀 Arxiv 论文每日简报系统启动")
    print("=" * 50)
    
    # 使用你提供的 API Key
    api_key = "REDACTED_GOOGLE_API_KEY"
    
    try:
        # 创建简报生成器
        generator = ArxivBriefingGenerator(api_key)
        
        # 生成简报
        briefing = generator.generate_daily_briefing(max_papers=5)
        
        # 输出简报
        print("\n" + "=" * 50)
        print("📋 每日简报生成完成")
        print("=" * 50)
        print(briefing)
        
        # 保存到文件
        filename = f"arxiv_briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(briefing)
        print(f"\n💾 简报已保存到文件: {filename}")
        
    except Exception as e:
        print(f"❌ 生成简报时出错: {e}")

if __name__ == "__main__":
    main()
