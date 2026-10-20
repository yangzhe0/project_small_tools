# IMCCE_MAP 修复交付与统计口径说明

日期：2026-10-19。当前版本采用逐来源可追溯账本，修复已知程序错误，并把无法由现有证据确认的科学定义保留为待核项。当前仅保留核对后的正式图件、复现代码与来源账本；已清理被替代的图件、重复入口和历史审计临时文件。

**主图口径：已知重叠调整后的目录位置条目（尚非全库唯一观测数）。团队 30,535，全球 213,638，占比 14.29%。**

累计参考值（保留在数据表中，不再另出柱状图）：团队逐篇累计 32,528；仅卫星目录累计 254,527（已排除海王星本体），占比 12.78%。当前图件统一使用选用口径；不能把累计分子与调整后的分母混搭。

## 已完成的修复

- 历史星表固定列保持原始行首空格；086/786、036/536 不再因 strip 错位。其余星表仅读取本来源 Format 明确指出的台站字段；取消任意三字符反向匹配。
- Gaia、Cassini、WISE 卫星任务、Voyager（含历史拼写 Voager）、Hipparcos 先按来源身份隔离；地面 Wise 天文台不会被关键词误排。零向量无法进入地面图。
- O49 恢复为云南姚安站；M22、T05、T08、W68、W84、I41 等恢复为经 MPC 原始数值核对的台站资料。坐标从视差常数做含高度的 WGS-84 ECEF 逆算，国家推断与直接身份依据分别标注。
- nm0090 海王星本体从所有选用统计及地图中排除；nm0091 按 Yan 2025 已发表成果纳入。作者归属按明确星表白名单；Shang/Peng 的 jo0078 只进入全球统计。
- 重叠调整同时作用于团队分子和全球分母：排除 sm0034 合集；保留 Camargo 2022/um0138 的 Gaia EDR3 新归算，排除对应旧版 um0124/25；N2 以 nm1032 替换其包含的 nm1019；N1 等指定重归算组按精确时刻逐行对应。
- 取消最大余数法和比例补足：每条未知记录与目录/TXT 数量差异单独保留。所有输入逐来源、逐系统守恒。
- 当前柱状图、七张地图、报告同源生成。柱状图保留原版配色、布局及 30,000 阈值的 symlog 坐标，仅替换为核对后的选用数据；地图采用确认的 A 版：世界地图为主、中国局部插图，标题只保留系统编号，上下字体与柱状图统一。

## 图件含义

- 柱状图：蓝柱为团队，灰柱为全球，全球包含团队；两者均使用已知重叠调整后的选用口径。
- 地图：全球已定位地面台站的数据分布；红点为中国台站，蓝点为其他地区台站。中国台站不等于本团队。
- 地图中的 China 百分比以已定位地面条目为分母，不是团队占比；空间与未定位记录不画在地图上。

## 六系统对账

| 系统 | 卫星目录累计 | 团队累计 | 选用条目 | 选用团队 | 选用占比 | 地面定位 | 空间 | 待核 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| J6-13 | 28,091 | 2,993 | 28,091 | 2,993 | 10.65% | 21,740 | 5,686 | 665 |
| S1-8 | 120,949 | 3,261 | 94,552 | 3,261 | 3.45% | 74,521 | 16,224 | 3,807 |
| S9 | 9,188 | 2,202 | 9,188 | 2,202 | 23.97% | 7,276 | 1,808 | 104 |
| U1-5 | 74,309 | 14,636 | 61,810 | 14,636 | 23.68% | 57,432 | 2,946 | 1,432 |
| N1 | 18,738 | 9,034 | 16,857 | 7,153 | 42.43% | 16,226 | 621 | 10 |
| N2 | 3,252 | 402 | 3,140 | 290 | 9.24% | 2,434 | 691 | 15 |

全流程：**256,445 原始输入 = 213,638 选用 + 42,807 明确排除**。
选用条目：**213,638 = 179,629 已定位地面 + 27,976 空间 + 6,033 待核**。逐来源及逐系统残差均为零。

## 每项排除的依据与数量

