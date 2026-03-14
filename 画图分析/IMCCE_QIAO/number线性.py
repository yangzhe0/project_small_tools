import matplotlib.pyplot as plt
import numpy as np

# 更新的数据
categories_full = ['J6-J13','S1-S8', 'S9', 'U1-5', 'N1', 'N2']
qiao_data_full = [639,3261, 1288, 14636, 7116, 402]  # QIAO数据
total_data_full = [22662,120949, 9188, 56580, 20656, 3252]  # 总数据
qiao_percentages_full = [round(q / t * 100) for q, t in zip(qiao_data_full, total_data_full)]  # 实时计算QIAO占比百分比

# 设置柱状图
x_full = np.arange(len(categories_full))  # X轴的类别位置
width_full = 0.35  # 柱状图的宽度

# 创建图表并使用普通纵轴
fig_full_linear, ax_full_linear = plt.subplots(figsize=(10, 6))

# 绘制QIAO数据和总数据的柱状图
rects2_full_linear = ax_full_linear.bar(x_full + width_full/2, total_data_full, width_full, label='Total Data', color='lightgray', alpha=0.55, zorder=2)
rects1_full_linear = ax_full_linear.bar(x_full - width_full/2, qiao_data_full, width_full, label='QIAO Data', color='blue', zorder=3)

# 添加比例标签和数量标签
for rect, qiao_percent, qiao_val, total_val in zip(rects1_full_linear, qiao_percentages_full, qiao_data_full, total_data_full):
    height = rect.get_height()
    ax_full_linear.annotate(f'{qiao_val}\n({qiao_percent}%)',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 文字稍微往上移动一点
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10)

for rect, total_val in zip(rects2_full_linear, total_data_full):
    height = rect.get_height()
    ax_full_linear.annotate(f'{total_val}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10, color='#444444')

# 设置图表标题和标签
ax_full_linear.set_xlabel('Plant Categories')
ax_full_linear.set_ylabel('Data Count')
ax_full_linear.set_title('QIAO Observational vs Total Observational', fontsize=16)
ax_full_linear.set_xticks(x_full)
ax_full_linear.set_xticklabels(categories_full)
ax_full_linear.legend()
ax_full_linear.grid(True, which="both", axis="y", linestyle="--", alpha=0.35, zorder=0)

# 显示图表
plt.tight_layout()
plt.savefig('number线性.png', dpi=300)
