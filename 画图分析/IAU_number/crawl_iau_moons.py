import sys
import re
import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 目标数据源（NASA Science Moons Facts 完整列表指向的 JPL SSD 权威数据源）
URL = "https://ssd.jpl.nasa.gov/sats/discovery.html"

def clean_year(year_str):
    """
    处理可能出现的多年份情况（例如 '1975, 2000' -> 2000），提取有效四位年份整数
    """
    if not year_str:
        return ""
    years = re.findall(r"\b\d{4}\b", str(year_str))
    if years:
        # 取最新确认年份（与原始数据集对齐）
        return int(years[-1])
    return year_str

def fetch_moons_data(output_file="IAU_number.csv"):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    
    print(f"正在从 NASA JPL SSD 爬取最新卫星发现数据: {URL} ...")
    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="sat-discovery")
    if not table:
        raise ValueError("未在页面中找到目标数据表格 (table.sat-discovery)")
    
    rows = []
    current_planet = ""
    
    for tr in table.find("tbody").find_all("tr"):
        classes = tr.get("class", [])
        if "sat-discovery-planet" in classes:
            planet_text = tr.get_text(strip=True)
            # 提取行星名称（如 Mars, Jupiter, Saturn, Uranus, Neptune, Pluto 等）
            m = re.search(r"Satellites of\s+(?:Dwarf Planet\s+(?:\(\d+\)\s+)?)?([A-Za-z]+)", planet_text)
            if m:
                current_planet = m.group(1).capitalize()
            else:
                current_planet = planet_text.replace("Satellites of", "").split(":")[0].strip()
        else:
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(tds) >= 6:
                raw_year = tds[3]
                parsed_year = clean_year(raw_year)
                rows.append({
                    "IAU number": tds[0],
                    "IAU name": tds[1],
                    "Provisional designation": tds[2],
                    "Year discovered": parsed_year,
                    "Discoverer(s)/spacecraft mission": tds[4],
                    "References": tds[5],
                    "Satellite": current_planet
                })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"[OK] 爬取成功！已保存至 {output_file}，共抓取 {len(df)} 颗卫星数据。")
    print("\n各大天体卫星数量统计：")
    print(df["Satellite"].value_counts().to_string())
    return df

if __name__ == "__main__":
    target = "IAU_number.csv" if len(sys.argv) < 2 else sys.argv[1]
    fetch_moons_data(target)