| 星表 | 排除条目 | 规则 |
| --- | ---: | --- |
| sm0034 | 26,394 | known_overlap: composite of retained sm0035 and sm0036; msapomai comment 1 |
| sm0053 | 3 | 仅删除与指定较新归算精确同日历时刻/站点或 JD/目标的匹配行；其余旧行保留 |
| um0124 | 2,702 | known_overlap: earlier reduction replaced by retained um0138 Gaia EDR3 reanalysis; um0138 comment 1 |
| um0125 | 9,797 | known_overlap: earlier reduction replaced by retained um0138 Gaia EDR3 reanalysis; um0138 comment 1 |
| nm0015 | 912 | 仅删除与指定较新归算精确同日历时刻/站点或 JD/目标的匹配行；其余旧行保留 |
| nm0085 | 969 | 仅删除与指定较新归算精确同日历时刻/站点或 JD/目标的匹配行；其余旧行保留 |
| nm0090 | 1,918 | non_satellite: Neptune planet positions; mnepomai note *2 and nm0090 Format |
| nm1019 | 112 | known_overlap: all 112 positions also in retained newer nm1032; nm1032 Comments |

逐行排除清单见 [excluded_records.csv](../data/excluded_records.csv)；规则见 [counting_policy.json](../inputs/resources/counting_policy.json)。选择新旧归算版本会改变条目数，这不是一条固定的“全球独立观测数”。

## 地面台站结果

当前共有 164 个已定位地面台站代码。中国 7 个，累计选用条目 39,722；这些计数覆盖地点，不能将其全部自动等同于该地某一口径望远镜。

| 站码 | 地点 | 经度 | 大地纬度 | 选用条目 |
| --- | --- | ---: | ---: | ---: |
| 286 | 云南昆明 | 102.7883 | 25.025447 | 24,568 |
| 337 | 上海佘山 | 121.1843 | 31.095924 | 11,991 |
| O44 | 云南丽江 | 100.02973 | 26.695087 | 1,490 |
| 327 | 兴隆 | 117.575 | 40.394236 | 1,087 |
| D29 | 盱眙 | 118.4639 | 32.734363 | 495 |
| O49 | 紫金山天文台云南姚安站 | 101.18111 | 25.528605 | 81 |
| 334 | 青岛 | 120.3196 | 36.069981 | 10 |

国家/地区汇总（包含明确标为 Natural Earth 推断的归属；未解析台站未参与排名）：

| 国家/地区 | 选用地面条目 | 台站代码数 |
| --- | ---: | ---: |
| USA | 48,524 | 55 |
| Brazil | 42,077 | 2 |
| China | 39,722 | 7 |
| Russia | 19,061 | 7 |
| France | 5,659 | 11 |
| Spain | 5,185 | 6 |
| Germany | 3,246 | 9 |
| Romania | 2,537 | 1 |
| Chile | 2,278 | 6 |
| Ukraine | 2,150 | 3 |
| UK | 2,108 | 7 |
| Australia | 2,082 | 6 |
| South Africa | 1,707 | 4 |
| Japan | 1,193 | 7 |
| Georgia | 951 | 1 |
| Uzbekistan | 403 | 3 |
| Morocco | 133 | 1 |
| Armenia | 130 | 2 |
| Slovenia | 89 | 1 |
| Egypt | 84 | 1 |
| Unknown | 81 | 1 |
| Switzerland | 61 | 5 |
| Argentina | 44 | 2 |
| Belgium | 29 | 1 |
| Italy | 26 | 5 |
| Croatia | 23 | 1 |
| Mexico | 15 | 1 |
| Portugal | 8 | 1 |
| Taiwan | 7 | 1 |
| Slovakia | 5 | 1 |
| Hungary | 3 | 1 |
| Kazakhstan | 3 | 1 |
| Israel | 2 | 1 |
| Venezuela | 2 | 1 |
| Peru | 1 | 1 |

## 科学证据边界

以下不是待修复的程序报错，而是现有资料不足以认证的科学内容；已经从图表标题和报告中删除“严格全库去重”“最终独立观测数”“100%科学认证”等表述。

