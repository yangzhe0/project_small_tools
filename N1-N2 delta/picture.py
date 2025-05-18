import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# =============== 自定义配置 ===============
# 包含 CSV 文件的文件夹路径
DELTA_FOLDER = 'N1-N2 delta/delta'
# 保存合并后图像的文件路径
OUTPUT_IMAGE = 'N1-N2 delta/Differences in the N1-N2.png'
# 图像整体宽度和每个子图的高度
FIGURE_WIDTH = 20
SUBPLOT_HEIGHT = 7
# 横坐标时间刻度间隔（此处设置为每10年）
DATE_TICK_FREQ = '10YE'
# 额外添加的横坐标刻度（例如：2043-01-01）
CUSTOM_XTICK_APPEND = '2049-01-01'
# 整体图标题
TITLE_MAIN = 'Differences in the N1-N2 between 1920 and 2049\n'
# =============== 结束自定义配置 ===============

def plot_combined_residuals():
    # 获取 DELTA_FOLDER 中的所有 CSV 文件
    files = [os.path.join(DELTA_FOLDER, f) for f in os.listdir(DELTA_FOLDER) if f.endswith('.csv')]
    
    # 根据文件数量创建子图，每个子图高度为 SUBPLOT_HEIGHT，总体图像尺寸调整为 (FIGURE_WIDTH, SUBPLOT_HEIGHT * 文件数)
    fig, axes = plt.subplots(nrows=len(files), ncols=1, figsize=(FIGURE_WIDTH, SUBPLOT_HEIGHT * len(files)))
    
    # 如果只有一个文件时，axes 转换为列表，保证后续统一遍历
    if len(files) == 1:
        axes = [axes]
    
    # 遍历每个文件及对应的子图
    for idx, (ax, file) in enumerate(zip(axes, files)):
        # 读取 CSV 文件
        df = pd.read_csv(file)
        # 去除重复记录（基于 Time、RA_Residual、Dec_Residual 三个字段）
        df = df.drop_duplicates(subset=['Time', 'RA_Residual', 'Dec_Residual'])
        # 将 Time 列转换为日期时间格式
        df['Time'] = pd.to_datetime(df['Time'])
        
        # 根据数据时间范围动态生成横坐标刻度列表，并添加自定义的额外刻度
        xticks = pd.date_range(start=df['Time'].min(), end=df['Time'].max(), freq=DATE_TICK_FREQ).tolist()
        xticks.append(pd.Timestamp(CUSTOM_XTICK_APPEND))
        
        # 绘制赤经残差和赤纬残差曲线
        ax.plot(df['Time'], df['RA_Residual'], 'r-', label='Δα cosδ', linewidth=1, alpha=0.6)
        ax.plot(df['Time'], df['Dec_Residual'], 'b-', label='Δδ', linewidth=1, alpha=0.6)
        ax.legend(loc='upper right', fontsize=22)
        
        # 设置子图标题（去除扩展名后的文件名），字体大小24
        title = os.path.splitext(os.path.basename(file))[0]
        ax.set_title(title, fontsize=24)
        
        # 设置横坐标格式为年份显示
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        # 根据数据时间范围设置横坐标范围
        ax.set_xlim(df['Time'].min(), df['Time'].max())
        # 手动设置横坐标刻度
        ax.set_xticks(xticks)
        
        # 设置横纵坐标标签及字体大小
        ax.set_xlabel('Year', fontsize=20)
        ax.set_ylabel('Δ (arcsec)', fontsize=20)
        
        # 设置坐标刻度文字大小，并加粗刻度文字
        ax.tick_params(axis='both', which='major', labelsize=16)
        for tick in ax.get_xticklabels():
            tick.set_fontweight('bold')
        for tick in ax.get_yticklabels():
            tick.set_fontweight('bold')
    
    # 设置整体图标题及字体大小
    fig.suptitle(TITLE_MAIN, fontsize=28)
    
    # 调整整体布局，避免标题与子图重叠，同时缩小子图之间的间距
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.subplots_adjust(hspace=0.25)
    
    # 保存图片（保存后不显示图像）
    plt.savefig(OUTPUT_IMAGE)

if __name__ == '__main__':
    plot_combined_residuals()
