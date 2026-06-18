"""
生成 "Coordinate frames" SVG 示意图
展示 ECI 和 LVLH 坐标系、目标卫星及来袭星群
"""
import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import (Circle, Ellipse, Arc, Polygon, Wedge,
                                  FancyArrowPatch, FancyBboxPatch)
import matplotlib.patches as mpatches

# ============================================================
# 样式配置
# ============================================================
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Liberation Serif'],
    'font.size': 10,
    'mathtext.fontset': 'stix',
    'svg.fonttype': 'none',       # 保留文本为可编辑文字
    'figure.dpi': 150,
    'axes.titlesize': 13,
    'axes.labelsize': 10,
})

fig, ax = plt.subplots(figsize=(11, 9.5))
ax.set_aspect('equal')
ax.set_xlim(-4.8, 7.0)
ax.set_ylim(-4.5, 6.0)
ax.axis('off')

# ============================================================
# 颜色定义
# ============================================================
C_EARTH_FILL   = '#4989C4'
C_EARTH_EDGE   = '#2B5F8A'
C_EARTH_GRID   = '#FFFFFF'
C_ECI_X        = '#222222'
C_ECI_Y        = '#444444'
C_ECI_Z        = '#222222'
C_ORBIT        = '#B03A2E'
C_ORBIT_NORMAL = '#922B21'
C_SAT_BODY     = '#1C2833'
C_SAT_PANEL    = '#2E86C1'
C_XL           = '#D35400'
C_YL           = '#1E8449'
C_ZL           = '#7D3C98'
C_CHASER       = ['#CB4335', '#D4AC0D', '#CB4335', '#D4AC0D']
C_APPROACH     = '#7F8C8D'
C_EQUATOR      = '#AAB7B8'

# ============================================================
# 几何参数
# ============================================================
r_earth     = 1.0              # 地球半径
orbit_r     = 2.9              # 轨道半径（3D）
inclination = np.deg2rad(52)   # 轨道倾角
theta_sat   = np.deg2rad(38)   # 目标卫星在轨道上的角度（从升交点量起）

# 轨道椭圆投影：a = orbit_r, b = orbit_r * cos(i)
orbit_a = orbit_r
orbit_b = orbit_r * np.cos(inclination)

# 目标卫星在 2D 投影中的位置
sat_x_3d = orbit_r * np.cos(theta_sat)
sat_y_3d = orbit_r * np.sin(theta_sat) * np.sin(inclination)  # out-of-page
sat_z_3d = orbit_r * np.sin(theta_sat) * np.cos(inclination)  # projected Z
sat_x = sat_x_3d
sat_y = sat_z_3d   # 投影 Z → 图的 Y 轴

# ============================================================
# 1. 赤道面示意（虚线）
# ============================================================
equator_line_x = np.linspace(-4.0, 6.5, 200)
ax.plot(equator_line_x, np.zeros_like(equator_line_x),
        color=C_EQUATOR, linestyle=':', linewidth=1.0, alpha=0.5, zorder=1)
ax.text(5.0, 0.25, 'Equatorial plane', fontsize=8, ha='center', va='bottom',
        style='italic', color=C_EQUATOR)

# ============================================================
# 2. 地球
# ============================================================
earth = Circle((0, 0), r_earth, facecolor=C_EARTH_FILL, edgecolor=C_EARTH_EDGE,
               linewidth=2.2, zorder=4, alpha=0.92)
ax.add_patch(earth)

# 经纬网（增加立体感）
for lat_angle in [-40, 0, 40]:
    r_proj = r_earth * np.cos(np.deg2rad(lat_angle))
    lat_arc = Arc((0, 0), 2*r_earth, 2*abs(r_proj), angle=0,
                  theta1=0, theta2=360,
                  color=C_EARTH_GRID, linewidth=0.5, alpha=0.45, zorder=5)
    ax.add_patch(lat_arc)

