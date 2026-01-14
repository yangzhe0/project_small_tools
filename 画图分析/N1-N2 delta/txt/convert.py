import os
import chardet
import csv
import re
from tqdm import tqdm

def b_convert_csv(folder_path, csv_path):
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)

    def detect_encoding(file_path):
        with open(file_path, 'rb') as file:
            return chardet.detect(file.read())['encoding']

    def detect_delimiter(file_content):
        patterns = {',': re.compile(r'[^,]+'), '\t': re.compile(r'[^\t]+'), ' ': re.compile(r'[^\s]+')}
        max_match_count = 0
        detected_delimiter = None
        for delimiter, pattern in patterns.items():
            matches = len(pattern.findall(file_content))
            if matches > max_match_count:
                max_match_count = matches
                detected_delimiter = delimiter
        return detected_delimiter

    failed_files = []

    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    for filename in tqdm(txt_files, desc='处理TXT文件'):
        file_path = os.path.join(folder_path, filename)
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
            file_content = file.read()
            delimiter = detect_delimiter(file_content)
            if delimiter is None:
                failed_files.append(filename)
                continue
            lines = file_content.split('\n')
            csv_lines = []
            for line in lines:
                if line.strip():
                    if delimiter == '\t':
                        fields = line.split('\t')
                    elif delimiter == ' ':
                        fields = line.split()
                    else:
                        fields = line.split(',')
                    fields_with_brackets = [f"[{field}]" for field in fields]
                    csv_lines.append(fields_with_brackets)
        csv_filename = filename.replace('.txt', '.csv')
        csv_file_path = os.path.join(csv_path, csv_filename)
        try:
            with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                headers = [f"C{i+1}" for i in range(len(csv_lines[0]))]
                csv_writer.writerow(headers)
                for row in csv_lines:
                    csv_writer.writerow(row)
        except Exception as e:
            failed_files.append(filename)
            print(f"写入{filename}失败: {e}")

    if failed_files:
        print("转换失败的文件:", failed_files)
    else:
        print("所有文件转换成功。")


if __name__ == "__main__":
    b_convert_csv("N1-N2 delta\\txt", "N1-N2 delta\\csv")