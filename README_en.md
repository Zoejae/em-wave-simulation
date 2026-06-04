# Electromagnetic Wave Reflection and Transmission Simulator

This is an open-source educational platform for the course of Electromagnetic Fields and Waves.
It is built with Python, Streamlit, NumPy, and Matplotlib.

---

## Features

- TE / TM polarization switching
- Frequency tuning from 0.1 to 20 GHz
- Incident angle tuning from 0° to 89°
- Material selection: air, glass, water, semiconductor, copper, aluminum, custom medium
- Single-interface reflection/transmission
- Three-layer medium mode
- Real-time coefficient update
- 2D electric field contour visualization

---

## Project Structure

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