import pandas as pd
import matplotlib.pyplot as plt
from bisect import bisect_left

file_path = 'IAU_number.csv'
data = pd.read_csv(file_path)

# 数据预处理
planets_of_interest = ['Jupiter', 'Saturn', 'Uranus', 'Neptune']
filtered_data = data[data['Satellite'].isin(planets_of_interest)]

# 按年统计卫星数量
annual_counts = filtered_data.groupby(['Year discovered', 'Satellite']).size().unstack(fill_value=0)

# 自定义刻度设置
custom_ticks = [1610, 1660, 1710, 1760, 1810, 1860, 1910, 1960, 1970, 
               1980, 1990, 2000, 2010, 2014, 2018, 2022, 2023]

# 创建完整时间索引（保留原始数据+自定义刻度）
full_years = sorted(list(set(annual_counts.index.tolist() + custom_ticks)))
full_index = pd.Index(full_years, name='Year discovered')

# 重新索引并计算累计值
complete_data = annual_counts.reindex(full_index).fillna(0)
cumulative_counts = complete_data.cumsum()

# 可视化设置
plt.figure(figsize=(10, 7))
colors = {'Jupiter': '#1f77b4', 'Saturn': '#ff7f0e', 
          'Uranus': '#2ca02c', 'Neptune': '#d62728'}

# 创建等间距坐标映射
def get_tick_positions(years, custom_ticks):
    return [bisect_left(custom_ticks, year) for year in years]

# 生成可视化数据
x_values = get_tick_positions(cumulative_counts.index, custom_ticks)

# 绘制曲线
for planet in cumulative_counts.columns:
    plt.plot(x_values, cumulative_counts[planet], 
             color=colors[planet], linewidth=2.5, label=planet)
    
    # 添加最终数值标注
    last_value = cumulative_counts[planet].iloc[-1]
    plt.text(x_values[-1], last_value, f'{int(last_value)}',
             color=colors[planet], fontsize=14, ha='center', va='bottom')

# 坐标轴设置
plt.xticks(ticks=range(len(custom_ticks)), 
           labels=custom_ticks)
plt.yticks(range(0, 160, 20))
plt.xlim(-0.5, len(custom_ticks)-0.5)

# 样式优化
plt.title('Number of Moons in the Solar System', fontsize=16, pad=20)
plt.xlabel('Year', fontsize=12, labelpad=10)
plt.ylabel('Number', fontsize=12, labelpad=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title="Planets", frameon=True, shadow=True)
# 保存图表到文件
output_file = 'Number of Moons in the Solar System.png'
plt.tight_layout()
plt.savefig(output_file, dpi=300)