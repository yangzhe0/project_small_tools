"""Generate current documentation and the local results index from shared outputs."""
from pathlib import Path
from collections import Counter
import csv
import html
import json
from PIL import Image

from paths import ROOT, DATA, FIGURES, REPORTS

def rows(name):
    with (DATA/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def report_links(text):
    import re
    def rewrite(match):
        label, target = match.groups()
        if target.endswith('.csv') or target == 'pipeline_manifest.json':
            target = '../data/' + target
        elif target.endswith('.png'):
            target = '../figures/' + target
        elif target == '目录索引.html':
            target = '../目录索引.html'
        elif target.startswith('resources/'):
            target = '../inputs/' + target
        return f'[{label}]({target})'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rewrite, text)


def main():
    stats=rows('satellite_statistics.csv');ledger=rows('catalogue_source_ledger.csv');sites=rows('observatory_satellite_summary.csv')
    countries=rows('country_satellite_summary.csv');manifest=json.loads((DATA/'pipeline_manifest.json').read_text(encoding='utf-8'))
    totals=manifest['totals'];china=[r for r in sites if r['country']=='China']
    space=totals['space_entries'];unknown=totals['unresolved_entries'];ground=totals['mapped_entries']
    pct=100*totals['selected_team_entries']/totals['selected_entries']
    metric='已知重叠调整后的目录位置条目（尚非全库唯一观测数）'
    lines=[
        '# IMCCE_MAP 修复交付与统计口径说明', '',
        '日期：2026-10-19。当前版本采用逐来源可追溯账本，修复已知程序错误，并把无法由现有证据确认的科学定义保留为待核项。当前仅保留核对后的正式图件、复现代码与来源账本；已清理被替代的图件、重复入口和历史审计临时文件。', '',
        f'**主图口径：{metric}。团队 {totals["selected_team_entries"]:,}，全球 {totals["selected_entries"]:,}，占比 {pct:.2f}%。**', '',
        f'累计参考值（保留在数据表中，不再另出柱状图）：团队逐篇累计 {totals["raw_team_entries"]:,}；仅卫星目录累计 {totals["satellite_entries"]:,}（已排除海王星本体），占比 {100*totals["raw_team_entries"]/totals["satellite_entries"]:.2f}%。当前图件统一使用选用口径；不能把累计分子与调整后的分母混搭。', '',
        '## 已完成的修复', '',
        '- 历史星表固定列保持原始行首空格；086/786、036/536 不再因 strip 错位。其余星表仅读取本来源 Format 明确指出的台站字段；取消任意三字符反向匹配。',
        '- Gaia、Cassini、WISE 卫星任务、Voyager（含历史拼写 Voager）、Hipparcos 先按来源身份隔离；地面 Wise 天文台不会被关键词误排。零向量无法进入地面图。',
        '- O49 恢复为云南姚安站；M22、T05、T08、W68、W84、I41 等恢复为经 MPC 原始数值核对的台站资料。坐标从视差常数做含高度的 WGS-84 ECEF 逆算，国家推断与直接身份依据分别标注。',
        '- nm0090 海王星本体从所有选用统计及地图中排除；nm0091 按 Yan 2025 已发表成果纳入。作者归属按明确星表白名单；Shang/Peng 的 jo0078 只进入全球统计。',
        '- 重叠调整同时作用于团队分子和全球分母：排除 sm0034 合集；保留 Camargo 2022/um0138 的 Gaia EDR3 新归算，排除对应旧版 um0124/25；N2 以 nm1032 替换其包含的 nm1019；N1 等指定重归算组按精确时刻逐行对应。',
        '- 取消最大余数法和比例补足：每条未知记录与目录/TXT 数量差异单独保留。所有输入逐来源、逐系统守恒。',
        '- 当前柱状图、七张地图、报告同源生成。柱状图保留原版配色、布局及 30,000 阈值的 symlog 坐标，仅替换为核对后的选用数据；地图采用确认的 A 版：世界地图为主、中国局部插图，标题只保留系统编号，上下字体与柱状图统一。', '',
        '## 图件含义', '',
        '- 柱状图：蓝柱为团队，灰柱为全球，全球包含团队；两者均使用已知重叠调整后的选用口径。',
        '- 地图：全球已定位地面台站的数据分布；红点为中国台站，蓝点为其他地区台站。中国台站不等于本团队。',
        '- 地图中的 China 百分比以已定位地面条目为分母，不是团队占比；空间与未定位记录不画在地图上。', '',
        '## 六系统对账', '',
        '| 系统 | 卫星目录累计 | 团队累计 | 选用条目 | 选用团队 | 选用占比 | 地面定位 | 空间 | 待核 |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in stats:
        lines.append('| '+r['system']+' | '+' | '.join(f'{int(r[k]):,}' for k in ['satellite_entries','raw_team_entries','selected_entries','selected_team_entries'])+f' | {float(r["selected_team_pct"]):.2f}% | '+' | '.join(f'{int(r[k]):,}' for k in ['mapped_entries','space_entries','unresolved_entries'])+' |')
    lines += ['',f'全流程：**{totals["raw_input_entries"]:,} 原始输入 = {totals["selected_entries"]:,} 选用 + {totals["excluded_entries"]:,} 明确排除**。',
              f'选用条目：**{totals["selected_entries"]:,} = {ground:,} 已定位地面 + {space:,} 空间 + {unknown:,} 待核**。逐来源及逐系统残差均为零。', '',
              '## 每项排除的依据与数量', '', '| 星表 | 排除条目 | 规则 |','| --- | ---: | --- |']
    for r in ledger:
        if int(r['excluded_count']):
            reason=manifest['policy']['full_exclusions'].get(r['file_id'],'仅删除与指定较新归算精确同日历时刻/站点或 JD/目标的匹配行；其余旧行保留')
            lines.append(f'| {r["file_id"]} | {int(r["excluded_count"]):,} | {reason} |')
    lines += ['', '逐行排除清单见 [excluded_records.csv](excluded_records.csv)；规则见 [counting_policy.json](resources/counting_policy.json)。选择新旧归算版本会改变条目数，这不是一条固定的“全球独立观测数”。', '',
              '## 地面台站结果', '',f'当前共有 {len(sites)} 个已定位地面台站代码。中国 {len(china)} 个，累计选用条目 {sum(int(r["total_obs"]) for r in china):,}；这些计数覆盖地点，不能将其全部自动等同于该地某一口径望远镜。', '',
              '| 站码 | 地点 | 经度 | 大地纬度 | 选用条目 |', '| --- | --- | ---: | ---: | ---: |']
    names={'286':'云南昆明','337':'上海佘山','O44':'云南丽江','O49':'紫金山天文台云南姚安站','327':'兴隆','D29':'盱眙','334':'青岛'}
    for r in china:lines.append(f'| {r["code"]} | {names.get(r["code"],r["name"])} | {r["longitude"]} | {r["latitude"]} | {int(r["total_obs"]):,} |')
    lines += ['', '国家/地区汇总（包含明确标为 Natural Earth 推断的归属；未解析台站未参与排名）：', '', '| 国家/地区 | 选用地面条目 | 台站代码数 |', '| --- | ---: | ---: |']
    for r in countries:lines.append(f'| {r["country"]} | {int(r["total_obs"]):,} | {r["station_count"]} |')
    lines += ['', '## 科学证据边界', '',
              '以下不是待修复的程序报错，而是现有资料不足以认证的科学内容；已经从图表标题和报告中删除“严格全库去重”“最终独立观测数”“100%科学认证”等表述。', '',
              '- 仍有部分重归算对应关系未建立，完整清单位于 pipeline_manifest.json。尤其 sm0074/sm0079 与早期星表、sm0084 的部分重归算、不同 Gaia 版本和 PHESAT 目标/参考卫星双计不能简单整表相减。',
              '- sm0053/54 的索引注释称有 44 个共有位置，本地原始文件仅有 3 个精确 JD/目标匹配；只删除这 3 条，没有猜测其余 41 条。',
              '- N1 的 nm0015 与 nm0088 对应 912 条旧记录，nm0085 对应 969 条；不一致时刻未按任意容差删除。nm0088 入库 1,006 与原论文 1,007 的差异继续保留。N2 根据原始说明确认 nm1019 全部 112 条被 nm1032 包含。',
              '- Zhang 2024 的 10,339 条按论文和工作簿的站点汇总纳入；没有本地原始观测文件或确认的 IMCCE 星表 ID，不能说已逐条复算或确认正式入库。',
              '- sm0084 目录 7,387 条，本地 TXT 6,487 行；根据其 telescope 定义定位原始行，其余 900 条保留为目录/原始数据差额。um0034 的非零目录目标为 U1–U3，本地多出的 231 行 Miranda 单列存档；所选原始行与目录仍差 6 条，保持未知。',
              '- 台站全目录在线下载失败，使用固定的原目录及官方检索数值补充；不宣称实时完整。经纬度的小数位是计算输出精度，不是对真实望远镜位置的同等测量精度承诺。',
              '- 待核项包括无台站字段、未确认坐标与计数/范围差异。数据均保留；不通过比例分摊消除未知。', '',
              '## 验证与复现', '',
              '现有 Windows 解释器：`C:\\Software\\Code\\Python\\python.exe`；无新增安装。也可使用已具备 openpyxl、matplotlib、pandas、numpy、Pillow 的 Python 环境，外部原始星表目录用 IMCCE_RAW_DIR 指定。代码位于 scripts/，输入位于 inputs/，统计账本位于 data/，图件位于 figures/，报告位于 reports/。脚本不依赖启动目录。', '',
              '```powershell', 'python scripts/rebuild_all.py','```','',
              '测试覆盖：原始固定列、混合台站、空间身份、地面 Wise 反例、坐标前向/逆向核对、作者边界、逐行排除、来源和分类守恒、未知不分摊、图表同源、八张 PNG 高度及完整性、隔离目录完整重建的逐字节一致性。通过仅说明这些检查成立，不代表上述待核定义已获认证。', '',
              '## 图件与复查文件', '', '| 文件 | 宽×高 px |','| --- | ---: |']
    from generate_all_satellite_maps import CONFIG
    pngs=['number.png']+[r[2] for r in CONFIG]
    for name in pngs:
        with Image.open(FIGURES/name) as im:lines.append(f'| [{name}]({name}) | {im.width}×{im.height} |')
    lines += ['', '- [本地可视化目录](目录索引.html)：打开即可查看当前柱状图和全部分类图。',
              '- [satellite_statistics.csv](satellite_statistics.csv)：唯一汇总入口；[catalogue_source_ledger.csv](catalogue_source_ledger.csv)：逐来源总账。',
              '- [record_classification.csv](record_classification.csv)：原始行号、分配、空间、待核与排除依据。',
              '- [unresolved_records_flagged.csv](unresolved_records_flagged.csv)：空间与未知分列；[raw_records_outside_catalogue_scope.csv](raw_records_outside_catalogue_scope.csv)：目录范围外原始行。',
              '- [pipeline_manifest.json](pipeline_manifest.json)：输入 SHA256、规则版本、限制清单；[resources/README.md](resources/README.md)：固定资料来源说明。',
              '- [verification.log](verification.log)：当前完整验证结果。', '',
              '本地整理仅保留当前版本。IMCCE_QIAO 旧目录、重复图、错误累计版柱图、过时的时间图与历史审计临时文件已清理；原始工作簿、固定资源、逐行账本与外部原始星表保留。无新增安装、commit、push 或部署。']
    (REPORTS/'DATA_LINEAGE_REPORT.md').write_text(report_links('\n'.join(lines)+'\n'),encoding='utf-8')
    china_doc=['# 中国台站选用条目汇总','','本报告由统一账本生成；口径、排除与待核条件见 [DATA_LINEAGE_REPORT.md](DATA_LINEAGE_REPORT.md)。台站计数不自动等同于某一口径望远镜的观测量。','',
               '| 代码 | 地点 | J6–J13 | S1–S8 | S9 | U1–U5 | N1 | N2 | 合计 |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in china:china_doc.append('| '+r['code']+' | '+names.get(r['code'],r['name'])+' | '+' | '.join(f'{int(r[k]):,}' for k in ['J6-13','S1-8','S9','U1-5','N1','N2','total_obs'])+' |')
    (REPORTS/'china_observatories_report.md').write_text('\n'.join(china_doc)+'\n',encoding='utf-8')
    labels=['团队与全球柱状图']+[title for _,title,_ in CONFIG]
    links=''.join(f'<a href="#{i}">{html.escape(label)}</a>' for i,label in enumerate(labels))
    imgs=''.join(f'<section id="{i}"><h2>{html.escape(labels[i])}</h2><a href="figures/{html.escape(n)}"><img src="figures/{html.escape(n)}" alt="{html.escape(n)}"></a></section>' for i,n in enumerate(pngs))
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IMCCE 卫星目录统计与地图</title><style>body{{font:16px/1.6 system-ui;margin:0;background:#f1f5f9;color:#172033}}main{{max-width:1400px;margin:auto;padding:32px}}header,section{{background:white;padding:24px;margin:20px 0;border-radius:12px}}h1{{margin:0}}h2{{font-size:18px}}img{{display:block;width:100%;height:auto}}nav a{{display:inline-block;margin:4px 16px 4px 0}}a{{color:#0369a1}}.note{{border-left:4px solid #0ea5e9;padding-left:18px}}</style><main><header><h1>IMCCE 卫星目录统计与地图</h1><p>2026-10-19 · 来源可追溯 · 图件统一高 2350 px</p><p class="note">主图为已知重叠调整后的目录位置条目，仍有待核重归算关系。团队 {totals['selected_team_entries']:,} / 全球 {totals['selected_entries']:,} = {pct:.2f}%；这不是已认证的唯一观测份额。</p><p>柱状图：蓝柱为团队，灰柱为全球（包含团队）。地图：红点为中国台站，蓝点为其他地区台站；中国台站不等于本团队。地图展示已定位地面条目 {ground:,}，空间 {space:,} 与待核 {unknown:,} 不画在地图上。</p><p><a href="reports/DATA_LINEAGE_REPORT.md">交付与口径说明</a> · <a href="data/satellite_statistics.csv">六系统统计 CSV</a> · <a href="data/pipeline_manifest.json">来源与规则清单</a> · <a href="reports/verification.log">验证日志</a></p><nav>{links}</nav></header>{imgs}</main></html>'''
    (ROOT/'目录索引.html').write_text(page,encoding='utf-8')
    print('Updated current report, China summary and local visual index.')


if __name__=='__main__':main()
