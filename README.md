# EM-Wave-Simulation 电磁波菲涅尔仿真平台
基于Python+Streamlit实现介质分界面电磁波反射、折射仿真，面向电磁场课程教学演示。

## ✨ 功能特点
1. 支持TE/TM两种偏振模式，自定义入射角度、工作频率
2. 内置空气、玻璃、铜、铝等常用材料库，可自定义介电常数、电导率
3. 实时计算菲涅尔系数，绘制反射率/透射率变化曲线、空间电场云图
4. 拓展多层介质膜仿真模块，模拟薄膜干涉

## 🚀 本地部署运行
```bash
# 1.创建虚拟环境
python -m venv venv
# 2.激活环境
.\venv\Scripts\activate
# 3.安装依赖
pip install -r requirements.txt
# 4.启动网页程序
streamlit run app.py
