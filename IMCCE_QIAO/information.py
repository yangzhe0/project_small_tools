import os
import csv
import re

def parse_html(path):
    info = {
        "planet": "",
        "dates": "",
        "type": "",
        "observatory": "no informations",
        "total_number": ""
    }
    obs_list = []
    in_obs = False

    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            l = line.strip()
            low = l.lower()

            # planet
            if low.startswith("planet:"):
                # e.g. "planet: 5 - Jupiter"
                if "jupiter" in low: info["planet"] = "J"
                elif "saturn" in low: info["planet"] = "S"
                elif "uranus" in low: info["planet"] = "U"
                elif "neptune" in low: info["planet"] = "N"
                elif "mars" in low: info["planet"] = "M"
                elif "pluto" in low: info["planet"] = "P"
                else: info["planet"] = l.split(":",1)[1].strip()

            # dates
            elif low.startswith("dates:"):
                info["dates"] = l.split(":",1)[1].strip()

            # type
            elif low.startswith("type:"):
                info["type"] = l.split(":",1)[1].strip()

            # total number
            elif low.startswith("total number"):
                m = re.search(r"(\d+)", l)
                if m: info["total_number"] = int(m.group(1))

            # observatory
            elif low.startswith("observatory:"):
                in_obs = True
                part = l.split(":",1)[1].strip()
                if part: obs_list.append(part)
            elif in_obs:
                if l and not l.startswith("---"):
                    obs_list.append(l)
                else:
                    in_obs = False

    if obs_list:
        info["observatory"] = "; ".join(obs_list)

    return info

def count_txt_lines(path):
    count = 0
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                count += 1
    return count

def main(base_dir=".", output="summary.csv"):
    rows = []
    for root, _, files in os.walk(base_dir):
        for fn in files:
            if fn.endswith(".html"):
                file_id = os.path.splitext(fn)[0]
                html_path = os.path.join(root, fn)
                txt_path = os.path.join(root, file_id + ".txt")

                info = parse_html(html_path)
                txt_lines = count_txt_lines(txt_path) if os.path.exists(txt_path) else 0
                total = info["total_number"] if info["total_number"] else 0
                diff = total - txt_lines if total else ""

                rows.append({
                    "planet": info["planet"],
                    "file": file_id,
                    "dates": info["dates"],
                    "lines(txt)": txt_lines,
                    "total(html)": total,
                    "total(html)-lines(txt)": diff,
                    "type": info["type"],
                    "observatory": info["observatory"]
                })

    if not rows:
        print("没有找到 html 文件！")
        return

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter=",")
        writer.writeheader()
        writer.writerows(rows)

    print(f"已生成 {output}，共 {len(rows)} 条记录。")

if __name__ == "__main__":
    main("data", "summary.csv")