- 仍有部分重归算对应关系未建立，完整清单位于 pipeline_manifest.json。尤其 sm0074/sm0079 与早期星表、sm0084 的部分重归算、不同 Gaia 版本和 PHESAT 目标/参考卫星双计不能简单整表相减。
- sm0053/54 的索引注释称有 44 个共有位置，本地原始文件仅有 3 个精确 JD/目标匹配；只删除这 3 条，没有猜测其余 41 条。
- N1 的 nm0015 与 nm0088 对应 912 条旧记录，nm0085 对应 969 条；不一致时刻未按任意容差删除。nm0088 入库 1,006 与原论文 1,007 的差异继续保留。N2 根据原始说明确认 nm1019 全部 112 条被 nm1032 包含。
- Zhang 2024 的 10,339 条按论文和工作簿的站点汇总纳入；没有本地原始观测文件或确认的 IMCCE 星表 ID，不能说已逐条复算或确认正式入库。
- sm0084 目录 7,387 条，本地 TXT 6,487 行；根据其 telescope 定义定位原始行，其余 900 条保留为目录/原始数据差额。um0034 的非零目录目标为 U1–U3，本地多出的 231 行 Miranda 单列存档；所选原始行与目录仍差 6 条，保持未知。
- 台站全目录在线下载失败，使用固定的原目录及官方检索数值补充；不宣称实时完整。经纬度的小数位是计算输出精度，不是对真实望远镜位置的同等测量精度承诺。
- 待核项包括无台站字段、未确认坐标与计数/范围差异。数据均保留；不通过比例分摊消除未知。

## 验证与复现

现有 Windows 解释器：`C:\Software\Code\Python\python.exe`；无新增安装。也可使用已具备 openpyxl、matplotlib、pandas、numpy、Pillow 的 Python 环境，外部原始星表目录用 IMCCE_RAW_DIR 指定。代码位于 scripts/，输入位于 inputs/，统计账本位于 data/，图件位于 figures/，报告位于 reports/。脚本不依赖启动目录。

```powershell
python scripts/rebuild_all.py
```

测试覆盖：原始固定列、混合台站、空间身份、地面 Wise 反例、坐标前向/逆向核对、作者边界、逐行排除、来源和分类守恒、未知不分摊、图表同源、八张 PNG 高度及完整性、隔离目录完整重建的逐字节一致性。通过仅说明这些检查成立，不代表上述待核定义已获认证。

## 图件与复查文件

| 文件 | 宽×高 px |
| --- | ---: |
| [number.png](../figures/number.png) | 3420×2350 |
| [global_satellite_observations_map.png](../figures/global_satellite_observations_map.png) | 4804×2350 |
| [map_J6-J13_jupiter_satellites.png](../figures/map_J6-J13_jupiter_satellites.png) | 4804×2350 |
| [map_S1-S8_saturn_satellites.png](../figures/map_S1-S8_saturn_satellites.png) | 4804×2350 |
| [map_S9_phoebe.png](../figures/map_S9_phoebe.png) | 4804×2350 |
| [map_U1-U5_uranus_satellites.png](../figures/map_U1-U5_uranus_satellites.png) | 4804×2350 |
| [map_N1_triton.png](../figures/map_N1_triton.png) | 4804×2350 |
| [map_N2_nereid.png](../figures/map_N2_nereid.png) | 4804×2350 |

- [本地可视化目录](../目录索引.html)：打开即可查看当前柱状图和全部分类图。
- [satellite_statistics.csv](../data/satellite_statistics.csv)：唯一汇总入口；[catalogue_source_ledger.csv](../data/catalogue_source_ledger.csv)：逐来源总账。
- [record_classification.csv](../data/record_classification.csv)：原始行号、分配、空间、待核与排除依据。
- [unresolved_records_flagged.csv](../data/unresolved_records_flagged.csv)：空间与未知分列；[raw_records_outside_catalogue_scope.csv](../data/raw_records_outside_catalogue_scope.csv)：目录范围外原始行。
- [pipeline_manifest.json](../data/pipeline_manifest.json)：输入 SHA256、规则版本、限制清单；[resources/README.md](../inputs/resources/README.md)：固定资料来源说明。
- [verification.log](verification.log)：当前完整验证结果。

本地整理仅保留当前版本。IMCCE_QIAO 旧目录、重复图、错误累计版柱图、过时的时间图与历史审计临时文件已清理；原始工作簿、固定资源、逐行账本与外部原始星表保留。无新增安装、commit、push 或部署。
