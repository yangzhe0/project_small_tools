import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from bisect import bisect_left
# Set the style for scientific publication
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 20,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'figure.figsize': (10, 7.5), # 4:3 aspect ratio
    'axes.grid': True,
    'grid.alpha': 0.5,
    'grid.linestyle': '--',
    'lines.linewidth': 3
})

file_path = 'IAU_number.csv'
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    exit(1)

# Data Preprocessing
planets_of_interest = ['Jupiter', 'Saturn', 'Uranus', 'Neptune']
filtered_data = data[data['Satellite'].isin(planets_of_interest)]

# Count satellites by year
annual_counts = filtered_data.groupby(['Year discovered', 'Satellite']).size().unstack(fill_value=0)

# Custom ticks for the x-axis (Non-linear time scale)
custom_ticks = [1610, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 1970, 1980, 1990, 2000, 2010, 2020, 2024]

# Create full time index
full_years = sorted(list(set(annual_counts.index.tolist() + custom_ticks)))
full_index = pd.Index(full_years, name='Year discovered')

# Reindex and calculate cumulative sum
complete_data = annual_counts.reindex(full_index).fillna(0)
cumulative_counts = complete_data.cumsum()

# Visualization Setup
fig, ax = plt.subplots()
colors = {'Jupiter': '#BC763C', 'Saturn': '#E3BA58', 
          'Uranus': '#82B9C8', 'Neptune': '#5376E0'} 

# Mapping function for non-linear x-axis
def get_tick_positions(years, custom_ticks):
    positions = []
    for year in years:
        idx = bisect_left(custom_ticks, year)
        if idx == 0:
            positions.append(0)
        elif idx >= len(custom_ticks):
            positions.append(len(custom_ticks) - 1)
        else:
            # Linear interpolation between custom_ticks[idx-1] and custom_ticks[idx]
            t0 = custom_ticks[idx-1]
            t1 = custom_ticks[idx]
            fraction = (year - t0) / (t1 - t0)
            positions.append(idx - 1 + fraction)
    return positions

# Generate x-values for plotting
x_values = get_tick_positions(cumulative_counts.index, custom_ticks)

# Plotting
for planet in planets_of_interest:
    if planet in cumulative_counts.columns:
        ax.plot(x_values, cumulative_counts[planet], 
                 color=colors.get(planet, 'gray'), label=planet, alpha=0.9)
        
        # Add final value annotation
        last_value = cumulative_counts[planet].iloc[-1]
        ax.text(x_values[-1] + 0.1, last_value, f'{int(last_value)}',
                 color=colors.get(planet, 'gray'), fontsize=14, fontweight='bold', va='center')

# Axis Setup
ax.set_xticks(range(len(custom_ticks)))
ax.set_xticklabels(custom_ticks, rotation=45)
ax.set_xlim(0, len(custom_ticks) - 1 + 0.8) # Add more space for labels

# Labels and Title
ax.set_title('Cumulative Number of Observed Natural Satellites', pad=20, fontweight='bold')
ax.set_xlabel('Year', labelpad=10)
ax.set_ylabel('Number of Satellites', labelpad=10)
# ax.set_yscale('log')
# ax.set_yticks([1, 10, 100, 500])
# ax.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

# Legend
ax.legend(title="Planets", loc='upper left', frameon=True, framealpha=0.9, edgecolor='gray')

# Layout
plt.tight_layout()

# Save
output_file = 'satellite_discovery_counts.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Chart saved to {output_file}")
