



import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

A_N = [[1847, 1852], [1856, 1856], [1863, 1863], [1866, 1868], [1873, 1877], [1883, 1889], [1892, 1923], [1928, 1928], [1939, 1942], [1949, 2021]]
A_S = [[1874, 2023]]
A_U = [[1787, 1832], [1837, 1837], [1847, 1892], [1894, 1927], [1947, 2020]]
A_J = [[1906, 1907], [1914, 1914], [1951, 1952], [1967, 1969], [1973, 1973], [1975, 1976], [1980, 1981], [1986, 2022]]

# B组数据 (N, S, U)
B_N = [[1996, 2009], [2010, 2019]]
B_S = [[1987, 1988], [2003, 2014]]
B_U = [[1990], [1998, 2007], [2008, 2014]]
B_J = [[2016, 2018]]

# Convert the data to datetime objects, handling both single and double year lists
def convert_to_dates(data):
    converted_data = []
    for item in data:
        if len(item) == 1:
            year = item[0]
            converted_data.append((datetime(year=year, month=1, day=1), datetime(year=year, month=1, day=1)))
        elif len(item) == 2:
            start, end = item
            converted_data.append((datetime(year=start, month=1, day=1), datetime(year=end, month=1, day=1)))
    return converted_data

A_N_dates = convert_to_dates(A_N)
A_S_dates = convert_to_dates(A_S)
A_U_dates = convert_to_dates(A_U)
A_J_dates = convert_to_dates(A_J)

B_N_dates = convert_to_dates(B_N)
B_S_dates = convert_to_dates(B_S)
B_U_dates = convert_to_dates(B_U)
B_J_dates = convert_to_dates(B_J)

# Create the plot with four separate subplots
fig, ax = plt.subplots(4, 1, figsize=(10, 8))

# Define y-positions for the two data types
y_total_time = 0.4
y_our_work = 0.6

# Plot for N
for start, end in A_N_dates:
    ax[0].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
for start, end in B_N_dates:
    ax[0].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
ax[0].set_xlabel('Neptune')
ax[0].set_yticks([y_total_time, y_our_work])
ax[0].set_yticklabels(['Other', 'QIAO'])
ax[0].set_ylim(0, 1)

# Plot for S
for start, end in A_S_dates:
    ax[1].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
for start, end in B_S_dates:
    ax[1].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
ax[1].set_xlabel('Saturn')
ax[1].set_yticks([y_total_time, y_our_work])
ax[1].set_yticklabels(['Total Time', 'QIAO'])
ax[1].set_ylim(0, 1)

# Plot for U
for start, end in A_U_dates:
    ax[2].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
for start, end in B_U_dates:
    ax[2].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
ax[2].set_xlabel('Uranus')
ax[2].set_yticks([y_total_time, y_our_work])
ax[2].set_yticklabels(['Total Time', 'QIAO'])
ax[2].set_ylim(0, 1)

# Plot for J
for start, end in A_J_dates:
    ax[3].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
for start, end in B_J_dates:
    ax[3].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
ax[3].set_xlabel('Jupiter')
ax[3].set_yticks([y_total_time, y_our_work])
ax[3].set_yticklabels(['Total Time', 'QIAO'])
ax[3].set_ylim(0, 1)

# Set the x-axis format for each plot
for i in range(4):
    ax[i].xaxis.set_major_locator(mdates.YearLocator(10))
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax[i].xaxis.set_tick_params(rotation=0)

# Add global title
fig.suptitle('QIAO Observational vs Total Observational', fontsize=16)

# Adjust layout to make sure everything fits
plt.tight_layout(rect=[0, 0, 1, 0.95])

plt.savefig('time.png', dpi=300)
plt.show()