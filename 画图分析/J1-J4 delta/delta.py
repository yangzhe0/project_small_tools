import os
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm

# ===================== 自定义配置 =====================
INPUT_FOLDER = "J1-J4 delta/csv"         # 输入 CSV 文件所在目录
OUTPUT_FOLDER = "J1-J4 delta/delta"      # 输出文件保存目录
FILE_NAMES = ['J1', 'J2','J3','J4']                 # 文件名数组（可根据实际情况添加更多文件）
# =====================================================

# 如果输出目录不存在，则创建
Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

def process_and_save(df1, df2, output_file):
    """
    处理两个 DataFrame（df1 与 df2），合并后计算残差，并将结果保存到 CSV 文件。
    同时返回一个包含处理信息的报告字典。
    """
    # 将所有数据转换为字符串，然后对每一列调用 str.strip 去除左右方括号
    df1 = df1.astype(str).apply(lambda col: col.str.strip('[]'))
    df2 = df2.astype(str).apply(lambda col: col.str.strip('[]'))
    
    # 重新命名列
    df1.columns = ['Year', 'M', 'D', 'H', 'Min', 'S', 'Alpha', 'Delta']
    df2.columns = ['Year', 'M', 'D', 'H', 'Min', 'S', 'Alpha', 'Delta']
    
    # 定义生成时间戳字符串的函数
    def create_time(row):
        try:
            year = int(row['Year'])
            month = int(row['M'])
            day = int(row['D'])
            hour = int(row['H'])
            minute = int(row['Min'])
            second = int(float(row['S']))
            return f"{year}-{month}-{day} {hour}:{minute}:{second}"
        except Exception:
            return None
    
    # 转换为 datetime 对象，添加新列 'Time'
    for df in [df1, df2]:
        df['Time'] = pd.to_datetime(df.apply(create_time, axis=1), errors='coerce')
    
    # 仅保留需要的列
    df1 = df1[['Time', 'Alpha', 'Delta']]
    df2 = df2[['Time', 'Alpha', 'Delta']]
    
    # 内连接合并数据（基于 Time 列）
    merged = pd.merge(df1, df2, on='Time', how='inner', suffixes=('_1', '_2'))
    
    # 计算残差
    def calculate_residuals(row):
        try:
            ra_diff = (float(row['Alpha_2']) - float(row['Alpha_1'])) * 15 * 3600
            ra_diff *= np.cos(np.radians(float(row['Delta_1'])))
            dec_diff = (float(row['Delta_2']) - float(row['Delta_1'])) * 3600
            return pd.Series([ra_diff, dec_diff])
        except Exception:
            return pd.Series([np.nan, np.nan])
    
    merged[['RA_Residual', 'Dec_Residual']] = merged.apply(calculate_residuals, axis=1)
    merged = merged.dropna(subset=['RA_Residual', 'Dec_Residual']).sort_values('Time')
    
    # 写入 CSV 文件（覆盖写入）
    merged.to_csv(output_file, index=False)
    
    # 返回处理报告信息
    report = {
        "input_rows_df1": len(df1),
        "input_rows_df2": len(df2),
        "merged_rows": len(merged),
        "output_file": output_file
    }
    return report

# 用于保存各个文件的处理报告
report_list = []

# 遍历所有文件，并使用 tqdm 显示进度条
for variable in tqdm(FILE_NAMES, desc="Processing files", unit="file"):
    input_file1 = Path(INPUT_FOLDER) / f"1-{variable}.csv"
    input_file2 = Path(INPUT_FOLDER) / f"2-{variable}.csv"
    output_file = Path(OUTPUT_FOLDER) / f"delta_{variable}.csv"
    
    # 读取整个 CSV 文件
    df1 = pd.read_csv(input_file1, header=0)
    df2 = pd.read_csv(input_file2, header=0)
    
    # 处理并保存结果，同时获取报告信息
    report = process_and_save(df1, df2, output_file)
    report["file"] = variable
    report_list.append(report)

# 打印处理报告
print("\n处理报告:")
for report in report_list:
    print(f"文件: {report['file']}")
    print(f"  合并后的行数: {report['merged_rows']}")
    
print(f"总共处理文件数量: {len(report_list)}")
