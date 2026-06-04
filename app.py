# app.py
# ------------------------------------------------------------
# 电磁波反射透射仿真平台
# Streamlit 网页主入口
#
# 功能：
# 1. TE/TM 斜入射
# 2. 频率、入射角、介质参数交互修改
# 3. 单界面 Fresnel 反射/透射系数
# 4. 多层介质输入阻抗回溯法
# 5. 电场二维瞬时分布云图
# 6. 系数柱状图
#
# 教学目标：
# 将《电磁场与电磁波》课程中的平面波、菲涅尔方程、
# 复介电常数、波阻抗、斯涅尔定律等公式转化为可视化仿真。
# ------------------------------------------------------------

import numpy as np
import streamlit as st

from config.materials import MATERIALS
from physics.fresnel import fresnel_single_interface
from physics.multilayer import multilayer_total_reflection
from physics.wavefield import build_field_map_single_interface
from plots.drawing import plot_field_contour, plot_rt_bar


# =========================
# 页面基础设置
# =========================
st.set_page_config(
    page_title="EM Wave Simulator",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("电磁波反射透射虚拟仿真教学平台")
st.markdown(
    """
本平台用于《电磁场与电磁波》课程教学，支持 **TE/TM 斜入射**、
**单界面反射透射**、**多层介质反射透射** 以及 **二维电场云图显示**。
"""
)

# =========================
# 侧边栏：参数设置
# =========================
with st.sidebar:
    st.header("仿真参数设置")

    # 偏振方式：TE / TM
    pol = st.selectbox("偏振方式", ["TE", "TM"], index=0)

    # 频率范围：0.1 ~ 20 GHz
    freq_ghz = st.slider("入射频率 (GHz)", 0.1, 20.0, 3.0, 0.1)
    freq = freq_ghz * 1e9  # 转换为 Hz

    # 入射角：0 ~ 89°
    theta_deg = st.slider("入射角 (deg)", 0.0, 89.0, 30.0, 1.0)
    theta_i = np.deg2rad(theta_deg)

    st.subheader("单界面介质选择")

    medium1_name = st.selectbox("上侧介质（介质1）", list(MATERIALS.keys()), index=0)
    medium2_name = st.selectbox("下侧介质（介质2）", list(MATERIALS.keys()), index=1)

    use_custom = st.checkbox("启用自定义介质参数", value=False)

    # 选择或自定义材料参数
    if use_custom:
        st.caption("可自定义 εr、μr、σ，用于教学演示任意介质。")
        eps1 = st.number_input(
            "介质1 相对介电常数 εr1",
            value=float(MATERIALS[medium1_name]["eps_r"]),
            min_value=0.1,
            step=0.1,
        )
        mu1 = st.number_input(
            "介质1 相对磁导率 μr1",
            value=float(MATERIALS[medium1_name]["mu_r"]),
            min_value=0.1,
            step=0.1,
        )
        sigma1 = st.number_input(
            "介质1 电导率 σ1 (S/m)",
            value=float(MATERIALS[medium1_name]["sigma"]),
            min_value=0.0,
            step=1e-4,
            format="%.6f",
        )

        eps2 = st.number_input(
            "介质2 相对介电常数 εr2",
            value=float(MATERIALS[medium2_name]["eps_r"]),
            min_value=0.1,
            step=0.1,
        )
        mu2 = st.number_input(
            "介质2 相对磁导率 μr2",
            value=float(MATERIALS[medium2_name]["mu_r"]),
            min_value=0.1,
            step=0.1,
        )
        sigma2 = st.number_input(
            "介质2 电导率 σ2 (S/m)",
            value=float(MATERIALS[medium2_name]["sigma"]),
            min_value=0.0,
            step=1e-4,
            format="%.6f",
        )
    else:
        eps1 = float(MATERIALS[medium1_name]["eps_r"])
        mu1 = float(MATERIALS[medium1_name]["mu_r"])
        sigma1 = float(MATERIALS[medium1_name]["sigma"])

        eps2 = float(MATERIALS[medium2_name]["eps_r"])
        mu2 = float(MATERIALS[medium2_name]["mu_r"])
        sigma2 = float(MATERIALS[medium2_name]["sigma"])

    st.subheader("多层介质模式")
    enable_multilayer = st.checkbox("一键开启多层介质模式（三层结构）", value=False)

    st.caption("说明：多层模式采用上层半无限介质 + 中间薄层 + 底层半无限基底。")


# =========================
# 物理计算：单界面 / 多层
# =========================
omega = 2.0 * np.pi * freq

if enable_multilayer:
    # 三层结构：上层半无限介质 + 中间薄层 + 底层半无限基底
    # 这里使用教学级结构，便于讲解多层介质中的输入阻抗回溯法
    thickness_cm = st.sidebar.number_input(
        "中间薄层厚度 (cm)", min_value=0.001, value=3.0, step=0.1
    )
    d = thickness_cm / 100.0  # 转换为 m

    # 默认中间层使用第二个介质，底层可指定为玻璃/半导体等
    substrate_name = st.sidebar.selectbox(
        "底层基底介质",
        list(MATERIALS.keys()),
        index=1,
    )
    mid_name = st.sidebar.selectbox(
        "中间薄层介质",
        list(MATERIALS.keys()),
        index=1,
    )

    # 中间层/基底参数
    mid = MATERIALS[mid_name]
    sub = MATERIALS[substrate_name]

    multilayer_layers = [
        {
            "name": medium1_name,
            "eps_r": eps1,
            "mu_r": mu1,
            "sigma": sigma1,
            "thickness": None,  # 半无限
        },
        {
            "name": mid_name,
            "eps_r": float(mid["eps_r"]),
            "mu_r": float(mid["mu_r"]),
            "sigma": float(mid["sigma"]),
            "thickness": d,
        },
        {
            "name": substrate_name,
            "eps_r": float(sub["eps_r"]),
            "mu_r": float(sub["mu_r"]),
            "sigma": float(sub["sigma"]),
            "thickness": None,  # 半无限
        },
    ]

    result = multilayer_total_reflection(
        layers=multilayer_layers,
        theta_i=theta_i,
        freq=freq,
        pol=pol,
    )

    r = result["r_total"]
    t = result["t_total"]
    theta_t = result["theta_t_01"]  # 第一界面的透射角（用于教学展示）
else:
    # 单界面 Fresnel 公式
    result = fresnel_single_interface(
        theta_i=theta_i,
        freq=freq,
        pol=pol,
        medium1={"eps_r": eps1, "mu_r": mu1, "sigma": sigma1},
        medium2={"eps_r": eps2, "mu_r": mu2, "sigma": sigma2},
    )
    r = result["r"]
    t = result["t"]
    theta_t = result["theta_t"]


# =========================
# 主内容布局
# =========================
col_left, col_right = st.columns([1.0, 1.05])

with col_left:
    st.subheader("计算结果")

    st.write(f"**偏振方式：** {pol}")
    st.write(f"**频率：** {freq_ghz:.2f} GHz")
    st.write(f"**入射角：** {theta_deg:.1f}°")

    st.markdown("### 复反射/透射系数")
    st.latex(r"r = " + f"{r.real:.4f} {'+' if r.imag >= 0 else '-'} {abs(r.imag):.4f}j")
    st.latex(r"t = " + f"{t.real:.4f} {'+' if t.imag >= 0 else '-'} {abs(t.imag):.4f}j")

    st.markdown("### 幅值结果")
    st.write(f"**|r| =** {np.abs(r):.6f}")
    st.write(f"**|t| =** {np.abs(t):.6f}")

    st.markdown("### 透射角")
    # 复角度下显示实部与虚部，教学上便于理解有耗介质中的波传播/衰减
    st.write(f"**θt =** {theta_t.real:.6f} rad")
    st.write(f"**θt（虚部）=** {theta_t.imag:.6f} rad")

    st.markdown("### 物理解释")
    st.info(
        "TE/TM 斜入射时，反射透射行为由菲涅尔方程决定；"
        "若介质有损耗，则折射率、波阻抗与透射角均为复数。"
    )

    fig_bar = plot_rt_bar(r=r, t=t, pol=pol)
    st.pyplot(fig_bar, clear_figure=True)

with col_right:
    st.subheader("Z = 0 介质分界面二维电场云图")

    # 构造空间网格
    x = np.linspace(-0.5, 0.5, 260)
    z = np.linspace(-0.45, 0.45, 220)

    # 构造瞬时场分布（t=0）
    X, Z, E = build_field_map_single_interface(
        freq=freq,
        theta_i=theta_i,
        theta_t=theta_t,
        r=r,
        t=t,
        x=x,
        z=z,
    )

    fig_field = plot_field_contour(
        X=X,
        Z=Z,
        field=E,
        title=f"{pol} 波瞬时电场分布（t = 0）",
    )
    st.pyplot(fig_field, clear_figure=True)

# =========================
# 教学说明
# =========================
st.markdown("---")
st.subheader("教学说明")

st.markdown(
    """
#### 1. 平面波表达式
\[
E(\mathbf r, t) = E_0 \\cos(\\mathbf k \\cdot \\mathbf r - \\omega t + \\phi)
\]

#### 2. 复介电常数
有耗介质中，利用复介电常数描述损耗：
\[
\\varepsilon_c = \\varepsilon_0 \\varepsilon_r - j\\frac{\\sigma}{\\omega}
\]

#### 3. 波阻抗
\[
\\eta = \\sqrt{\\frac{j\\omega\\mu}{\\sigma + j\\omega\\varepsilon}}
\]

#### 4. 斯涅尔定律
\[
n_1 \\sin\\theta_i = n_2 \\sin\\theta_t
\]

#### 5. 菲涅尔方程
TE 波：
\[
r_{TE} = \\frac{\\eta_2\\cos\\theta_i - \\eta_1\\cos\\theta_t}{\\eta_2\\cos\\theta_i + \\eta_1\\cos\\theta_t}
\]

TM 波：
\[
r_{TM} = \\frac{\\eta_2\\cos\\theta_t - \\eta_1\\cos\\theta_i}{\\eta_2\\cos\\theta_t + \\eta_1\\cos\\theta_i}
\]

#### 6. 金属趋肤效应
高电导率金属内的场强随深度指数衰减，可由趋肤深度表示：
\[
\\delta = \\sqrt{\\frac{2}{\\omega\\mu\\sigma}}
\]

#### 7. 多层介质
三层结构采用输入阻抗回溯法：
- 先从最底层开始求等效输入阻抗
- 再逐层向前递推
- 最终得到总反射系数

"""
)

st.caption("本项目适合电磁场课程教学、课程设计与开源部署展示。")