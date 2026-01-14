@ -0,0 +1,198 @@
import tkinter as tk
from datetime import datetime
import math

class AnalogClock:
    def __init__(self, root):
        self.root = root
        self.root.title("精美时钟")
        self.root.geometry("600x700")
        self.root.configure(bg='#1a1a2e')
        
        # 时钟参数
        self.canvas_size = 500
        self.center_x = 300
        self.center_y = 350
        self.radius = 220
        
        # 创建画布
        self.canvas = tk.Canvas(
            root, 
            width=600, 
            height=700, 
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # 数字显示区域
        self.digital_label = tk.Label(
            root,
            font=('Arial', 24, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e',
            pady=20
        )
        self.digital_label.pack()
        
        # 日期显示
        self.date_label = tk.Label(
            root,
            font=('Arial', 14),
            fg='#6c757d',
            bg='#1a1a2e'
        )
        self.date_label.pack()
        
        # 绘制静态元素
        self.draw_static_elements()
        
        # 开始更新
        self.update_clock()
    
    def draw_static_elements(self):
        """绘制时钟的静态元素：表盘、刻度、数字"""
        # 外圈装饰圆环
        self.canvas.create_oval(
            self.center_x - self.radius - 10,
            self.center_y - self.radius - 10,
            self.center_x + self.radius + 10,
            self.center_y + self.radius + 10,
            outline='#16213e',
            width=20
        )
        
        # 主表盘
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline='#0f3460',
            width=4,
            fill='#16213e'
        )
        
        # 绘制小时刻度（12个，较长）
        for i in range(12):
            angle = math.radians(i * 30 - 90)  # -90度让12点在顶部
            # 刻度外点
            x1 = self.center_x + (self.radius - 30) * math.cos(angle)
            y1 = self.center_y + (self.radius - 30) * math.sin(angle)
            # 刻度内点
            x2 = self.center_x + (self.radius - 15) * math.cos(angle)
            y2 = self.center_y + (self.radius - 15) * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, fill='#00ff88', width=3)
            
            # 小时数字
            hour_num = 12 if i == 0 else i
            num_x = self.center_x + (self.radius - 50) * math.cos(angle)
            num_y = self.center_y + (self.radius - 50) * math.sin(angle)
            self.canvas.create_text(
                num_x, num_y,
                text=str(hour_num),
                font=('Arial', 18, 'bold'),
                fill='#00ff88'
            )
        
        # 绘制分钟刻度（60个，较短）
        for i in range(60):
            if i % 5 != 0:  # 跳过小时刻度位置
                angle = math.radians(i * 6 - 90)
                x1 = self.center_x + (self.radius - 25) * math.cos(angle)
                y1 = self.center_y + (self.radius - 25) * math.sin(angle)
                x2 = self.center_x + (self.radius - 15) * math.cos(angle)
                y2 = self.center_y + (self.radius - 15) * math.sin(angle)
                self.canvas.create_line(x1, y1, x2, y2, fill='#0f3460', width=1)
        
        # 中心点装饰
        self.canvas.create_oval(
            self.center_x - 8,
            self.center_y - 8,
            self.center_x + 8,
            self.center_y + 8,
            fill='#00ff88',
            outline='#0f3460',
            width=2
        )
    
    def update_clock(self):
        """更新时钟显示"""
        now = datetime.now()
        
        # 清除动态元素（指针）
        self.canvas.delete("hand")
        
        # 计算角度（-90度让12点在上方）
        second_angle = math.radians(now.second * 6 - 90)
        minute_angle = math.radians(now.minute * 6 + now.second * 0.1 - 90)
        hour_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)
        
        # 绘制秒针（细长，红色）
        second_length = self.radius - 40
        second_x = self.center_x + second_length * math.cos(second_angle)
        second_y = self.center_y + second_length * math.sin(second_angle)
        self.canvas.create_line(
            self.center_x, self.center_y,
            second_x, second_y,
            fill='#ff0066',
            width=2,
            tags="hand"
        )
        
        # 绘制分针（中等，蓝色）
        minute_length = self.radius - 60
        minute_x = self.center_x + minute_length * math.cos(minute_angle)
        minute_y = self.center_y + minute_length * math.sin(minute_angle)
        self.canvas.create_line(
            self.center_x, self.center_y,
            minute_x, minute_y,
            fill='#00a8ff',
            width=4,
            tags="hand"
        )
        
        # 绘制时针（短粗，绿色）
        hour_length = self.radius - 100
        hour_x = self.center_x + hour_length * math.cos(hour_angle)
        hour_y = self.center_y + hour_length * math.sin(hour_angle)
        self.canvas.create_line(
            self.center_x, self.center_y,
            hour_x, hour_y,
            fill='#00ff88',
            width=6,
            tags="hand"
        )
        
        # 更新数字时间
        time_str = now.strftime("%H:%M:%S")
        self.digital_label.config(text=time_str)
        
        # 更新日期
        date_str = now.strftime("%Y年%m月%d日  %A")
        # 转换为中文星期
        weekdays = {
            'Monday': '星期一',
            'Tuesday': '星期二',
            'Wednesday': '星期三',
            'Thursday': '星期四',
            'Friday': '星期五',
            'Saturday': '星期六',
            'Sunday': '星期日'
        }
        date_str = date_str.replace(now.strftime("%A"), weekdays.get(now.strftime("%A"), now.strftime("%A")))
        self.date_label.config(text=date_str)
        
        # 100毫秒后再次更新
        self.root.after(100, self.update_clock)


def main():
    root = tk.Tk()
    clock = AnalogClock(root)
    root.mainloop()


if __name__ == "__main__":
    main()
