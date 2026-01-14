import matplotlib.pyplot as plt
import numpy as np

# 更新的数据
categories_full = ['J6-J13','S1-S8', 'S9', 'U1-5', 'N1', 'N2']
qiao_data_full = [639,3261, 1288, 14636, 7116, 402]  # QIAO数据
total_data_full = [26147,127065, 8152, 45683, 17223, 3252]  # 总数据
qiao_percentages_full = [2,3, 16, 32, 41, 12]  # QIAO占比百分比

# 设置柱状图
x_full = np.arange(len(categories_full))  # X轴的类别位置
width_full = 0.35  # 柱状图的宽度

# 创建图表并使用普通纵轴
fig_full_linear, ax_full_linear = plt.subplots(figsize=(10, 6))

# 绘制QIAO数据和总数据的柱状图
rects1_full_linear = ax_full_linear.bar(x_full - width_full/2, qiao_data_full, width_full, label='QIAO Data', color='blue')
rects2_full_linear = ax_full_linear.bar(x_full + width_full/2, total_data_full, width_full, label='Total Data', color='lightgray')

# 添加比例标签和数量标签
for rect, qiao_percent, qiao_val, total_val in zip(rects1_full_linear, qiao_percentages_full, qiao_data_full, total_data_full):
    height = rect.get_height()
    ax_full_linear.annotate(f'{qiao_val}\n({qiao_percent}%)',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 文字稍微往上移动一点
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10)

# 设置图表标题和标签
ax_full_linear.set_xlabel('Plant Categories')
ax_full_linear.set_ylabel('Data Count')
ax_full_linear.set_title('QIAO Observational vs Total Observational', fontsize=16)
ax_full_linear.set_xticks(x_full)
ax_full_linear.set_xticklabels(categories_full)
ax_full_linear.legend()

# 显示图表
plt.tight_layout()
plt.savefig('number.png', dpi=300)
