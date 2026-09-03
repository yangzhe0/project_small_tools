import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bisect import bisect_left

# ---------------------------------------------------------
# 1. Scientific Publication Style
# ---------------------------------------------------------
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13.5,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10.5,
    'legend.fontsize': 10.5,
    'lines.linewidth': 2.8,
    'figure.dpi': 300
})

# ---------------------------------------------------------
# 2. Data Loading & Preprocessing
# ---------------------------------------------------------
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'IAU_number.csv')
data = pd.read_csv(file_path)

# Extract only the 4 giant planets of interest
planets_of_interest = ['Saturn', 'Jupiter', 'Uranus', 'Neptune']
filtered_data = data[data['Satellite'].isin(planets_of_interest)].copy()

# Ensure Year is numeric
filtered_data['Year discovered'] = pd.to_numeric(filtered_data['Year discovered'], errors='coerce')
filtered_data = filtered_data.dropna(subset=['Year discovered'])
filtered_data['Year discovered'] = filtered_data['Year discovered'].astype(int)

# Group by Year and Satellite
annual_counts = filtered_data.groupby(['Year discovered', 'Satellite']).size().unstack(fill_value=0)

# Custom Non-linear Timeline Ticks (Compress early centuries, expand modern boom)
custom_ticks = [1610, 1670, 1750, 1800, 1850, 1900, 1950, 1970, 1980, 1990, 2000, 2010, 2020, 2026]

# Create complete year index
full_years = sorted(list(set(annual_counts.index.tolist() + custom_ticks)))
full_index = pd.Index(full_years, name='Year discovered')
complete_data = annual_counts.reindex(full_index).fillna(0)
cumulative_counts = complete_data.cumsum()

# ---------------------------------------------------------
# 3. Canvas Setup (Equal Height = 8.0 in, Ratio 1:1.2 -> Width = 6.67 in)
# ---------------------------------------------------------
fig_h = 8.0
fig_w = 6.67  # 6.67 : 8.0 = 1 : 1.2
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)

fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#fafbfc')

# Planet color mapping
colors = {
    'Saturn': '#D97706',   # Warm Amber / Gold
    'Jupiter': '#DC2626',  # Deep Crimson / Vermilion
    'Uranus': '#0284C7',   # Cyan Sky Blue
    'Neptune': '#4F46E5'   # Royal Indigo
}

# Coordinate mapping for non-linear x-axis
def get_tick_positions(years, ticks):
    positions = []
    for y in years:
        idx = bisect_left(ticks, y)
        if idx == 0:
            positions.append(0.0)
        elif idx >= len(ticks):
            positions.append(float(len(ticks) - 1))
        else:
            t0, t1 = ticks[idx - 1], ticks[idx]
            frac = (y - t0) / (t1 - t0)
            positions.append(idx - 1 + frac)
    return positions

x_values = get_tick_positions(cumulative_counts.index, custom_ticks)

# ---------------------------------------------------------
# 4. Plot Cumulative Curves & End-Value Annotations
# ---------------------------------------------------------
for planet in planets_of_interest:
    if planet in cumulative_counts.columns:
        ax.plot(
            x_values,
            cumulative_counts[planet],
            color=colors[planet],
            label=planet,
            alpha=0.95,
            zorder=3
        )
        
        # End value annotation
        last_val = int(cumulative_counts[planet].iloc[-1])
        last_x = x_values[-1]
        
        # Slight vertical adjustment for close values
        y_offset = 0
        if planet == 'Uranus':
            y_offset = 3.5
        elif planet == 'Neptune':
            y_offset = -3.5
            
        ax.annotate(
            f"{last_val}",
            xy=(last_x, last_val),
            xytext=(7, y_offset),
            textcoords="offset points",
            color=colors[planet],
            fontsize=11.5,
            fontweight='bold',
            va='center',
            zorder=5
        )

# ---------------------------------------------------------
# 5. Axis, Grid & Boundaries
# ---------------------------------------------------------
ax.set_xticks(range(len(custom_ticks)))
ax.set_xticklabels(custom_ticks, rotation=45, ha='right', fontsize=9.5, color='#334155')
ax.set_xlim(-0.3, len(custom_ticks) - 1 + 1.2)  # Extra room on right for numbers
ax.set_ylim(-8, 315)

ax.grid(True, which="major", axis="both", linestyle="--", alpha=0.55, color='#CBD5E1', zorder=0)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#94A3B8')
ax.spines['bottom'].set_color('#94A3B8')

ax.set_xlabel('Discovery Year', fontsize=11.5, fontweight='bold', labelpad=8, color='#0F172A')
ax.set_ylabel('Cumulative Number of Satellites', fontsize=11.5, fontweight='bold', labelpad=8, color='#0F172A')

# ---------------------------------------------------------
# 6. Legend & "Data as of Date" Badge
# ---------------------------------------------------------
legend = ax.legend(
    title="Planets",
    title_fontsize=10.5,
    loc='upper left',
    frameon=True,
    facecolor='#ffffff',
    edgecolor='#CBD5E1',
    framealpha=0.95,
    borderpad=0.7
)
legend.get_frame().set_boxstyle('round,pad=0.35,rounding_size=0.25')

# "Data as of Date" Badge placed cleanly in top-left below the legend
ax.text(
    0.035, 0.64,
    "Data as of August 2026",
    transform=ax.transAxes,
    ha='left',
    va='top',
    fontsize=9.2,
    fontweight='bold',
    color='#334155',
    bbox=dict(
        boxstyle='round,pad=0.3,rounding_size=0.25',
        facecolor='#F1F5F9',
        edgecolor='#CBD5E1',
        alpha=0.95,
        lw=0.8
    ),
    zorder=6
)

# Title
plt.title(
    "Cumulative Discoveries of Natural Satellites\nGiant Planets in the Solar System",
    fontsize=14.5,
    fontweight='bold',
    pad=20,
    color='#0F172A',
    linespacing=1.3
)

# ---------------------------------------------------------
# 7. Bottom Data Source Footnote (Bold & Prominent)
# ---------------------------------------------------------
fig.text(
    0.98, 0.012,
    "Data Source: NASA/JPL Solar System Dynamics & IAU WGPSN",
    ha='right',
    va='bottom',
    fontsize=10.5,
    fontweight='bold',
    color='#1E293B'
)

plt.tight_layout(rect=[0, 0.05, 1, 0.98])

# ---------------------------------------------------------
# 8. Save Output Figure (Standardized Height for PPT: 2350px)
# ---------------------------------------------------------
output_file = os.path.join(script_dir, 'satellite_discovery_counts_narrow.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')

# Exact Height Normalization for PPT side-by-side layout
from PIL import Image
target_h = 2350
img = Image.open(output_file)
if img.size[1] != target_h:
    new_img = Image.new('RGB', (img.size[0], target_h), (255, 255, 255))
    offset_y = (target_h - img.size[1]) // 2
    new_img.paste(img, (0, offset_y))
    new_img.save(output_file)

print(f"Successfully saved {output_file} (Size: {Image.open(output_file).size[0]} x {target_h} px, Ratio ~ 1:1.2)")
