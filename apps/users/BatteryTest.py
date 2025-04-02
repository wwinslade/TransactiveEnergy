import tkinter as tk
from tkinter import ttk, simpledialog
import numpy as np

# Battery Data
battery_percentages = np.array([100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 
                                45, 40, 35, 30, 25, 20, 15, 10, 5, 0])
total_time_minutes = np.array([0, 11, 23, 36, 47, 55, 64, 74, 82, 91, 99, 
                               107, 114, 120, 126, 132, 138, 155, 171, 181, 193])

# Time intervals between percentage drops
time_intervals = np.diff(total_time_minutes)  
time_intervals_ms = (time_intervals * 60 * 1000).astype(int)  

# Quadratic model for Estimated Remaining Time
coeffs_R_P = np.polyfit(battery_percentages, total_time_minutes[::-1], 2)
d, e, f = coeffs_R_P

def estimate_remaining_time(battery_percentage):
    if battery_percentage <= 0:
        return 0
    return max(0, d * battery_percentage**2 + e * battery_percentage + f)

# GUI Setup
root = tk.Tk()
root.withdraw()  

# User input for starting battery percentage
user_input = simpledialog.askinteger("Battery Input", "Enter starting battery percentage (0-100):", 
                                     minvalue=0, maxvalue=100)

if user_input is None:
    exit()  # Exit if user cancels input

# Goes to closest percentage from input
battery_percentage = max([p for p in battery_percentages if p <= user_input])
index = np.where(battery_percentages == battery_percentage)[0][0]  

# Remaining time based on input
remaining_time = int(estimate_remaining_time(battery_percentage))

# Main GUI window
root.deiconify()
root.title("Battery Monitor")
root.geometry("400x250")
root.configure(bg="black")

# Progress Bar Style
style = ttk.Style()
style.theme_use("clam")

def update_bar_color():
    if battery_percentage > 40:
        bar_color = "#39FF14"  # Neon Green
    elif battery_percentage > 20:
        bar_color = "#FFD700"  # Yellow
    else:
        bar_color = "#FF3131"  # Red

    style.configure("Battery.Horizontal.TProgressbar", 
                    troughcolor="black", 
                    background=bar_color, 
                    thickness=20)

# Progress Bar
style.configure("Battery.Horizontal.TProgressbar", 
                troughcolor="black", 
                background="#39FF14",  
                thickness=20)

battery_bar = ttk.Progressbar(root, length=300, mode='determinate', 
                              maximum=100, style="Battery.Horizontal.TProgressbar")
battery_bar.pack(pady=20)

# Labels
battery_label = tk.Label(root, text=f"Battery: {battery_percentage}%", font=("Arial", 14), fg="white", bg="black")
battery_label.pack()

time_label = tk.Label(root, text=f"Estimated Time Left: {remaining_time // 60}h {remaining_time % 60}m", 
                      font=("Arial", 12), fg="white", bg="black")
time_label.pack()

# Battery percentage at correct intervals
def update_battery():
    global battery_percentage, index

    if index < len(time_intervals):
        battery_percentage = battery_percentages[index]  
        battery_bar['value'] = battery_percentage
        battery_label.config(text=f"Battery: {battery_percentage}%")
        update_bar_color()

        # Schedule next update
        root.after(time_intervals_ms[index], update_battery)
        index += 1  

# Update remaining time every minute
def update_time():
    global remaining_time

    if remaining_time > 0:
        remaining_time -= 1  
        hours = int(remaining_time // 60)
        minutes = int(remaining_time % 60)
        time_label.config(text=f"Estimated Time Left: {hours}h {minutes}m")

        root.after(60000, update_time)

# Set progress bar to user input value
battery_bar['value'] = battery_percentage

# Start battery decrease
root.after(1000, update_battery)

# Live time updates
update_time()

root.mainloop()