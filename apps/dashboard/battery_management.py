import numpy as np
from datetime import datetime, timezone

# Battery percentage levels and corresponding total time in minutes
battery_percentages = np.array([100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 
                                45, 40, 35, 30, 25, 20, 15, 10, 5, 0])
total_time_minutes = np.array([0, 11, 23, 36, 47, 55, 64, 74, 82, 91, 99, 
                               107, 114, 120, 126, 132, 138, 155, 171, 181, 193])

# Quadratic model coefficients
d, e, f = np.polyfit(battery_percentages, total_time_minutes[::-1], 2)

def estimate_remaining_time(battery_percentage):
    """Estimate the remaining battery time based on percentage."""
    return max(0, d * battery_percentage**2 + e * battery_percentage + f)

# Battery tracking variables
battery_percentage = 100  # Start at full charge
index = 0  # Index for battery percentage updates
remaining_time = estimate_remaining_time(battery_percentage)
time_intervals = np.diff(total_time_minutes) * 60  # Convert to seconds

def update_battery(battery_time_start):
    """Update battery percentage."""
    global battery_percentage, index, remaining_time
    now = datetime.now(timezone.utc)

    # Calculate diff in minutes between now and battery start time, 
    # then use delta to determine what index we should be at
def get_index(now, time_intervals):
    for i in range(len(time_intervals) - 1):
        if time_intervals[i] <= now < time_intervals[i + 1]:
            return i
    return len(time_intervals) - 1 #Returns last index if needed

#index = get_index(datetime.now(timezone.utc), time_intervals)


if index < len(time_intervals):
        battery_percentage = battery_percentages[index]  # Update battery percentage
        remaining_time = estimate_remaining_time(battery_percentage)  # Update estimated time
        index += 1
        
        print(f"Battery updated: {battery_percentage}%, Estimated Time: {remaining_time // 60}h {remaining_time % 60}m", f"Index: {index}")
        #return battery_percentage, remaining_time / 60