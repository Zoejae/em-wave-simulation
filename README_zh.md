# 电磁波反射透射仿真平台

本项目是一个面向《电磁场与电磁波》课程教学的开源仿真平台，使用 Python + Streamlit + Numpy + Matplotlib 实现电磁波在单界面和多层介质中的反射、透射与空间电场分布可视化。

---

## 一、项目功能

### 1. 交互式教学功能
- 支持 **TE/TM** 偏振切换
- 支持 **0.1 ~ 20 GHz** 频率调节
- 支持 **0° ~ 89°** 入射角调节
- 支持介质选择：空气、玻璃、水、半导体、铜、铝、自定义介质
- 支持 **多层介质模式**
- 实时刷新反射、透射系数与电场云图

### 2. 物理仿真功能
- 严格采用 **菲涅尔方程**
- 使用 **复介电常数** 描述有耗介质
- 使用 **复折射率** 与 **复数斯涅尔定律**
- 金属采用高电导率模型，体现 **趋肤效应**
- 多层介质采用 **输入阻抗回溯法**

---

## 二、项目结构

```bash
emwave-simulator/
├─ app.py
├─ requirements.txt
├─ config/
│  ├─ __init__.py
│  └─ materials.py
├─ physics/
│  ├─ __init__.py
│  ├─ constants.py
│  ├─ fresnel.py
│  ├─ multilayer.py
│  └─ wavefield.py
├─ plots/
│  ├─ __init__.py
│  └─ drawing.py
├─ assets/
├─ README_zh.md
├─ README_en.md
├─ .gitignore
└─ LICENSE