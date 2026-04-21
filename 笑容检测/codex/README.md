# 笑容识别小程序

这是一个本地网页版笑容识别小程序，打开后会调用摄像头，实时识别人脸关键点，并根据表情系数输出笑容分数。

## 功能

- 实时摄像头预览
- 笑容分数与状态提示
- 左右嘴角、张嘴程度的简易可视化
- 关键点轮廓描绘
- 本地 PowerShell 静态服务脚本

## 启动方式

1. 打开 PowerShell，进入目录：

   ```powershell
   cd C:\Users\Y\Downloads\smile-detector-mini
   ```

2. 启动本地服务：

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\start-server.ps1
   ```

3. 在浏览器中打开：

   `http://localhost:8080`

## 使用说明

- 点击“开启识别”
- 浏览器弹出权限时允许摄像头访问
- 对着镜头自然微笑，观察分数和状态变化
- 如果你想看到与自拍一致的方向，可以保持镜像开启

## 注意

- 首次运行需要联网加载 MediaPipe 官方模型和前端运行库
- 摄像头通常只能在 `localhost` 或 `https` 环境下使用，所以不要直接双击 HTML 文件打开
- 建议使用较新的 Chrome 或 Edge 浏览器
