# physics/fresnel.py
# ------------------------------------------------------------
# 菲涅尔方程模块
#
# 功能：
# 1. 复介电常数
# 2. 有耗介质波阻抗
# 3. 复折射率
# 4. 斯涅尔定律（复数形式）
# 5. 单界面 TE/TM 反射与透射系数
#
# 教学重点：
# - 无耗介质：σ = 0，此时 ε 为实数
# - 有耗介质：σ > 0，此时用复介电常数描述损耗
# - 金属：高电导率下，场在介质中快速衰减，体现趋肤效应
# ------------------------------------------------------------

import numpy as np

from .constants import mu0, eps0


def complex_permittivity(eps_r, sigma, omega):
    """
    复介电常数 εc

    对有耗介质：
        εc = ε0 εr - j σ / ω

    物理意义：
    - 实部：储能能力
    - 虚部：损耗能力
    """
    return eps0 * eps_r - 1j * sigma / omega


def intrinsic_impedance(eps_r, mu_r, sigma, omega):
    """
    有耗介质波阻抗 η

    通式：
        η = sqrt( jωμ / (σ + jωε) )

    当 σ = 0 时：
        η = sqrt( μ / ε )

    物理意义：
    - 波阻抗越大，表示电场相对磁场越强
    - 金属中由于 σ 很大，η 很小，电磁波难以深入
    """
    mu = mu0 * mu_r
    eps = eps0 * eps_r
    return np.sqrt(1j * omega * mu / (sigma + 1j * omega * eps))


def refractive_index(eps_r, mu_r, sigma, omega):
    """
    复折射率 n

    教学上可写作：
        n = sqrt( μr * εr_complex )

    其中：
        εr_complex = εr - j σ / (ω ε0)

    注意：
    - 这里返回复数折射率，用于描述有耗介质中的相位传播与衰减
    """
    eps_r_complex = eps_r - 1j * sigma / (omega * eps0)
    return np.sqrt(mu_r * eps_r_complex)


def snell_complex(theta_i, n1, n2):
    """
    复数斯涅尔定律

    n1 sinθi = n2 sinθt

    因而：
        θt = arcsin( n1 sinθi / n2 )

    参数可为复数，适合有耗介质或金属场景。
    返回值为复数角度。
    """
    return np.arcsin(n1 * np.sin(theta_i) / n2)


def fresnel_single_interface(theta_i, freq, pol, medium1, medium2):
    """
    单界面 Fresnel 反射/透射系数计算

    参数：
    - theta_i: 入射角（弧度）
    - freq   : 频率（Hz）
    - pol    : "TE" 或 "TM"
    - medium1: 上层介质参数字典 {eps_r, mu_r, sigma}
    - medium2: 下层介质参数字典 {eps_r, mu_r, sigma}

    返回：
    - r: 复反射系数
    - t: 复透射系数
    - theta_t: 复透射角
    - n1, n2: 复折射率
    - eta1, eta2: 波阻抗
    """
    omega = 2.0 * np.pi * freq

    eps1, mu1, sigma1 = medium1["eps_r"], medium1["mu_r"], medium1["sigma"]
    eps2, mu2, sigma2 = medium2["eps_r"], medium2["mu_r"], medium2["sigma"]

    # 复折射率
    n1 = refractive_index(eps1, mu1, sigma1, omega)
    n2 = refractive_index(eps2, mu2, sigma2, omega)

    # 复透射角：严格使用复数斯涅尔定律求解
    theta_t = snell_complex(theta_i, n1, n2)

    # 介质波阻抗
    eta1 = intrinsic_impedance(eps1, mu1, sigma1, omega)
    eta2 = intrinsic_impedance(eps2, mu2, sigma2, omega)

    ci = np.cos(theta_i)
    ct = np.cos(theta_t)

    pol = pol.upper().strip()

    if pol == "TE":
        """
        TE（s偏振）：
        电场垂直入射面

        反射系数：
            rTE = (η2 cosθi - η1 cosθt) / (η2 cosθi + η1 cosθt)

        透射系数：
            tTE = 2η2 cosθi / (η2 cosθi + η1 cosθt)
        """
        r = (eta2 * ci - eta1 * ct) / (eta2 * ci + eta1 * ct)
        t = (2.0 * eta2 * ci) / (eta2 * ci + eta1 * ct)
    else:
        """
        TM（p偏振）：
        磁场垂直入射面

        反射系数：
            rTM = (η2 cosθt - η1 cosθi) / (η2 cosθt + η1 cosθi)

        透射系数：
            tTM = 2η2 cosθi / (η2 cosθt + η1 cosθi)
        """
        r = (eta2 * ct - eta1 * ci) / (eta2 * ct + eta1 * ci)
        t = (2.0 * eta2 * ci) / (eta2 * ct + eta1 * ci)

    return {
        "r": r,
        "t": t,
        "theta_t": theta_t,
        "n1": n1,
        "n2": n2,
        "eta1": eta1,
        "eta2": eta2,
        "omega": omega,
    }