for lon_angle in [-45, 0, 45]:
    a = r_earth * abs(np.cos(np.deg2rad(lon_angle)))
    b = r_earth
    lon_arc = Arc((0, 0), 2*a, 2*b, angle=0,
                  theta1=-70, theta2=70,
                  color=C_EARTH_GRID, linewidth=0.5, alpha=0.45, zorder=5)
    ax.add_patch(lon_arc)

# 中心点 O_I
ax.plot(0, 0, 'o', markersize=3, color='black', zorder=10)
ax.annotate(r'$O_{\mathrm{I}}$', xy=(0, 0), xytext=(-0.22, -0.42),
            fontsize=13, fontweight='bold', ha='center', va='top', zorder=18)

# ============================================================
# 3. ECI 坐标系
# ============================================================
# X_I 轴（水平向右，春分点方向）
ax.annotate('', xy=(5.0, 0), xytext=(1.08, 0),
            arrowprops=dict(arrowstyle='->', color=C_ECI_X, lw=2.2,
                           shrinkA=0, shrinkB=0), zorder=12)
ax.text(5.25, -0.30, r'$X_{\mathrm{I}}$ (Vernal equinox)',
        fontsize=10, ha='left', va='top', color=C_ECI_X)

# Z_I 轴（垂直向上，北极方向）
ax.annotate('', xy=(0, 5.0), xytext=(0, 1.08),
            arrowprops=dict(arrowstyle='->', color=C_ECI_Z, lw=2.2,
                           shrinkA=0, shrinkB=0), zorder=12)
ax.text(0.18, 5.25, r'$Z_{\mathrm{I}}$ (Celestial north pole)',
        fontsize=10, ha='left', va='bottom', color=C_ECI_Z)

# Y_I 轴（垂直纸面向里，右手系：X×Y=Z）
# 使用 ⊗（圆内画×）表示"垂直纸面向里"
y_dot_x, y_dot_y = -0.5, 0.5
# 画一个×符号（circle-cross）表示 Y_I 指向纸内
circle_cross_radius = 0.15
cross_circle = Circle((y_dot_x, y_dot_y), circle_cross_radius,
                       facecolor='white', edgecolor=C_ECI_Y, linewidth=2.0, zorder=13)
ax.add_patch(cross_circle)
# × 的两条线
cross_size = circle_cross_radius * 0.65
ax.plot([y_dot_x - cross_size, y_dot_x + cross_size],
        [y_dot_y - cross_size, y_dot_y + cross_size],
        color=C_ECI_Y, linewidth=1.8, solid_capstyle='round', zorder=14)
ax.plot([y_dot_x - cross_size, y_dot_x + cross_size],
        [y_dot_y + cross_size, y_dot_y - cross_size],
        color=C_ECI_Y, linewidth=1.8, solid_capstyle='round', zorder=14)
ax.text(y_dot_x + 0.35, y_dot_y - 0.05, r'$Y_{\mathrm{I}}$',
        fontsize=10, ha='left', va='center', color=C_ECI_Y)
ax.text(y_dot_x + 0.35, y_dot_y - 0.45, '(into page)',
        fontsize=7.5, ha='left', va='center', style='italic', color=C_EQUATOR)

# ECI 标签
ax.text(3.8, 4.5, r'$\mathcal{F}_{\mathrm{I}}$: ECI', fontsize=9,
        ha='center', va='center', style='italic', color='gray',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                  edgecolor='lightgray', alpha=0.7))

# ============================================================
# 4. 轨道及其法线
# ============================================================
# 轨道椭圆（倾角 52° 的投影）
n_pts = 300
theta_arr = np.linspace(0, 2*np.pi, n_pts)
orbit_x_arr = orbit_r * np.cos(theta_arr)
orbit_y_arr = orbit_r * np.sin(theta_arr) * np.cos(inclination)  # Z component projected
ax.plot(orbit_x_arr, orbit_y_arr, color=C_ORBIT, linewidth=2.0,
        linestyle='-', zorder=2, alpha=0.85)

# 升交点标记（赤道面与轨道面的交线）
# 在 theta=0 处：x = orbit_r, y = 0（升交点）
ax.plot(orbit_r, 0, 'o', markersize=3.5, color=C_ORBIT, zorder=8)
ax.text(orbit_r + 0.15, -0.35, 'Ascending\nnode', fontsize=7, ha='left',
        va='top', color=C_ORBIT, style='italic')

