# plots/drawing.py
# ------------------------------------------------------------
# 绘图模块
#
# 功能：
# 1. 电场云图绘制
# 2. 反射/透射系数柱状图绘制
#
# 采用 Matplotlib，方便与 Streamlit 集成。
# ------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt


def plot_field_contour(X, Z, field, title="Electric Field Contour", cmap="RdBu_r"):
    """
    绘制二维电场云图

    参数：
    - X, Z : 网格坐标
    - field: 电场值
    - title: 图标题
    - cmap : 颜色映射
    """
    fig, ax = plt.subplots(figsize=(10.5, 5.2))

    cf = ax.contourf(X, Z, field, levels=70, cmap=cmap)
    ax.axhline(0, color="k", linestyle="--", linewidth=1.2, label="z = 0 interface")

    ax.set_xlabel("x (m)")
    ax.set_ylabel("z (m)")
    ax.set_title(title)
    ax.legend(loc="upper right")

    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("Electric Field (a.u.)")

    plt.tight_layout()
    return fig


def plot_rt_bar(r, t, pol="TE"):
    """
    绘制反射/透射系数柱状图

    为了教学展示，显示：
    - |r|
    - |t|
    """
    mag_r = np.abs(r)
    mag_t = np.abs(t)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))

    labels = ["|r|", "|t|"]
    values = [mag_r, mag_t]
    colors = ["#ff6b6b", "#4dabf7"]

    bars = ax.bar(labels, values, color=colors, width=0.55)

    ax.set_ylim(0, max(1.2, max(values) * 1.25))
    ax.set_ylabel("Magnitude")
    ax.set_title(f"{pol} Wave Reflection/Transmission Coefficients")
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    # 数值标注
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.03,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=11,
        )

    plt.tight_layout()
    return fig