# physics/wavefield.py
# ------------------------------------------------------------
# 平面波时域表达式与二维电场分布生成
#
# 功能：
# 1. 构造入射波、反射波、透射波
# 2. 在 Z=0 分界面上下分别叠加
# 3. 生成二维空间电场分布，用于云图绘制
#
# 教学说明：
# - 此处以瞬时场 (t=0) 为主，便于展示波前与反射透射
# - 代码中保留时域表达式，方便未来扩展动画
# ------------------------------------------------------------

import numpy as np

from .constants import c0
from .fresnel import refractive_index


def plane_wave_field(x, z, t, freq, theta, amplitude=1.0, phase=0.0, direction=1):
    """
    平面波瞬时场表达式

    E(x, z, t) = A cos( kx x + kz z - ωt + φ )

    参数：
    - direction = 1 : 沿 +z 方向传播
    - direction = -1: 沿 -z 方向传播

    说明：
    - 此处使用真空中的 k0 = ω/c0 作为展示基准
    - 在教学可视化中，该表达式足以表达传播方向与波前形态
    """
    omega = 2.0 * np.pi * freq
    k0 = omega / c0

    kx = k0 * np.sin(theta)
    kz = k0 * np.cos(theta) * direction

    return amplitude * np.cos(kx * x + kz * z - omega * t + phase)


def build_field_map_single_interface(freq, theta_i, theta_t, r, t, x, z):
    """
    构造单界面二维电场分布

    设界面位于 Z = 0：
    - Z < 0：入射波 + 反射波
    - Z >= 0：透射波

    参数：
    - freq   : 频率
    - theta_i: 入射角（弧度）
    - theta_t: 透射角（复数），这里使用其实部参与空间方向展示
    - r, t   : 复反射/透射系数
    - x, z   : 空间网格

    返回：
    - X, Z, E: 网格和电场值
    """
    X, Z = np.meshgrid(x, z)

    # 教学展示时，取透射角实部表示波前方向
    # 注意：在有耗介质中 theta_t 可能为复数，其虚部对应衰减信息
    theta_t_real = float(np.real(theta_t))

    # 入射波
    Ei = plane_wave_field(
        X, Z,
        t=0.0,
        freq=freq,
        theta=theta_i,
        amplitude=1.0,
        phase=0.0,
        direction=1,
    )

    # 反射波：传播方向相反，幅值由 |r| 调制，实部/虚部共同决定相位
    Er = np.abs(r) * plane_wave_field(
        X, Z,
        t=0.0,
        freq=freq,
        theta=theta_i,
        amplitude=1.0,
        phase=np.angle(r),
        direction=-1,
    )

    # 透射波：Z>=0 区域，幅值由 |t| 调制
    # 复透射系数的相位用于展示透射波的相位变化
    Et = np.abs(t) * plane_wave_field(
        X, Z,
        t=0.0,
        freq=freq,
        theta=theta_t_real,
        amplitude=1.0,
        phase=np.angle(t),
        direction=1,
    )

    # 分界面叠加
    E = np.where(Z < 0.0, Ei + Er, Et)

    return X, Z, E