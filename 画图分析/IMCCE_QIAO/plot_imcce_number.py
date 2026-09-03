import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# Data Definition
# ---------------------------------------------------------
categories = ['J6-J13', 'S1-S8', 'S9', 'U1-5', 'N1', 'N2']
categories_desc = [
    'J6–J13\n(Jupiter)',
    'S1–S8\n(Saturn)',
    'S9 (Phoebe)\n(Saturn)',
    'U1–5\n(Uranus)',
    'N1 (Triton)\n(Neptune)',
    'N2 (Nereid)\n(Neptune)'
]

qiao_data = [639, 3261, 1288, 14636, 7116, 402]          # Qiao R.C's team data
total_data = [22662, 120949, 9188, 56580, 20656, 3252]   # Total data in IMCCE
qiao_percentages = [q / t * 100 for q, t in zip(qiao_data, total_data)]

# ---------------------------------------------------------
# Figure Configuration (Standardized Height for PPT Alignment)
# ---------------------------------------------------------
fig_h = 8.0
fig_w = 11.5
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#fafbfc')

# Symmetrical Log scale (linear 0-30k, log2 >30k)
ax.set_yscale("symlog", linthresh=30000, base=2)
ax.set_ylim(0, 175000)

x = np.arange(len(categories))
width = 0.28   # Refined width for optimal separation
bar_gap = 0.07 # Distinct gap between the two bars in each group

x_qiao = x - (width / 2 + bar_gap / 2)
x_total = x + (width / 2 + bar_gap / 2)

# ---------------------------------------------------------
# Bar Plots
# ---------------------------------------------------------
# 1. Total Data in IMCCE
rects_total = ax.bar(
    x_total,
    total_data,
    width,
    label='Total Data in IMCCE',
    color='#E2E8F0',
    edgecolor='#94A3B8',
    linewidth=1.1,
    alpha=0.9,
    zorder=2
)

# 2. Qiao R.C's team Data
rects_qiao = ax.bar(
    x_qiao,
    qiao_data,
    width,
    label="Qiao R.C's team",
    color='#0284C7',
    edgecolor='#0369A1',
    linewidth=1.1,
    zorder=3
)

# ---------------------------------------------------------
# Text Annotations (Well-spaced & Distinct)
# ---------------------------------------------------------
# Annotate Qiao R.C's team
for rect, percent, q_val in zip(rects_qiao, qiao_percentages, qiao_data):
    height = rect.get_height()
    pct_str = f"{percent:.1f}%"
    
    ax.annotate(
        f"{q_val:,}\n({pct_str})",
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 6),
        textcoords="offset points",
        ha='center',
        va='bottom',
        fontsize=9.0,
        fontweight='bold',
        color='#0369A1',
        linespacing=1.2,
        bbox=dict(
            boxstyle='round,pad=0.22,rounding_size=0.2',
            facecolor='#F0F9FF',
            edgecolor='#BAE6FD',
            alpha=0.95,
            lw=0.8
        ),
        zorder=5
    )

# Annotate Total Data in IMCCE
for rect, t_val in zip(rects_total, total_data):
    height = rect.get_height()
    ax.annotate(
        f"{t_val:,}",
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 6),
        textcoords="offset points",
        ha='center',
        va='bottom',
        fontsize=9.0,
        fontweight='bold',
        color='#475569',
        bbox=dict(
            boxstyle='round,pad=0.2,rounding_size=0.2',
            facecolor='#F8FAFC',
            edgecolor='#CBD5E1',
            alpha=0.9,
            lw=0.7
        ),
        zorder=5
    )

# ---------------------------------------------------------
# Ticks, Labels, and Grid
# ---------------------------------------------------------
ax.set_xticks(x)
ax.set_xticklabels(categories_desc, fontsize=10.5, fontweight='bold', color='#1E293B')
ax.set_xlabel('Natural Satellite Categories of Giant Planets', fontsize=12, fontweight='bold', labelpad=12, color='#0F172A')
ax.set_ylabel('Number of Observations', fontsize=12, fontweight='bold', labelpad=10, color='#0F172A')

# Custom informative Y-axis ticks
yticks = [0, 10000, 20000, 30000, 65536, 131072]
yticklabels = ['0', '10,000', '20,000', '30,000', '65,536\n($2^{16}$)', '131,072\n($2^{17}$)']
ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels, fontsize=9.5, color='#334155')

ax.grid(True, which="both", axis="y", linestyle="--", alpha=0.55, color='#CBD5E1', zorder=0)

# Spine formatting
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#94A3B8')
ax.spines['bottom'].set_color('#94A3B8')

# Legend
legend = ax.legend(
    loc='upper right',
    frameon=True,
    facecolor='#ffffff',
    edgecolor='#CBD5E1',
    fontsize=10.5,
    borderpad=0.8
)
legend.get_frame().set_boxstyle('round,pad=0.4,rounding_size=0.2')

# Titles
plt.title(
    "Astrometric Observations Recorded in IMCCE Database\nQiao R.C's team vs. Total Observational Data",
    fontsize=14.5,
    fontweight='bold',
    pad=20,
    color='#0F172A',
    linespacing=1.3
)

# Footer / Attribution
plt.figtext(
    0.98, 0.012,
    "Data Source: IMCCE Database (Institut de mécanique céleste et de calcul des éphémérides / NSDC)",
    ha='right',
    va='bottom',
    fontsize=10.5,
    fontweight='bold',
    color='#1E293B'
)

# ---------------------------------------------------------
# Save Figure (Standardized Height for PPT: 2350px)
# ---------------------------------------------------------
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
plt.tight_layout(rect=[0, 0.05, 1, 0.98])
output_path = os.path.join(script_dir, "number.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

# Exact Height Normalization for PPT side-by-side layout
from PIL import Image
target_h = 2350
img = Image.open(output_path)
if img.size[1] != target_h:
    new_img = Image.new('RGB', (img.size[0], target_h), (255, 255, 255))
    offset_y = (target_h - img.size[1]) // 2
    new_img.paste(img, (0, offset_y))
    new_img.save(output_path)

print(f"Successfully generated {output_path} (Size: {Image.open(output_path).size[0]} x {target_h} px)")