# 轨道面法线方向（从地球中心画出，沿 Z_L 方向）
# Z_L 方向 = h = [0, -sin(i), cos(i)] in ECI
h_z = np.cos(inclination)   # Z component
h_y = -np.sin(inclination)  # Y component (out of page)
# 投影到 2D (X-Z平面)：只有 Z 分量可见
h_proj_len = h_z * 1.8     # visible projection
h_x_start, h_y_start = 0, 0.3
ax.annotate('', xy=(0, h_proj_len), xytext=(h_x_start, h_y_start),
            arrowprops=dict(arrowstyle='->', color=C_ORBIT_NORMAL, lw=1.8,
                           shrinkA=0, shrinkB=0), zorder=10)
ax.text(0.22, h_proj_len + 0.15,
        r'$Z_{\mathrm{L}}$ normal to orbit plane',
        fontsize=9, ha='left', va='bottom', color=C_ORBIT_NORMAL)

# 轨道面标签
mid_idx = len(theta_arr) // 4
ox_mid = orbit_x_arr[mid_idx]
oy_mid = orbit_y_arr[mid_idx]
ax.text(ox_mid + 0.25, oy_mid - 0.25, 'Orbit',
        fontsize=8.5, ha='left', va='top', color=C_ORBIT, style='italic',
        rotation=-15)

# ============================================================
# 5. 目标卫星（我方）
# ============================================================
# 卫星主体
sat_body_w, sat_body_h = 0.14, 0.14
sat_rect = Polygon([
    (sat_x - sat_body_w/2, sat_y + sat_body_h/2),
    (sat_x + sat_body_w/2, sat_y + sat_body_h/2),
    (sat_x + sat_body_w/2, sat_y - sat_body_h/2),
    (sat_x - sat_body_w/2, sat_y - sat_body_h/2),
], facecolor=C_SAT_BODY, edgecolor='#111111', linewidth=1.5, zorder=15)
ax.add_patch(sat_rect)

# 太阳翼
panel_w, panel_h = 0.25, 0.08
for side in [-1, 1]:
    panel = Polygon([
        (sat_x + side * (sat_body_w/2 + panel_w), sat_y + panel_h/2),
        (sat_x + side * sat_body_w/2, sat_y + panel_h/2),
        (sat_x + side * sat_body_w/2, sat_y - panel_h/2),
        (sat_x + side * (sat_body_w/2 + panel_w), sat_y - panel_h/2),
    ], facecolor=C_SAT_PANEL, edgecolor='#1A5276', linewidth=0.8, zorder=14)
    ax.add_patch(panel)

# O_L 标注（标注在卫星的右下方，避开 Chaser C）
ax.annotate(r'$O_{\mathrm{L}}$', xy=(sat_x, sat_y), xytext=(sat_x + 0.50, sat_y - 0.95),
            fontsize=13, fontweight='bold', ha='center', va='top',
            arrowprops=dict(arrowstyle='->', color='gray', lw=1.2,
                           connectionstyle='arc3,rad=0.3'),
            zorder=25)

# "Own satellite" 标签（左上方避开坐标轴）
ax.text(sat_x - 0.90, sat_y + 1.00, 'Own satellite\n(target)',
        fontsize=9, ha='center', va='bottom', fontweight='bold', zorder=25,
        bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                  edgecolor='#888888', alpha=0.85))

# ============================================================
# 6. LVLH 坐标系（在目标卫星处）
# ============================================================
axis_len = 0.95

# 径向单位向量（从地心指向卫星）
radial_vec = np.array([sat_x, sat_y])
radial_unit = radial_vec / np.linalg.norm(radial_vec)

# X_L：径向方向
xl_tip = sat_x + radial_unit[0] * axis_len
xl_tip_y = sat_y + radial_unit[1] * axis_len
ax.annotate('', xy=(xl_tip, xl_tip_y), xytext=(sat_x, sat_y),
            arrowprops=dict(arrowstyle='->', color=C_XL, lw=2.5,
                           shrinkA=0, shrinkB=0), zorder=18)
