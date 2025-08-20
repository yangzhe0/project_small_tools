import matplotlib.pyplot as plt
import numpy as np

# A组数据 (N, S, U)
A_N = [[1847, 1852], [1856, 1856], [1863, 1863], [1866, 1868], [1873, 1877], [1883, 1889], [1892, 1923], [1928, 1928], [1939, 1942], [1949, 2021]]
A_S = [[1874, 2023]]
A_U = [[1787, 1832], [1837, 1837], [1847, 1892], [1894, 1927], [1947, 2020]]
A_J = [[1906, 1907], [1914, 1914], [1951, 1952], [1967, 1969], [1973, 1973], [1975, 1976], [1980, 1981], [1986, 2022]]

# B组数据 (N, S, U)
B_N = [[1996, 2009], [2010, 2019]]
B_S = [[1987, 1988], [2003, 2014]]
B_U = [[1990], [1998, 2007], [2008, 2014]]
B_J = [[2016, 2018]]

# 新增函数：将年份段转换为不连续的x和y坐标
def get_disconnected_plot_data(date_ranges, y_position):
    x_coords = []
    y_coords = []
    for i, item in enumerate(date_ranges):
        # 处理单个年份的情况
        if len(item) == 1:
            start = end = item[0]  # 单个年份表示一个点
        else:
            start, end = item  # 否则就是一个区间
        
        if i > 0:  # 如果不是第一个段落
            # 在每个时间段之间插入一个None，创建断点
            x_coords.append(None)
            y_coords.append(None)
        
        # 添加开始和结束日期
        x_coords.append(start)
        y_coords.append(y_position)
        x_coords.append(end)
        y_coords.append(y_position)
    
    return x_coords, y_coords

# 创建一个包含四个子图的图形，并设置其大小
fig, ax = plt.subplots(4, 1, figsize=(10, 8))

# 定义y轴上两条线的位置
y_total_time = 0.4
y_our_work = 0.6

# --- 绘制木星（Jupiter）的子图 (ax[0]) ---
x_A_J, y_A_J = get_disconnected_plot_data(A_J, y_total_time)
x_B_J, y_B_J = get_disconnected_plot_data(B_J, y_our_work)
ax[0].plot(x_A_J, y_A_J, color='lightgray', lw=10)
ax[0].plot(x_B_J, y_B_J, color='blue', lw=10)
ax[0].set_title('Jupiter (J6 - J13)')
ax[0].set_yticks([y_total_time, y_our_work])
ax[0].set_yticklabels(['Total Time', 'QIAO'])
ax[0].set_ylim(0, 1)

# --- 绘制土星（Saturn）的子图 (ax[1]) ---
x_A_S, y_A_S = get_disconnected_plot_data(A_S, y_total_time)
x_B_S, y_B_S = get_disconnected_plot_data(B_S, y_our_work)
ax[1].plot(x_A_S, y_A_S, color='lightgray', lw=10)
ax[1].plot(x_B_S, y_B_S, color='blue', lw=10)
ax[1].set_title('Saturn (S1-S8, S9)')
ax[1].set_yticks([y_total_time, y_our_work])
ax[1].set_yticklabels(['Total Time', 'QIAO'])
ax[1].set_ylim(0, 1)

# --- 绘制天王星（Uranus）的子图 (ax[2]) ---
x_A_U, y_A_U = get_disconnected_plot_data(A_U, y_total_time)
x_B_U, y_B_U = get_disconnected_plot_data(B_U, y_our_work)
ax[2].plot(x_A_U, y_A_U, color='lightgray', lw=10)
ax[2].plot(x_B_U, y_B_U, color='blue', lw=10)
ax[2].set_title('Uranus (U1-U5)')
ax[2].set_yticks([y_total_time, y_our_work])
ax[2].set_yticklabels(['Total Time', 'QIAO'])
ax[2].set_ylim(0, 1)

# --- 绘制海王星（Neptune）的子图 (ax[3]) ---
x_A_N, y_A_N = get_disconnected_plot_data(A_N, y_total_time)
x_B_N, y_B_N = get_disconnected_plot_data(B_N, y_our_work)
ax[3].plot(x_A_N, y_A_N, color='lightgray', lw=10)
ax[3].plot(x_B_N, y_B_N, color='blue', lw=10)
ax[3].set_title('Neptune (N1, N2)')
ax[3].set_yticks([y_total_time, y_our_work])
ax[3].set_yticklabels(['Other', 'QIAO'])
ax[3].set_ylim(0, 1)

# 对所有子图进行格式化
for i in range(4):
    ax[i].tick_params(axis='x', rotation=0)
    ax[i].grid(True, linestyle='--', alpha=0.6)

# 添加全局标题
fig.suptitle('QIAO Observational vs Total Observational', fontsize=16)

# 调整子图布局，确保标题和标签不重叠
plt.tight_layout(rect=[0, 0, 1, 0.96])

# 保存图形为高分辨率的PNG文件
plt.savefig('time.png', dpi=300)

# 显示图形
plt.show()
