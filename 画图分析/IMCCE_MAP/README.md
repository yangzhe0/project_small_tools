# IMCCE 卫星统计与图件

打开 [目录索引.html](目录索引.html) 查看当前柱状图和七张地图。

| 目录 | 内容 |
| --- | --- |
| figures/ | 当前正式图件，共 8 张；柱状图为 number.png |
| scripts/ | 当前统计、绘图、验证与报告代码 |
| inputs/ | 原始工作簿、固定台站/地图/规则资料、补充星表 |
| data/ | 六系统统计、逐来源账本、逐行分类与排除、来源清单 |
| reports/ | 科学口径说明、中国台站汇总、验证日志、整理记录 |

当前柱状图保留原版样式，使用已知重叠调整后的数据：团队 **30,535**，全球 **213,638**；海卫一团队 **7,153**，海卫二团队 **290**。这些数值尚不是已认证的全库唯一观测数。

累计参考值保留在统计表中：`raw_team_entries` / `satellite_entries`；当前柱状图使用 `selected_team_entries` / `selected_entries`。不要混用。

## 图件含义

- 柱状图：蓝柱为团队、灰柱为全球（包含团队）。
- 地图：全球已定位地面台站分布；红点为中国台站、蓝点为其他地区台站。中国台站不等于团队。
- 地图的 China 占比以已定位地面条目为分母；空间观测和未定位记录不画在地图上。

正式地图采用确认的 A 版：大幅世界地图、中国局部放大图、简短系统编号，以及与柱状图统一的标题、图例和来源字体。旧图与候选仅存于本地忽略缓存，不纳入本次提交范围。

## 重新生成

在此目录运行（Windows 已有 Python 环境，无新增安装）：

```powershell
C:\Software\Code\Python\python.exe scripts/rebuild_all.py
```

脚本先重建统计、生成图件，再执行验证并更新报告。代码不依赖启动目录。

外部原始星表默认位于 `C:\Users\Y\Documents\study_ancoj\data\imcce`；更换位置时设置 `IMCCE_RAW_DIR`。本项目不删除或修改该目录。

只重新绘制柱状图：`python scripts/plot_imcce_number.py`。

统计定义与未解决问题见 [口径说明](reports/DATA_LINEAGE_REPORT.md)。

当前依赖版本列于 requirements.txt；已有依赖可直接运行，迁移环境时安装这些依赖并设置外部原始星表路径。

本地提交范围、验证结果与手动推送步骤见 [推送交接](reports/推送交接.md)。
