import tkinter as tk
from tkinter import messagebox
import json
import subprocess

# Function to update the JSON configuration
def update_config():
    try:
        frequencies = freq_entry.get()
        power_levels = power_entry.get()
        attenuation = attenuation_entry.get()

        # Convert inputs to appropriate types
        freq_list = [float(f.strip()) for f in frequencies.split(",")]
        power_list = [int(p.strip()) for p in power_levels.split(",")]
        attenuation_value = float(attenuation)

        # Update the JSON configuration
        config = {
            "signal_generator": {
                "frequencies": freq_list,
                "power_levels": power_list,
                "attenuation": attenuation_value
            },
            "signal_analyzer": {
                "attenuation": attenuation_value
            },
            "timeout": 3000
        }

        # Save the updated configuration to Config.json
        with open("Config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

        # Notify the user
        messagebox.showinfo("Success", "Configuration updated successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update configuration: {e}")

# Function to run the measurement script
def run_script():
    try:
        # Assuming your main script is named `main.py`
        subprocess.run(["python", "CableLoss_Multifrequency_Graphgeneration.py"], check=True)
        messagebox.showinfo("Success", "Measurement completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute the script: {e}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Cable Loss Measurement UI")

# Frequency Input
tk.Label(root, text="Frequencies (Hz in 10^9 , comma-separated):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
freq_entry = tk.Entry(root, width=50)
freq_entry.grid(row=0, column=1, padx=10, pady=10)

# Power Levels Input
tk.Label(root, text="Power Levels (dBm, comma-separated):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
power_entry = tk.Entry(root, width=50)
power_entry.grid(row=1, column=1, padx=10, pady=10)

# Attenuation Input
tk.Label(root, text="Attenuation (dB):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
attenuation_entry = tk.Entry(root, width=50)
attenuation_entry.grid(row=2, column=1, padx=10, pady=10)

# Buttons
update_button = tk.Button(root, text="Update Config", command=update_config)
update_button.grid(row=3, column=0, padx=10, pady=20)

run_button = tk.Button(root, text="Run Measurement", command=run_script)
run_button.grid(row=3, column=1, padx=10, pady=20)

# Start the Tkinter main loop
root.mainloop()
