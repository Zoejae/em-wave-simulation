import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import tkinter as tk
from tkinter import ttk
import warnings

# 忽略无关警告
warnings.filterwarnings("ignore", category=UserWarning, module="mpl_toolkits.mplot3d")
# 全局中文/负号设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ===================== 通用物理常数 =====================
c = 3e8  # 光速 (m/s)
n1 = 1.0  # 介质1折射率（空气）

# ===================== 2D电磁波传播模块 =====================
class EMWave2D:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始化参数
        self.lambda0 = 2.0    # 初始波长 (m)
        self.f0 = c / self.lambda0  # 初始频率 (Hz)
        self.A0 = 1.0         # 初始电场振幅
        self.x = np.linspace(0, 10, 500)
        
        # 创建画布
        self.fig, self.ax = plt.subplots(figsize=(10,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 初始化绘图元素
        self.lineE, = self.ax.plot(self.x, np.zeros_like(self.x), 'r-', label='电场 E', linewidth=2)
        self.lineB, = self.ax.plot(self.x, np.zeros_like(self.x), 'b-', label='磁场 B', linewidth=2)
        self.title = self.ax.text(0.5, 1.05, "", transform=self.ax.transAxes, ha='center', fontsize=13)
        
        # 坐标轴设置
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-2, 2)
        self.ax.set_xlabel('x (m)')
        self.ax.set_ylabel('振幅 (V/m, T)')
        self.ax.legend(loc='upper right')
        self.fig.subplots_adjust(left=0.07, right=0.98, bottom=0.25, top=0.90)
        
        # 创建滑块
        axcolor = 'lightgoldenrodyellow'
        self.ax_lamb = plt.axes([0.12, 0.13, 0.35, 0.03], facecolor=axcolor)
        self.ax_freq = plt.axes([0.6, 0.13, 0.30, 0.03], facecolor=axcolor)
        self.ax_amp = plt.axes([0.12, 0.08, 0.78, 0.03], facecolor=axcolor)
        
        self.lamb_slider = Slider(self.ax_lamb, '波长λ(m)', 0.5, 4.0, valinit=self.lambda0, valstep=0.01)
        self.freq_slider = Slider(self.ax_freq, '频率(Hz)', 0.5 * self.f0, 2.0 * self.f0, valinit=self.f0, valstep=0.01)
        self.amp_slider = Slider(self.ax_amp, '振幅(V/m)', 0.2, 2.0, valinit=self.A0, valstep=0.01)
        
        # 动画
        self.ani = FuncAnimation(self.fig, self.update, frames=np.linspace(0, 0.03, 200), 
                                 interval=40, blit=True)

    def get_wave_params(self):
        lam = self.lamb_slider.val
        amp = self.amp_slider.val
        freq = self.freq_slider.val
        return lam, amp, freq

    def update(self, frame):
        lam, amp, freq = self.get_wave_params()
        k = 2*np.pi / lam
        omega = 2*np.pi * freq

        # 电场+磁场计算
        E = amp * np.sin(k * self.x - omega * frame)
        B = (amp / c) * np.sin(k * self.x - omega * frame)

        self.lineE.set_ydata(E)
        self.lineB.set_ydata(B)
        self.title.set_text(f"电磁波传播  波长: {lam:.2f}m  频率: {freq:.2f}Hz  振幅: {amp:.2f}V/m")
        return self.lineE, self.lineB, self.title

# ===================== 电磁波反射折射模块 =====================
class EMWaveReflection:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始参数
        self.default_theta_i_deg = 30.0  # 入射角 (度)
        self.default_n2 = 1.5            # 介质2折射率
        
        # 创建画布
        self.fig = plt.Figure(figsize=(10,7))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 滑块区域
        self.fig.subplots_adjust(left=0.15, bottom=0.25)
        self.ax_theta = plt.axes([0.2, 0.1, 0.6, 0.03])
        self.ax_n2 = plt.axes([0.2, 0.05, 0.6, 0.03])
        
        # 创建滑块
        self.slider_theta = Slider(self.ax_theta, '入射角 (度)', 0, 80, 
                                   valinit=self.default_theta_i_deg, valstep=1)
        self.slider_n2 = Slider(self.ax_n2, '介质2折射率 n2', 0.5, 2.5, 
                                valinit=self.default_n2, valstep=0.01)
        
        # 绑定回调
        self.slider_theta.on_changed(self.update)
        self.slider_n2.on_changed(self.update)
        
        # 初始绘图
        self.update()

    def compute_angles(self, theta_i_deg, n2):
        """计算反射角、折射角(度) 和 反射/透射系数 (TE波)"""
        theta_i = np.radians(theta_i_deg)
        theta_r_deg = theta_i_deg  # 反射角=入射角
        
        # 折射角（斯涅耳定律）
        sin_theta_t = (n1 / n2) * np.sin(theta_i)
        if abs(sin_theta_t) >= 1.0:
            theta_t_deg = 90.0
            total_reflection = True
        else:
            theta_t_deg = np.degrees(np.arcsin(sin_theta_t))
            total_reflection = False
        
        # 菲涅耳公式 (TE波)
        cos_i = np.cos(theta_i)
        if not total_reflection:
            cos_t = np.cos(np.radians(theta_t_deg))
            denom = n1 * cos_i + n2 * cos_t
            r = (n1 * cos_i - n2 * cos_t) / denom if denom != 0 else 1.0
            t = 2 * n1 * cos_i / denom if denom != 0 else 0.0
        else:
            r = 1.0
            t = 0.0
        
        return theta_r_deg, theta_t_deg, r, t, total_reflection

    def update(self, val=None):
        theta_i_deg = self.slider_theta.val
        n2 = self.slider_n2.val
        theta_r_deg, theta_t_deg, r, t, total_ref = self.compute_angles(theta_i_deg, n2)

        # 清除旧图
        self.ax.cla()

        # 坐标轴设置
        self.ax.set_xlim([-1.5, 1.5])
        self.ax.set_ylim([-1.2, 1.2])
        self.ax.set_zlim([-1.2, 1.2])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # 标题
        self.ax.set_title(
            f'电磁波反射与折射 (n1=1.0, n2={n2:.2f})\n'
            f'θi={theta_i_deg:.1f}°, θr={theta_r_deg:.1f}°, θt={theta_t_deg:.1f}°\n'
            f'反射系数r={r:.3f}, 透射系数t={t:.3f}', fontsize=11
        )

        # 绘制分界面 (z=0平面)
        xx, yy = np.meshgrid(np.linspace(-1.5, 1.5, 2), np.linspace(-1.2, 1.2, 2))
        self.ax.plot_surface(xx, yy, np.zeros_like(xx), alpha=0.25, color='lightblue', edgecolor='none')

        # 法线（z轴）
        self.ax.quiver(0, 0, -0.9, 0, 0, 1.8, color='gray', alpha=0.6,
                       arrow_length_ratio=0.08, linewidth=1.5)

        # 波矢方向计算
        theta_i_rad = np.radians(theta_i_deg)
        inc_dir = np.array([np.sin(theta_i_rad), 0, -np.cos(theta_i_rad)])  # 入射波
        ref_dir = np.array([np.sin(theta_i_rad), 0, np.cos(theta_i_rad)])   # 反射波
        
        # 透射波
        if not total_ref:
            theta_t_rad = np.radians(theta_t_deg)
            trans_dir = np.array([np.sin(theta_t_rad), 0, -np.cos(theta_t_rad)])
        else:
            trans_dir = None

        # 绘制波矢箭头
        arrow_len = 0.9
        # 入射波
        start_inc = -inc_dir * arrow_len
        self.ax.quiver(start_inc[0], start_inc[1], start_inc[2],
                       inc_dir[0], inc_dir[1], inc_dir[2],
                       color='red', arrow_length_ratio=0.18, linewidth=2, label='入射波')
        # 反射波
        self.ax.quiver(0, 0, 0, ref_dir[0], ref_dir[1], ref_dir[2],
                       color='orange', arrow_length_ratio=0.18, linewidth=2, label='反射波')
        # 透射波
        if trans_dir is not None:
            self.ax.quiver(0, 0, 0, trans_dir[0], trans_dir[1], trans_dir[2],
                           color='green', arrow_length_ratio=0.18, linewidth=2, label='透射波')

        # 角度标注
        arc_radius = 0.45
        # 入射角
        angles_i = np.linspace(0, theta_i_rad, 30)
        arc_x_i = arc_radius * np.sin(angles_i)
        arc_z_i = arc_radius * np.cos(angles_i)
        self.ax.plot(arc_x_i, np.zeros_like(arc_x_i), arc_z_i, color='black', linewidth=1)
        mid_i = theta_i_rad / 2
        self.ax.text(arc_radius * 1.1 * np.sin(mid_i), 0,
                     arc_radius * 1.1 * np.cos(mid_i),
                     f'{theta_i_deg:.0f}°', fontsize=9, ha='center', va='center')
        # 反射角
        angles_r = np.linspace(0, theta_i_rad, 30)
        arc_x_r = arc_radius * np.sin(angles_r)
        arc_z_r = arc_radius * np.cos(angles_r)
        self.ax.plot(-arc_x_r, np.zeros_like(arc_x_r), arc_z_r, color='black', linewidth=1)
        self.ax.text(-arc_radius * 1.1 * np.sin(mid_i), 0,
                     arc_radius * 1.1 * np.cos(mid_i),
                     f'{theta_r_deg:.0f}°', fontsize=9, ha='center', va='center')
        # 折射角
        if not total_ref and theta_t_deg > 0:
            theta_t_rad = np.radians(theta_t_deg)
            angles_t = np.linspace(0, theta_t_rad, 30)
            arc_x_t = arc_radius * np.sin(angles_t)
            arc_z_t = -arc_radius * np.cos(angles_t)
            self.ax.plot(arc_x_t, np.zeros_like(arc_x_t), arc_z_t, color='black', linewidth=1)
            mid_t = theta_t_rad / 2
            self.ax.text(arc_radius * 1.1 * np.sin(mid_t), 0,
                         -arc_radius * 1.1 * np.cos(mid_t),
                         f'{theta_t_deg:.0f}°', fontsize=9, ha='center', va='center')

        # 介质标注
        self.ax.text(0, 1.0, 0.85, '介质1 (n1=1.0)', ha='center', fontsize=10, color='darkblue')
        self.ax.text(0, 1.0, -0.85, f'介质2 (n2={n2:.2f})', ha='center', fontsize=10, color='darkgreen')

        # 图例+比例
        self.ax.legend(loc='upper left', fontsize=8)
        self.ax.set_box_aspect([1.5, 1, 1])
        
        # 刷新
        self.canvas.draw_idle()

# ===================== 3D电磁波传播模块 =====================
class EMWave3D:
    def __init__(self, parent):
        self.root = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # 默认参数
        self.lambda0 = 2.0
        self.f0 = c / self.lambda0
        self.A0 = 1.0
        self.freq = self.f0
        self.amp = self.A0
        self.wavelength = self.lambda0
        self.direction = "x"
        self.grid_points = 16
        self.is_animating = True
        self.frame_count = 0
        self.anim_speed = 40

        # 布局：左侧控制面板 + 右侧画布
        main_pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # 左侧控制面板
        left_frame = ttk.Frame(main_pane, width=280, relief=tk.RIDGE, padding=10)
        main_pane.add(left_frame, weight=0)

        # 右侧画布
        right_frame = ttk.Frame(main_pane, relief=tk.SUNKEN)
        main_pane.add(right_frame, weight=1)

        # 创建matplotlib画布
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 控制面板UI
        self.setup_control_panel(left_frame)
        # 初始化网格+参数
        self.update_grid()
        self.on_param_change()
        # 启动动画
        self.animate()

    def setup_control_panel(self, parent):
        # 标题
        ttk.Label(parent, text="3D电磁波参数调节", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10)

        # 波长
        ttk.Label(parent, text="波长 (m):").grid(row=1, column=0, sticky="w", pady=2)
        self.lambda_var = tk.DoubleVar(value=self.lambda0)
        lambda_scale = ttk.Scale(parent, from_=0.5, to=4.0, orient=tk.HORIZONTAL,
                                 variable=self.lambda_var, command=self.on_param_change)
        lambda_scale.grid(row=1, column=1, sticky="ew", padx=5)
        self.lambda_label = ttk.Label(parent, text=f"{self.lambda0:.2f}")
        self.lambda_label.grid(row=2, column=1, sticky="w", padx=5)
        self.lambda_var.trace_add("write", lambda *a: self.lambda_label.config(
            text=f"{self.lambda_var.get():.2f}"))

        # 频率
        ttk.Label(parent, text="频率 (Hz):").grid(row=3, column=0, sticky="w", pady=2)
        self.freq_rel_var = tk.DoubleVar(value=1.0)
        freq_scale = ttk.Scale(parent, from_=0.5, to=2.0, orient=tk.HORIZONTAL,
                               variable=self.freq_rel_var, command=self.on_param_change)
        freq_scale.grid(row=3, column=1, sticky="ew", padx=5)
        self.freq_label = ttk.Label(parent, text=f"{self.f0:.2e}")
        self.freq_label.grid(row=4, column=1, sticky="w", padx=5)
        self.freq_rel_var.trace_add("write", lambda *a: self.update_freq_label())

        # 振幅
        ttk.Label(parent, text="振幅 (V/m):").grid(row=5, column=0, sticky="w", pady=2)
        self.amp_var = tk.DoubleVar(value=self.A0)
        amp_scale = ttk.Scale(parent, from_=0.2, to=2.0, orient=tk.HORIZONTAL,
                              variable=self.amp_var, command=self.on_param_change)
        amp_scale.grid(row=5, column=1, sticky="ew", padx=5)
        self.amp_label = ttk.Label(parent, text=f"{self.A0:.2f}")
        self.amp_label.grid(row=6, column=1, sticky="w", padx=5)
        self.amp_var.trace_add("write", lambda *a: self.amp_label.config(
            text=f"{self.amp_var.get():.2f}"))

        # 传播方向
        ttk.Label(parent, text="传播方向:").grid(row=7, column=0, sticky="w", pady=5)
        self.dir_var = tk.StringVar(value="x")
        ttk.Radiobutton(parent, text="沿 X 轴", variable=self.dir_var, value="x",
                        command=self.on_param_change).grid(row=7, column=1, sticky="w")
        ttk.Radiobutton(parent, text="沿 Y 轴", variable=self.dir_var, value="y",
                        command=self.on_param_change).grid(row=8, column=1, sticky="w")

        # 网格密度
        ttk.Label(parent, text="网格密度 (箭头数):").grid(row=9, column=0, sticky="w", pady=5)
        self.grid_var = tk.IntVar(value=self.grid_points)
        grid_scale = ttk.Scale(parent, from_=8, to=24, orient=tk.HORIZONTAL,
                               variable=self.grid_var, command=self.on_grid_change)
        grid_scale.grid(row=9, column=1, sticky="ew", padx=5)
        self.grid_label = ttk.Label(parent, text=f"{self.grid_points}")
        self.grid_label.grid(row=10, column=1, sticky="w", padx=5)
        self.grid_var.trace_add("write", lambda *a: self.grid_label.config(
            text=f"{self.grid_var.get()}"))

        # 播放/暂停
        self.play_pause_btn = ttk.Button(parent, text="暂停", command=self.toggle_animation)
        self.play_pause_btn.grid(row=11, column=0, columnspan=2, pady=15, ipadx=10)

        # 重置
        self.reset_btn = ttk.Button(parent, text="重置", command=self.reset_params)
        self.reset_btn.grid(row=12, column=0, columnspan=2, pady=5, ipadx=10)
        
        # 保存数据
        self.save_btn = ttk.Button(parent, text="保存场数据", command=self.save_current_field)
        self.save_btn.grid(row=13, column=0, columnspan=2, pady=5)

        # 图例说明
        info = ttk.LabelFrame(parent, text="图例", padding=5)
        info.grid(row=14, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(info, text="红色箭头: 电场 E\n蓝色箭头: 磁场 B\n横波，沿X/Y轴传播").pack(anchor=tk.W)

        parent.columnconfigure(1, weight=1)

    def update_freq_label(self):
        rel = self.freq_rel_var.get()
        freq_val = rel * self.f0
        self.freq_label.config(text=f"{freq_val:.2e}")

    def on_param_change(self, event=None):
        self.wavelength = self.lambda_var.get()
        self.amp = self.amp_var.get()
        self.freq = self.freq_rel_var.get() * self.f0
        self.direction = self.dir_var.get()
        self.k = 2 * np.pi / self.wavelength
        self.omega = 2 * np.pi * self.freq
        self.draw_quiver()

    def on_grid_change(self, event=None):
        self.grid_points = self.grid_var.get()
        self.update_grid()
        self.draw_quiver()

    def update_grid(self):
        n = self.grid_points
        x_min, x_max = 0, 4
        y_min, y_max = 0, 4
        x = np.linspace(x_min, x_max, n)
        y = np.linspace(y_min, y_max, n)
        self.X, self.Y = np.meshgrid(x, y)
        self.Z = np.zeros_like(self.X)
        self.xlim = (x_min, x_max)
        self.ylim = (y_min, y_max)
        self.zlim = (-2, 2)

    def compute_vectors(self, t):
        # 相位计算
        if self.direction == "x":
            phase = self.k * self.X - self.omega * t
        else:
            phase = self.k * self.Y - self.omega * t

        # 电场（Z方向）
        E_z = self.amp * np.sin(phase)
        Ex, Ey = np.zeros_like(self.X), np.zeros_like(self.X)
        Ez = E_z

        # 磁场（垂直于电场+传播方向）
        if self.direction == "x":
            Bx, Bz = np.zeros_like(self.X), np.zeros_like(self.X)
            By = np.sin(phase) * 0.8
        else:
            By, Bz = np.zeros_like(self.X), np.zeros_like(self.X)
            Bx = np.sin(phase) * 0.8

        return (Ex, Ey, Ez), (Bx, By, Bz)

    def draw_quiver(self):
        t = self.frame_count * (self.anim_speed / 1000.0)
        E_vec, B_vec = self.compute_vectors(t)

        # 清空轴
        self.ax.clear()

        # 坐标轴范围
        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)
        self.ax.set_zlim(*self.zlim)
        # 坐标轴标签
        self.ax.set_xlabel('X (传播方向)' if self.direction == 'x' else 'X')
        self.ax.set_ylabel('Y' if self.direction == 'x' else 'Y (传播方向)')
        self.ax.set_zlabel('电场E / 磁场B')

        # 绘制矢量箭头
        self.ax.quiver(self.X, self.Y, self.Z,
                       E_vec[0], E_vec[1], E_vec[2],
                       length=0.4, color='red', alpha=0.8, label='电场 E')
        self.ax.quiver(self.X, self.Y, self.Z,
                       B_vec[0], B_vec[1], B_vec[2],
                       length=0.4, color='blue', alpha=0.8, label='磁场 B')

        # 标题
        dir_text = "X轴" if self.direction == 'x' else "Y轴"
        self.ax.set_title(
            f"3D电磁波传播 ({dir_text})  λ={self.wavelength:.2f}m  f={self.freq:.2e}Hz  A={self.amp:.2f}V/m",
            fontsize=12
        )
        self.ax.legend(loc='upper right', fontsize=8)
        self.canvas.draw_idle()

    def animate(self):
        if self.is_animating:
            self.draw_quiver()
            self.frame_count += 1
        self.root.after(self.anim_speed, self.animate)

    def toggle_animation(self):
        self.is_animating = not self.is_animating
        self.play_pause_btn.config(text="播放" if not self.is_animating else "暂停")

    def reset_params(self):
        self.lambda_var.set(self.lambda0)
        self.freq_rel_var.set(1.0)
        self.amp_var.set(self.A0)
        self.dir_var.set("x")
        self.grid_var.set(16)
        self.on_param_change()

    def save_current_field(self):
        t = self.frame_count * (self.anim_speed / 1000.0)
        E_vec, B_vec = self.compute_vectors(t)
        
        np.savez('3D电磁场数据.npz',
                 X=self.X, Y=self.Y, Z=self.Z,
                 Ex=E_vec[0], Ey=E_vec[1], Ez=E_vec[2],
                 Bx=B_vec[0], By=B_vec[1], Bz=B_vec[2],
                 frame=self.frame_count, t=t,
                 direction=self.direction,
                 wavelength=self.wavelength,
                 amp=self.amp,
                 freq=self.freq)
        print("3D电磁场数据已保存到 3D电磁场数据.npz")

# ===================== 主程序 =====================
class EMWaveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("电磁波仿真整合工具")
        self.root.geometry("1200x800")

        # 创建选项卡
        self.tab_control = ttk.Notebook(root)
        
        # 添加三个功能选项卡
        self.tab_2d = ttk.Frame(self.tab_control)
        self.tab_reflect = ttk.Frame(self.tab_control)
        self.tab_3d = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_2d, text='2D电磁波传播')
        self.tab_control.add(self.tab_reflect, text='电磁波反射折射')
        self.tab_control.add(self.tab_3d, text='3D电磁波传播')
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        # 初始化各模块
        self.wave_2d = EMWave2D(self.tab_2d)
        self.wave_reflect = EMWaveReflection(self.tab_reflect)
        self.wave_3d = EMWave3D(self.tab_3d)

if __name__ == "__main__":
    root = tk.Tk()
    app = EMWaveApp(root)
    root.mainloop()