ax.text(xl_tip + 0.35, xl_tip_y + 0.05,
        r'$X_{\mathrm{L}}$ (Radial)', fontsize=10, color=C_XL,
        ha='left', va='center', fontweight='bold')

# 切线方向（沿轨道，逆时针 = 正方向）
tangent = np.array([-orbit_r * np.sin(theta_sat),
                     orbit_r * np.cos(theta_sat) * np.cos(inclination)])
tangent_unit = tangent / np.linalg.norm(tangent)
yl_tip = sat_x + tangent_unit[0] * axis_len
yl_tip_y = sat_y + tangent_unit[1] * axis_len
ax.annotate('', xy=(yl_tip, yl_tip_y), xytext=(sat_x, sat_y),
            arrowprops=dict(arrowstyle='->', color=C_YL, lw=2.5,
                           shrinkA=0, shrinkB=0), zorder=18)
ax.text(yl_tip + 0.08, yl_tip_y + 0.2,
        r'$Y_{\mathrm{L}}$ (Along-track)', fontsize=10, color=C_YL,
        ha='left', va='bottom', fontweight='bold')

# Z_L：轨道面法线方向（垂直纸面向外，⊙ 符号）
# 轨道在 X-Z 平面内（极轨道），轨道面法线垂直于纸面
z_cx, z_cy = sat_x + 0.30, sat_y + 0.40
# 大圆（白色边框）
circle_dot = Circle((z_cx, z_cy), 0.18,
                     facecolor='white', edgecolor=C_ZL, linewidth=2.2, zorder=18)
ax.add_patch(circle_dot)
# 小圆点（表示出纸面）
ax.plot(z_cx, z_cy, 'o', markersize=4.5, markerfacecolor=C_ZL,
        markeredgecolor='none', zorder=19)
ax.text(z_cx + 0.30, z_cy + 0.02,
        r'$Z_{\mathrm{L}}$ (Orbit normal, out of page)',
        fontsize=10, color=C_ZL, ha='left', va='center', fontweight='bold')

# LVLH 标签
ax.text(sat_x + 1.6, sat_y - 0.55, r'$\mathcal{F}_{\mathrm{L}}$: LVLH',
        fontsize=9, ha='left', va='center', style='italic', color='gray')

# ============================================================
# 7. 来袭星群（Chaser spacecrafts）
# ============================================================
# 在目标卫星周围放置若干个机动追踪者
chaser_data = [
    {'r': 1.7, 'angle':  20, 'label': 'Chaser A', 'lbl_dx': 0.4, 'lbl_dy': -0.6},
    {'r': 1.5, 'angle': 110, 'label': 'Chaser B', 'lbl_dx': 0.6, 'lbl_dy': 0.2},
    {'r': 1.4, 'angle': 210, 'label': 'Chaser C', 'lbl_dx': -0.5, 'lbl_dy': -0.5},
    {'r': 1.6, 'angle': 310, 'label': 'Chaser D', 'lbl_dx': -0.5, 'lbl_dy': 0.5},
]

