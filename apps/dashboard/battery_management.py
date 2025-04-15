import numpy as np
from datetime import datetime, timezone
import requests
from django.http import JsonResponse

# Battery levels and corresponding total time in minutes
battery_percentages = np.array([100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 
                                45, 40, 35, 30, 25, 20, 15, 10, 5, 0])
total_time_minutes = np.array([0, 1, 24, 36, 45, 55, 63, 70, 80, 90, 99, 
                               107, 114, 120, 126, 132, 138, 155, 171, 181, 193])

# Fit a quadratic model to reverse time values for better curve behavior
d, e, f = np.polyfit(battery_percentages, total_time_minutes[::-1], 2)

def estimate_remaining_time(battery_percentage):
    return max(0, d * battery_percentage**2 + e * battery_percentage + f)

# Compute time intervals in seconds
time_intervals = np.diff(total_time_minutes) * 60  # minutes to seconds

def get_index(battery_time_start, time_intervals):
    now = datetime.now(timezone.utc)
    elapsed_seconds = (now - battery_time_start).total_seconds()
    cumulative_intervals = np.cumsum(time_intervals)

    for i in range(len(cumulative_intervals)):
        if elapsed_seconds < cumulative_intervals[i]:
            return i
    return len(cumulative_intervals) - 1

def update_dashboard_state(request):
    # Example external logic to determine current power state
    battery = float(request.GET.get("battery", 0))  # For testing
    if battery >= 1.0:
        power_source = 'Battery'
        if not request.session.get('battery_time_start'):
            # Set battery start time only once
            request.session['battery_time_start'] = datetime.now(timezone.utc).isoformat()
    else:
        power_source = 'Grid'
        request.session.pop('battery_time_start', None)  # Clear it

    # Simulate battery usage if on battery
    if power_source == 'Battery' and request.session.get('battery_time_start'):
        battery_time_start = datetime.fromisoformat(request.session['battery_time_start'])
        index = get_index(battery_time_start, time_intervals)

        if index < len(battery_percentages):
            battery_percentage = battery_percentages[index]
            remaining_time = estimate_remaining_time(battery_percentage)

            print(f"Battery updated: {battery_percentage}%, Estimated Time: {remaining_time // 60}h {remaining_time % 60}m", f"Index: {index}")
        else:
            battery_percentage = 0
            remaining_time = 0
    else:
        battery_percentage = None
        remaining_time = None

    # IotaWatt request
    url = 'http://192.168.0.111/query?select=[time.iso,input_0,Fridge,Solar,Recepticles]&begin=s-5s&end=s&group=5s&format=json&header=yes'
    response = requests.get(url)

    if response.status_code != 200:
        return JsonResponse({'error': 'Error fetching data from IotaWatt'}, status=500)

    return JsonResponse({
        'power_source': power_source,
        'battery_percentage': battery_percentage,
        'remaining_time_minutes': round(remaining_time, 2) if remaining_time is not None 
        else None
    })

