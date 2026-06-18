import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------- style ----------
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 7.5,
    'axes.linewidth': 0.5,
})

# Single-column width ~3.35 in. Keep figure compact.
FIG_W = 3.35
FIG_H = 3.2
DPI = 300

# colors
C_INPUT  = '#E8F5E9'
C_MODEL  = '#E3F2FD'
C_PHYS   = '#FFF3E0'
C_OUTPUT = '#FCE4EC'
C_COND   = '#F3E5F5'
C_EDGE   = '#333333'

def rbox(ax, xy, w, h, text, sub=None, color=C_MODEL, lw=1.0, fs=7.5, sfs=6.5):
    box = mpatches.FancyBboxPatch(xy, w, h,
                                  boxstyle="round,pad=0.06",
                                  facecolor=color, edgecolor=C_EDGE, lw=lw, zorder=3)
    ax.add_patch(box)
    cx, cy = xy[0] + w/2, xy[1] + h/2
    dy = 1.5 if sub else 0
    ax.text(cx, cy + dy, text, fontsize=fs, ha='center', va='center',
            fontweight='bold', color='#111111', zorder=4)
    if sub:
        ax.text(cx, cy - dy - 3, sub, fontsize=sfs, ha='center', va='top',
                color='#444444', zorder=4)

def arrow(ax, x1, y1, x2, y2, lw=1.0, color='#555555'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=lw, color=color,
                                connectionstyle='arc3,rad=0'), zorder=2)

def arrow_c(ax, x1, y1, x2, y2, lw=0.8, color='#888888', rad=0.15):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=lw, color=color,
                                connectionstyle=f'arc3,rad={rad}'), zorder=2)

# ---------- figure ----------
fig, ax = plt.subplots(1, 1, figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis('off')

# Layout
CX = FIG_W / 2
BW = 2.0          # block width
BH = 0.35         # block height
SBW = 1.4         # side block width
SBH = 0.30        # side block height

# Y positions (inches from bottom)
Y = {
    'in':    0.15,
    'dv':    0.65,
    'ext':   1.15,
    'enc':   1.65,
    'dec':   2.15,
    'out':   2.65,
    'cond':  1.15,   # same level as ext
    'phys':  0.15,   # bottom-right
}

# ---- labels ----
def lbl(ax, x, y, text):
    ax.text(x, y, text, fontsize=6, ha='right', va='center', color='#666666',
            fontweight='bold', zorder=5)

# 1) Input
rbox(ax, (CX-BW/2, Y['in']), BW, BH, 'Input Sequence',
     '10 steps, 6-dim (pos+vel)', C_INPUT)
lbl(ax, CX-BW/2-0.06, Y['in']+BH/2, '1')

# 2) Delta-v Estimator
rbox(ax, (CX-BW/2, Y['dv']), BW, BH, 'Δv Estimator',
     'Differentiable CW inverse', C_MODEL)
lbl(ax, CX-BW/2-0.06, Y['dv']+BH/2, '2')

# 3) Condition Builder (right side)
cond_x = CX + BW/2 + 0.15
rbox(ax, (cond_x, Y['cond']), SBW, SBH, 'Condition Builder',
     'Mode embed + Δv MLP\n  -> 8-dim vector', C_COND, fs=7, sfs=6)
lbl(ax, cond_x+SBW+0.06, Y['cond']+SBH/2, '3')

# 4) Extended Input
rbox(ax, (CX-BW/2, Y['ext']), BW, BH, 'Extended Input',
     'State (6-dim) + Cond (8-dim)', C_MODEL)
lbl(ax, CX-BW/2-0.06, Y['ext']+BH/2, '4')

# 5) Encoder
rbox(ax, (CX-BW/2, Y['enc']), BW, BH, 'LSTM Encoder',
     '3-layer, hidden=256', C_MODEL)
lbl(ax, CX-BW/2-0.06, Y['enc']+BH/2, '5')

# 6) Decoder
rbox(ax, (CX-BW/2, Y['dec']), BW, BH, 'LSTM Decoder',
     '3-layer, autoregressive\ndelta prediction', C_MODEL)
lbl(ax, CX-BW/2-0.06, Y['dec']+BH/2, '6')

# 7) Output
rbox(ax, (CX-BW/2, Y['out']), BW, BH, 'Predicted Trajectory',
     '10 steps, 6-dim residual Δ', C_OUTPUT)
lbl(ax, CX-BW/2-0.06, Y['out']+BH/2, '7')

# 8) Physics Loss (right side, bottom)
phys_x = cond_x
rbox(ax, (phys_x, Y['phys']), SBW, SBH+0.05, 'Physics Loss',
     'CW free residual\n+ Δv penalty + smooth', C_PHYS, fs=7, sfs=6)
lbl(ax, phys_x+SBW+0.06, Y['phys']+(SBH+0.05)/2, '8')

# ---- arrows ----
dy = BH  # vertical distance between block centers
arrow(ax, CX, Y['in']+BH, CX, Y['dv'])             # 1->2
arrow(ax, CX, Y['dv']+BH, CX, Y['ext'])            # 2->4
arrow_c(ax, CX+BW*0.3, Y['dv']+BH*0.3,
         cond_x+SBW/2, Y['cond']+SBH, rad=0.2)    # 2->3
arrow_c(ax, cond_x+SBW/2, Y['cond'],
         CX+BW*0.3, Y['ext']+BH*0.7, rad=0.2)     # 3->4
arrow(ax, CX, Y['ext']+BH, CX, Y['enc'])           # 4->5
arrow(ax, CX, Y['enc']+BH, CX, Y['dec'])           # 5->6
arrow(ax, CX, Y['dec']+BH, CX, Y['out'])           # 6->7
# Physics loss arrow (dashed, from output to physics)
ax.annotate('', xy=(phys_x+SBW/2, Y['phys']), xytext=(CX+BW*0.3, Y['out']+BH*0.3),
            arrowprops=dict(arrowstyle='->', lw=0.8, color='#CC5555',
                            connectionstyle='arc3,rad=0', linestyle='dashed'),
            zorder=2)

# ---- legend ----
ax.plot([0.10, 0.28], [0.02, 0.02], color='#555555', lw=1.0, transform=ax.transData)
ax.text(0.30, 0.02, 'Data flow', fontsize=5.5, ha='left', va='center', color='#555555',
        transform=ax.transData)
ax.plot([0.55, 0.73], [0.02, 0.02], color='#CC5555', lw=0.8, dashes=(3,2), transform=ax.transData)
ax.text(0.75, 0.02, 'Physics loss', fontsize=5.5, ha='left', va='center', color='#CC5555',
        transform=ax.transData)

plt.savefig('D:/Office/2026.1/意图识别论文/Manuscript/figs/fig1_pilstm.pdf',
            dpi=DPI, facecolor='white', edgecolor='none')
plt.savefig('D:/Office/2026.1/意图识别论文/Manuscript/figs/fig1_preview.png',
            dpi=150, facecolor='white', edgecolor='none')
plt.close()
print("Figure 1 saved OK")
