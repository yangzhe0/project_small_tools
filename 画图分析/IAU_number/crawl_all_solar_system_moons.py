"""
全太阳系天然卫星数据爬虫 (All Solar System Natural Satellites Crawler)
数据来源：NASA Science / NASA JPL Solar System Dynamics (SSD) 官方权威数据库
支持：
  1. 大行星与冥王星卫星 (Planetary Moons: 460 颗)
  2. 全太阳系小天体/矮行星/小行星卫星 (Small-Body Satellites: 531 颗)
  3. 全太阳系完整卫星数据库 (All Moons: 991 颗)
"""

import sys
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

URL_PLANETARY = "https://ssd.jpl.nasa.gov/sats/discovery.html"
URL_SMALL_BODIES = "https://ssd-api.jpl.nasa.gov/sb_sat.api"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def clean_year(year_str):
    if not year_str:
        return None
    years = re.findall(r"\b\d{4}\b", str(year_str))
    if years:
        return int(years[-1])
    return None

def fetch_planetary_moons():
    """爬取大行星及冥王星卫星 (460颗)"""
    print(f"正在从 NASA JPL SSD 爬取【大行星及冥王星卫星数据】: {URL_PLANETARY} ...")
    resp = requests.get(URL_PLANETARY, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", class_="sat-discovery")
    if not table:
        raise ValueError("未在页面中找到行星卫星表格 (table.sat-discovery)")
    
    rows = []
    current_planet = ""
    for tr in table.find("tbody").find_all("tr"):
        classes = tr.get("class", [])
        if "sat-discovery-planet" in classes:
            p_text = tr.get_text(strip=True)
            m = re.search(r"Satellites of\s+(?:Dwarf Planet\s+(?:\(\d+\)\s+)?)?([A-Za-z]+)", p_text)
            current_planet = m.group(1).capitalize() if m else p_text.replace("Satellites of", "").split(":")[0].strip()
        else:
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(tds) >= 6:
                rows.append({
                    "System Type": "Planetary Moon",
                    "Primary Body": current_planet,
                    "Orbit Class": "Major / Dwarf Planet",
                    "IAU number": tds[0],
                    "IAU name": tds[1],
                    "Provisional designation": tds[2],
                    "Year discovered": clean_year(tds[3]),
                    "Discoverer(s)/spacecraft mission": tds[4],
                    "References": tds[5],
                    "Satellite": current_planet
                })
    df = pd.DataFrame(rows)
    print(f"[OK] 成功抓取大行星及冥王星卫星共 {len(df)} 颗。")
    return df

def fetch_small_body_moons():
    """爬取全太阳系小行星、矮行星与海王星外天体卫星 (531颗)"""
    print(f"正在调用 NASA JPL 官方 REST API 抓取【小行星与小天体卫星数据】: {URL_SMALL_BODIES} ...")
    params = {"www": "1", "fullname": "1", "class": "1"}
    resp = requests.get(URL_SMALL_BODIES, params=params, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    data = resp.json()
    
    rows = []
    for item in data.get("data", []):
        sat = item.get("sat", {})
        parent = sat.get("fullname", "").strip()
        orbit_class = sat.get("class_name", sat.get("class", "Small Body"))
        
        prov_desig = sat.get("sat_fullname") or sat.get("pdes") or ""
        iau_name = sat.get("iau_name") or ""
        
        rows.append({
            "System Type": "Small-Body Moon",
            "Primary Body": parent,
            "Orbit Class": orbit_class,
            "IAU number": str(sat.get("iau_num")) if sat.get("iau_num") else "",
            "IAU name": iau_name,
            "Provisional designation": prov_desig,
            "Year discovered": clean_year(sat.get("prov_year")),
            "Discoverer(s)/spacecraft mission": sat.get("ref", ""),
            "References": sat.get("ref", ""),
            "Satellite": "Small-Body"
        })
    df = pd.DataFrame(rows)
    print(f"[OK] 成功抓取小天体/矮行星/小行星卫星共 {len(df)} 颗。")
    return df

def main(mode="all"):
    """
    mode:
      - 'planetary': 仅大行星卫星 (生成 IAU_number.csv)
      - 'all': 全太阳系全量卫星 (生成 all_solar_system_moons.csv 并同步更新 IAU_number.csv)
    """
    df_planets = fetch_planetary_moons()
    
    if mode == "planetary":
        output = "IAU_number.csv"
        df_planets.to_csv(output, index=False, encoding="utf-8")
        print(f"\n[Done] 已将大行星卫星数据输出至 {output}")
        return df_planets
    
    df_sb = fetch_small_body_moons()
    df_all = pd.concat([df_planets, df_sb], ignore_index=True)
    
    output_all = "all_solar_system_moons.csv"
    df_all.to_csv(output_all, index=False, encoding="utf-8")
    
    # 同时也更新原有的 IAU_number.csv 确保行星绘图程序兼容
    df_planets.to_csv("IAU_number.csv", index=False, encoding="utf-8")
    
    print("\n=======================================================")
    print(f"🎉 全太阳系天然卫星抓取完成！共收录 {len(df_all)} 颗卫星：")
    print(f"   1. 大行星与冥王星卫星: {len(df_planets)} 颗 (输出至 IAU_number.csv)")
    print(f"   2. 小行星/矮行星/TNO卫星: {len(df_sb)} 颗")
    print(f"   -> 全量数据已保存至: {output_all}")
    print("=======================================================")
    print("\n天体轨道分类统计 (Top 10):")
    print(df_all["Orbit Class"].value_counts().head(10).to_string())
    return df_all

if __name__ == "__main__":
    mode = "all" if len(sys.argv) < 2 else sys.argv[1]
    main(mode)