for idx, ch in enumerate(chaser_data):
    angle_rad = np.deg2rad(ch['angle'])
    cx = sat_x + ch['r'] * np.cos(angle_rad)
    cy = sat_y + ch['r'] * np.sin(angle_rad)

    # 从追踪者到目标的方向
    to_target = np.array([sat_x - cx, sat_y - cy])
    to_target_unit = to_target / np.linalg.norm(to_target)

    # 追踪者三角形（尖端朝向目标）
    tri_size = 0.14
    perp = np.array([-to_target_unit[1], to_target_unit[0]])
    tri = Polygon([
        (cx + to_target_unit[0] * tri_size,
         cy + to_target_unit[1] * tri_size),
        (cx - to_target_unit[0] * tri_size * 0.55 + perp[0] * tri_size * 0.8,
         cy - to_target_unit[1] * tri_size * 0.55 + perp[1] * tri_size * 0.8),
        (cx - to_target_unit[0] * tri_size * 0.55 - perp[0] * tri_size * 0.8,
         cy - to_target_unit[1] * tri_size * 0.55 - perp[1] * tri_size * 0.8),
    ], facecolor=C_CHASER[idx], edgecolor='#7B241C', linewidth=1.2, zorder=12)
    ax.add_patch(tri)

    # 机动轨迹虚线（弧形逼近）
    # 在 chaser 和目标之间画 2-3 段虚线
    n_seg = 3
    for s in range(n_seg):
        t0 = s / n_seg
        t1 = (s + 0.6) / n_seg
        # 在中点加入一定曲率偏移
        t_mid = (t0 + t1) / 2
        bend_factor = 0.15 * (1 if idx % 2 == 0 else -1)  # 交替弯曲方向
        bend_x = (cy - sat_y) * bend_factor * np.sin(np.pi * t_mid)
        bend_y = -(cx - sat_x) * bend_factor * np.sin(np.pi * t_mid)

        sx = cx + (sat_x - cx) * t0 + bend_x * (1 - abs(2*t_mid - 1))
        sy = cy + (sat_y - cy) * t0 + bend_y * (1 - abs(2*t_mid - 1))
        ex = cx + (sat_x - cx) * t1 + bend_x * (1 - abs(2*t_mid - 1))
        ey = cy + (sat_y - cy) * t1 + bend_y * (1 - abs(2*t_mid - 1))
        ax.plot([sx, ex], [sy, ey], color=C_APPROACH, linewidth=1.5,
                linestyle='--', alpha=0.8, zorder=6)

    # 箭头（最后一段末端加箭头）
    arr_x = cx + (sat_x - cx) * 0.92
    arr_y = cy + (sat_y - cy) * 0.92
    ax.plot(arr_x, arr_y, marker=(3, 0, np.degrees(np.arctan2(
            sat_y - cy, sat_x - cx)) - 90),
            markersize=10, color=C_APPROACH, alpha=0.8, zorder=7)

    # 标签（使用自定义偏移避免重叠）
    lx = cx + ch['lbl_dx']
    ly = cy + ch['lbl_dy']
    ax.text(lx, ly, ch['label'], fontsize=7.5, ha='center', va='center',
            color=C_CHASER[idx], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor='none', alpha=0.7))

# 通用 chaser 标签
ax.text(5.5, 3.2, 'Maneuvering\nchasers',
        fontsize=9, ha='center', va='center', color='#CB4335',
        fontweight='bold', style='italic',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor='#CB4335', alpha=0.75, linewidth=1.2))

# ============================================================
# 8. 标题
# ============================================================
ax.set_title('Coordinate frames', fontsize=14, fontweight='bold',
             pad=12, loc='center')

# 副标题/说明
fig.text(0.5, 0.015,
         'ECI frame $\\mathcal{F}_{\\mathrm{I}}$ and LVLH frame '
         '$\\mathcal{F}_{\\mathrm{L}}$ with maneuvering chaser spacecraft',
         ha='center', va='bottom', fontsize=9, style='italic', color='#555555')

# ============================================================
# 9. 保存 SVG 和 PDF
# ============================================================
plt.tight_layout(pad=0.5)

svg_path = 'figs/coordinate_frames.svg'
plt.savefig(svg_path, format='svg', bbox_inches='tight',
            pad_inches=0.3, transparent=False,
            facecolor='white', edgecolor='none')
print(f'[OK] SVG saved to: {svg_path}')

pdf_path = 'figs/coordinate_frames.pdf'
plt.savefig(pdf_path, format='pdf', bbox_inches='tight',
            pad_inches=0.3, transparent=False,
            facecolor='white', edgecolor='none')
print(f'[OK] PDF saved to: {pdf_path}')

png_path = 'figs/coordinate_frames_preview.png'
plt.savefig(png_path, format='png', dpi=200, bbox_inches='tight',
            pad_inches=0.3, transparent=False,
            facecolor='white', edgecolor='none')
print(f'[OK] PNG saved to: {png_path}')

plt.close()
