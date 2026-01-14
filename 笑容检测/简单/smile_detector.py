import cv2
import numpy as np

class SmileDetector:
    def __init__(self):
        """初始化微笑检测器"""
        # 加载人脸检测器（Haar Cascade）
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # 加载微笑检测器（Haar Cascade）
        try:
            # 尝试加载 OpenCV 自带的微笑检测器
            smile_cascade_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
            self.smile_cascade = cv2.CascadeClassifier(smile_cascade_path)
            if self.smile_cascade.empty():
                # 如果没有，使用另一个路径或者创建简单的检测逻辑
                self.use_landmark_method = True
            else:
                self.use_landmark_method = False
        except:
            self.use_landmark_method = True
        
        # 如果使用地标方法，我们将基于嘴部区域的特征
        if self.use_landmark_method:
            print("使用基于几何特征的笑容检测方法")
    
    def detect_faces(self, gray):
        """检测人脸"""
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def detect_smile_haar(self, gray, face_roi):
        """使用 Haar Cascade 检测微笑"""
        if self.smile_cascade.empty():
            return False
        
        # 在面部下半部分检测微笑（嘴部区域）
        x, y, w, h = face_roi
        roi_gray = gray[y + h//2:y + h, x:x + w]
        
        if roi_gray.size == 0:
            return False
        
        smiles = self.smile_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.7,
            minNeighbors=20,
            minSize=(20, 20)
        )
        return len(smiles) > 0
    
    def detect_smile_geometric(self, gray, face_roi):
        """基于几何特征检测微笑（嘴部区域的对比度）"""
        x, y, w, h = face_roi
        
        # 提取嘴部区域（面部下半部分）
        mouth_roi = gray[y + int(h*0.5):y + int(h*0.85), x:x + w]
        
        if mouth_roi.size == 0:
            return False
        
        # 使用边缘检测和轮廓分析
        # 微笑时，嘴角向上，嘴部区域会有特定的边缘模式
        edges = cv2.Canny(mouth_roi, 30, 100)
        
        # 计算边缘密度（微笑时嘴角边缘更明显）
        edge_density = np.sum(edges > 0) / mouth_roi.size
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            # 找到最大的轮廓（可能是嘴部）
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 计算轮廓的凸包
            hull = cv2.convexHull(largest_contour)
            
            # 简单的微笑判断：轮廓宽度较大且有一定高度
            x_coords = hull[:, 0, 0]
            y_coords = hull[:, 0, 1]
            
            if len(x_coords) > 0 and len(y_coords) > 0:
                width = np.max(x_coords) - np.min(x_coords)
                height = np.max(y_coords) - np.min(y_coords)
                
                # 微笑特征：嘴部较宽，宽度/高度比大于某个阈值
                aspect_ratio = width / (height + 1e-5)
                
                # 结合多个特征
                is_smiling = (
                    edge_density > 0.15 and  # 边缘密度阈值
                    aspect_ratio > 1.5 and  # 宽高比
                    width > mouth_roi.shape[1] * 0.3  # 最小宽度
                )
                return is_smiling
        
        return False
    
    def detect_smile(self, gray, face_roi):
        """检测微笑"""
        if self.use_landmark_method:
            return self.detect_smile_geometric(gray, face_roi)
        else:
            return self.detect_smile_haar(gray, face_roi)
    
    def draw_info(self, frame, faces, smile_status):
        """在画面上绘制信息"""
        h, w = frame.shape[:2]
        
        # 绘制状态栏背景
        cv2.rectangle(frame, (0, 0), (w, 80), (0, 0, 0), -1)
        
        # 绘制状态文字
        if smile_status:
            status_text = "😊 你在笑！好开心！"
            color = (0, 255, 0)  # 绿色
            bg_color = (0, 200, 0)
        else:
            status_text = "😐 没有检测到笑容，笑一个吧！"
            color = (100, 100, 255)  # 红色
            bg_color = (0, 0, 200)
        
        # 绘制状态指示圆
        cv2.circle(frame, (30, 40), 15, bg_color, -1)
        cv2.circle(frame, (30, 40), 15, color, 3)
        
        # 绘制文字
        cv2.putText(
            frame, status_text,
            (60, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2,
            cv2.LINE_AA
        )
        
        # 绘制人脸和微笑区域
        for (x, y, w, h) in faces:
            # 人脸框
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
            
            # 嘴部区域
            mouth_y = y + int(h * 0.65)
            mouth_h = int(h * 0.2)
            if smile_status:
                cv2.rectangle(
                    frame,
                    (x, mouth_y),
                    (x+w, mouth_y+mouth_h),
                    (0, 255, 0),
                    2
                )
            else:
                cv2.rectangle(
                    frame,
                    (x, mouth_y),
                    (x+w, mouth_y+mouth_h),
                    (0, 0, 255),
                    2
                )
    
    def run(self):
        """运行摄像头检测"""
        print("🎥 启动摄像头...")
        print("📸 按 'q' 键退出")
        print("=" * 50)
        
        # 打开摄像头
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ 错误：无法打开摄像头")
            print("请检查：")
            print("  1. 摄像头是否已连接")
            print("  2. 其他程序是否在使用摄像头")
            return
        
        # 设置摄像头参数
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        smile_count = 0
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ 无法读取摄像头画面")
                    break
                
                # 水平翻转（镜像效果）
                frame = cv2.flip(frame, 1)
                
                # 转为灰度图
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 检测人脸
                faces = self.detect_faces(gray)
                
                # 检测微笑
                smiling = False
                if len(faces) > 0:
                    # 检测第一个（最大的）人脸
                    main_face = faces[0]
                    smiling = self.detect_smile(gray, main_face)
                    
                    if smiling:
                        smile_count += 1
                    frame_count += 1
                
                # 绘制信息
                self.draw_info(frame, faces, smiling)
                
                # 显示微笑统计（右上角）
                if frame_count > 0:
                    smile_ratio = (smile_count / frame_count) * 100
                    stats_text = f"笑容率: {smile_ratio:.1f}%"
                    cv2.putText(
                        frame, stats_text,
                        (frame.shape[1] - 200, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )
                
                # 显示画面
                cv2.imshow('😊 笑容检测器 - 按 q 退出', frame)
                
                # 按 'q' 退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\n⏹️  用户中断")
        finally:
            # 清理资源
            cap.release()
            cv2.destroyAllWindows()
            print("✅ 摄像头已关闭")


def main():
    print("=" * 50)
    print("😊 笑容检测器启动")
    print("=" * 50)
    
    detector = SmileDetector()
    detector.run()
    
    print("\n👋 再见！")


if __name__ == "__main__":
    main()

