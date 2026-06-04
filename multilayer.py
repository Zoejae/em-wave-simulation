# physics/multilayer.py
# ------------------------------------------------------------
# 多层介质反射透射计算模块
#
# 功能：
# - 三层结构：上层半无限介质 + 中间薄层 + 底层半无限基底
# - 采用输入阻抗回溯法求总反射系数
#
# 教学思路：
# 1. 从最底层基底开始，逐层向上求等效输入阻抗
# 2. 薄层会引入相位变化与衰减
# 3. 最终在入射界面得到总反射系数 r_total
#
# 注意：
# - 这是教学版分层求解，便于理解“层层等效”的物理含义
# - 对更复杂薄膜设计，可扩展为完整传输矩阵法 TMM
# ------------------------------------------------------------

import numpy as np

from .fresnel import fresnel_single_interface, intrinsic_impedance, refractive_index
from .constants import mu0, eps0


def propagation_constant(eps_r, mu_r, sigma, omega):
    """
    传播常数 γ = α + jβ

    通式：
        γ = sqrt( jωμ (σ + jωε) )

    其中：
        α 为衰减常数
        β 为相位常数

    在有耗介质中：
    - α > 0 表示场幅值衰减
    - β 控制相位推进
    """
    mu = mu0 * mu_r
    eps = eps0 * eps_r
    return np.sqrt(1j * omega * mu * (sigma + 1j * omega * eps))


def input_impedance_recurrence(layers, freq):
    """
    输入阻抗回溯法

    参数：
    - layers: 介质层列表
      每层字典格式：
        {
          "name": "...",
          "eps_r": ...,
          "mu_r": ...,
          "sigma": ...,
          "thickness": ...   # 半无限层可设为 None
        }
    - freq: 频率（Hz）

    返回：
    - Z_in: 从最上层看进去的等效输入阻抗
    - eta_list: 各层波阻抗
    - gamma_list: 各层传播常数
    """
    omega = 2.0 * np.pi * freq

    eta_list = []
    gamma_list = []

    for layer in layers:
        eta_list.append(
            intrinsic_impedance(
                layer["eps_r"],
                layer["mu_r"],
                layer["sigma"],
                omega,
            )
        )
        gamma_list.append(
            propagation_constant(
                layer["eps_r"],
                layer["mu_r"],
                layer["sigma"],
                omega,
            )
        )

    # 从最底层开始，认为其为半无限介质
    Z_in = eta_list[-1]

    # 逐层向前回溯
    for k in range(len(layers) - 2, -1, -1):
        d = layers[k].get("thickness", None)

        if d is None:
            # 半无限层不需要传播项
            Z_load = Z_in
        else:
            """
            教学版输入阻抗公式：
                Z_in = ηk * ( Z_L + ηk tanh(γk d) ) / ( ηk + Z_L tanh(γk d) )

            其中：
            - ηk: 第 k 层波阻抗
            - Z_L: 下方等效负载阻抗
            - γk: 第 k 层传播常数
            - d : 第 k 层厚度
            """
            tanh_term = np.tanh(gamma_list[k] * d)
            Z_load = eta_list[k] * (Z_in + eta_list[k] * tanh_term) / (
                eta_list[k] + Z_in * tanh_term
            )

        Z_in = Z_load

    return Z_in, eta_list, gamma_list


def multilayer_total_reflection(layers, theta_i, freq, pol="TE"):
    """
    多层介质总反射系数与相关量

    本函数主要用于三层结构教学展示：
    上层半无限介质 + 中间薄层 + 底层半无限基底

    返回：
    - r_total: 总反射系数
    - t_total: 总透射系数（教学近似：1 + r_total）
    - theta_t_01: 第一界面的透射角
    - Z_in: 等效输入阻抗
    """
    omega = 2.0 * np.pi * freq

    # 输入阻抗回溯
    Z_in, eta_list, gamma_list = input_impedance_recurrence(layers, freq)

    # 入射侧介质的本征阻抗
    eta_inc = eta_list[0]

    # 总反射系数（从上方看到整个多层结构）
    r_total = (Z_in - eta_inc) / (Z_in + eta_inc)

    # 教学上将 t_total 近似写作 1 + r
    # 这样便于理解“入射场 = 反射场 + 透射场”的概念
    t_total = 1.0 + r_total

    # 第一界面透射角：严格采用复数斯涅尔定律
    med1 = layers[0]
    med2 = layers[1]

    # 调用单界面求解，获得第一界面的复透射角
    first = fresnel_single_interface(
        theta_i=theta_i,
        freq=freq,
        pol=pol,
        medium1={
            "eps_r": med1["eps_r"],
            "mu_r": med1["mu_r"],
            "sigma": med1["sigma"],
        },
        medium2={
            "eps_r": med2["eps_r"],
            "mu_r": med2["mu_r"],
            "sigma": med2["sigma"],
        },
    )

    return {
        "r_total": r_total,
        "t_total": t_total,
        "theta_t_01": first["theta_t"],
        "Z_in": Z_in,
        "eta_list": eta_list,
        "gamma_list": gamma_list,
    }