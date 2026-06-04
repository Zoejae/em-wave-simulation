import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 全局设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
c = 3e8
n1 = 1.0

# 侧边栏菜单
page = st.sidebar.radio("仿真功能选择", ["2D电磁波传播", "3D矢量电磁波", "反射折射仿真"])

if page == "2D电磁波传播":
    st.header("二维平面电磁波 E/B 波形动画")
    lam = st.slider("波长(m)",0.5,4.0,2.0,0.01)
    amp = st.slider("振幅(V/m)",0.2,2.0,1.0,0.01)
    f_ratio = st.slider("频率倍率",0.5,2.0,1.0,0.01)
    f = c/lam * f_ratio
    k = 2*np.pi/lam
    omega = 2*np.pi*f
    t = st.slider("时间",0.0,0.03,0.01,0.001)
    x = np.linspace(0,10,500)
    E = amp*np.sin(k*x - omega*t)
    B = amp/c*np.sin(k*x - omega*t)

    fig,ax=plt.subplots(figsize=(10,4))
    ax.plot(x,E,'r-',lw=2,label="电场E")
    ax.plot(x,B,'b-',lw=2,label="磁场B")
    ax.set_ylim(-2,2)
    ax.legend()
    ax.set_xlabel("x(m)")
    st.pyplot(fig)

elif page == "3D矢量电磁波":
    st.header("三维电磁场矢量仿真")
    lam = st.slider("波长(m)",0.5,4.0,2.0)
    amp = st.slider("振幅",0.2,2.0,1.0)
    f_scale = st.slider("频率系数",0.5,2.0,1.0)
    direct = st.radio("传播方向",["x","y"])
    grid = st.slider("网格密度",8,24,16)
    # 【修复滑块：min=0,max=1e-7,默认=5e-8，步长1e-9】
    t = st.slider("时间", 0.0, 1e-7, 5e-8, 1e-9)
    k=2*np.pi/lam
    omega=2*np.pi*(c/lam)*f_scale
    X,Y=np.meshgrid(np.linspace(0,4,grid),np.linspace(0,4,grid))
    Z=np.zeros_like(X)
    if direct=="x":
        phase = k*X - omega*t
    else:
        phase = k*Y - omega*t
    Ez = amp*np.sin(phase)
    Ex=Ey=np.zeros_like(X)
    if direct=="x":
        Bx,Bz=np.zeros_like(X),np.zeros_like(X)
        By = 0.8*np.sin(phase)
    else:
        By,Bz=np.zeros_like(X),np.zeros_like(X)
        Bx = 0.8*np.sin(phase)
    fig=plt.figure(figsize=(8,6))
    ax=fig.add_subplot(111,projection="3d")
    ax.quiver(X,Y,Z,Ex,Ey,Ez,color="red",length=0.4,label="电场E")
    ax.quiver(X,Y,Z,Bx,By,Bz,color="blue",length=0.4,label="磁场B")
    ax.legend()
    st.pyplot(fig)

elif page == "反射折射仿真":
    st.header("介质分界面反射折射(TE波)")
    theta_i = st.slider("入射角(°)",0,80,30)
    n2 = st.slider("介质2折射率n2",0.5,2.5,1.5)
    ti = np.radians(theta_i)
    sin_tt = n1/n2*np.sin(ti)
    total = abs(sin_tt)>=1
    if total:
        tt_deg=90.0
        r=1.0
        t=0.0
    else:
        tt_deg=np.degrees(np.arcsin(sin_tt))
        cost=np.cos(np.radians(tt_deg))
        cosi=np.cos(ti)
        denom=n1*cosi+n2*cost
        r=(n1*cosi-n2*cost)/denom
        t=2*n1*cosi/denom
    st.write(f"折射角:{tt_deg:.1f}°,反射系数r={r:.3f},透射系数t={t:.3f}")
    fig=plt.figure(figsize=(8,6))
    ax=fig.add_subplot(111,projection="3d")
    xx,yy=np.meshgrid([-1.5,1.5],[-1.2,1.2])
    ax.plot_surface(xx,yy,np.zeros_like(xx),alpha=0.25,color="lightblue")
    ax.quiver(0,0,-0.9, 0,0,1.8,color="gray")
    incd=np.array([np.sin(ti),0,-np.cos(ti)])
    refd=np.array([np.sin(ti),0,np.cos(ti)])
    al=0.9
    stinc=-incd*al
    ax.quiver(stinc[0],stinc[1],stinc[2],incd[0],incd[1],incd[2],color="red",label="入射")
    ax.quiver(0,0,0,refd[0],refd[1],refd[2],color="orange",label="反射")
    if not total:
        ttd=np.array([np.sin(np.radians(tt_deg)),0,-np.cos(np.radians(tt_deg))])
        ax.quiver(0,0,0,ttd[0],ttd[1],ttd[2],color="green",label="透射")
    ax.legend()
    st.pyplot(fig)
