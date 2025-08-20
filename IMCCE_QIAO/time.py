import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Data for A (N, S, U)
A_N = [[1847, 1852], [1856, 1857], [1863, 1864], [1866, 1868], [1873, 1877], [1883, 1889], [1892, 1923], [1928, 1929], [1939, 1942], [1949, 2019]]
A_S = [[1966, 1980], [1981, 1987], [1990, 1991], [1994, 1996], [1998, 1999], [2004, 2016], [2014, 2019]]
A_U = [[1847, 1849], [1851, 1852], [1863, 1865], [1870, 1882], [1887, 1892], [1901, 1914], [1920, 1922], [1940, 1948], [1966, 1977], [1981, 1985], [1992, 1997], [2007, 2016]]

# Data for B (N, S, U)
B_N = [[1996, 2019]]
B_S = [[1987, 1988], [2003, 2014]]
B_U = [[1990], [1998, 2020]]

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

B_N_dates = convert_to_dates(B_N)
B_S_dates = convert_to_dates(B_S)
B_U_dates = convert_to_dates(B_U)

# Create the plot with three separate subplots
fig, ax = plt.subplots(3, 1, figsize=(10, 6))

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
ax[0].set_yticklabels(['Total Time', 'Our Work'])
ax[0].set_ylim(0, 1)

# Plot for S
for start, end in A_S_dates:
    ax[1].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
for start, end in B_S_dates:
    ax[1].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
ax[1].set_xlabel('Saturn')
ax[1].set_yticks([y_total_time, y_our_work])
ax[1].set_yticklabels(['Total Time', 'Our Work'])
ax[1].set_ylim(0, 1)

# Plot for U
for start, end in A_U_dates:
    ax[2].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
for start, end in B_U_dates:
    ax[2].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
ax[2].set_xlabel('Uranus')
ax[2].set_yticks([y_total_time, y_our_work])
ax[2].set_yticklabels(['Total Time', 'Our Work'])
ax[2].set_ylim(0, 1)

# Set the x-axis format for each plot
for i in range(3):
    ax[i].xaxis.set_major_locator(mdates.YearLocator(10))
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax[i].xaxis.set_tick_params(rotation=45)

# Add global title
fig.suptitle('QIAO Observational vs Total Observational', fontsize=16)

# Adjust layout to make sure everything fits
plt.tight_layout(rect=[0, 0, 1, 0.95])

plt.savefig('time.png', dpi=300)



# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from datetime import datetime

# # Data for A (N, S, U)
# A_N = [[1847, 1852], [1856, 1857], [1863, 1864], [1866, 1868], [1873, 1877], [1883, 1889], [1892, 1923], [1928, 1929], [1939, 1942], [1949, 2019]]
# A_S = [[1966, 1980], [1981, 1987], [1990, 1991], [1994, 1996], [1998, 1999], [2004, 2016], [2014, 2019]]
# A_U = [[1847, 1849], [1851, 1852], [1863, 1865], [1870, 1882], [1887, 1892], [1901, 1914], [1920, 1922], [1940, 1948], [1966, 1977], [1981, 1985], [1992, 1997], [2007, 2016]]

# # Data for B (N, S, U)
# B_N = [[1996, 2019]]
# B_S = [[1987, 1988], [2003, 2014]]
# B_U = [[1990], [1998, 2020]]

# # New data for Jupiter
# A_J = [[1847, 1852], [1856, 1857], [1863, 1864], [1866, 1868], [1873, 1877], [1883, 1889], [1892, 1923], [1928, 1929], [1939, 1942], [1949, 2019]]
# A_J = [[1891, 1892], [1901, 1902], [1905, 1906], [1951, 1952], [1962, 1963], [1967, 1968], [1969, 1970], [1973, 1974], [1976, 1981], [1983, 1986], [1989, 2007], [2009, 2019], [2020, 2021]]
# B_J = [[1987,1988],[2016,2018]]

# # Convert the data to datetime objects, handling both single and double year lists
# def convert_to_dates(data):
#     converted_data = []
#     for item in data:
#         if len(item) == 1:
#             year = item[0]
#             converted_data.append((datetime(year=year, month=1, day=1), datetime(year=year, month=1, day=1)))
#         elif len(item) == 2:
#             start, end = item
#             converted_data.append((datetime(year=start, month=1, day=1), datetime(year=end, month=1, day=1)))
#     return converted_data

# A_N_dates = convert_to_dates(A_N)
# A_S_dates = convert_to_dates(A_S)
# A_U_dates = convert_to_dates(A_U)
# A_J_dates = convert_to_dates(A_J)

# B_N_dates = convert_to_dates(B_N)
# B_S_dates = convert_to_dates(B_S)
# B_U_dates = convert_to_dates(B_U)
# B_J_dates = convert_to_dates(B_J)

# # Create the plot with four separate subplots
# fig, ax = plt.subplots(4, 1, figsize=(10, 8))

# # Define y-positions for the two data types
# y_total_time = 0.4
# y_our_work = 0.6

# # Plot for N
# for start, end in A_N_dates:
#     ax[0].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
# for start, end in B_N_dates:
#     ax[0].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
# ax[0].set_xlabel('Neptune')
# ax[0].set_yticks([y_total_time, y_our_work])
# ax[0].set_yticklabels(['Total Time', 'QIAO'])
# ax[0].set_ylim(0, 1)

# # Plot for S
# for start, end in A_S_dates:
#     ax[1].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
# for start, end in B_S_dates:
#     ax[1].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
# ax[1].set_xlabel('Saturn')
# ax[1].set_yticks([y_total_time, y_our_work])
# ax[1].set_yticklabels(['Total Time', 'QIAO'])
# ax[1].set_ylim(0, 1)

# # Plot for U
# for start, end in A_U_dates:
#     ax[2].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
# for start, end in B_U_dates:
#     ax[2].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
# ax[2].set_xlabel('Uranus')
# ax[2].set_yticks([y_total_time, y_our_work])
# ax[2].set_yticklabels(['Total Time', 'QIAO'])
# ax[2].set_ylim(0, 1)

# # Plot for J
# for start, end in A_J_dates:
#     ax[3].plot([start, end], [y_total_time, y_total_time], color='lightgray', lw=10)
# for start, end in B_J_dates:
#     ax[3].plot([start, end], [y_our_work, y_our_work], color='blue', lw=10)
# ax[3].set_xlabel('Jupiter')
# ax[3].set_yticks([y_total_time, y_our_work])
# ax[3].set_yticklabels(['Total Time', 'QIAO'])
# ax[3].set_ylim(0, 1)

# # Set the x-axis format for each plot
# for i in range(4):
#     ax[i].xaxis.set_major_locator(mdates.YearLocator(10))
#     ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
#     ax[i].xaxis.set_tick_params(rotation=0)

# # Add global title
# fig.suptitle('QIAO Observational vs Total Observational', fontsize=16)

# # Adjust layout to make sure everything fits
# plt.tight_layout(rect=[0, 0, 1, 0.95])

# plt.savefig('time.png', dpi=300)
# plt.savefig('time.png', dpi=300)