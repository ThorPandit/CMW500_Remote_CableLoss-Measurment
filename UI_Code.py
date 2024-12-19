import pyvisa_py
import tkinter as tk
from tkinter import messagebox, IntVar
import json
import webbrowser
import os
#from CableLoss_Multifrequency_Graphgeneration import main as run_measurement
from CableLoss_Multifrequency_Graphgeneration import main as run_measurement

# Function to run the measurement script
def run_script():
    try:
        messagebox.showinfo("Started", "Measurement started, please wait for final results")
        run_measurement()  # Call the main function of the measurement script
        messagebox.showinfo("Success", "Measurement completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute the script: {e}")

# Get the directory where the script is running
base_dir = os.path.dirname(os.path.abspath(__file__))

# Update paths to use base_dir
config_path = os.path.join(base_dir, "Config.json")

# Function to open LinkedIn
def open_link1():
    webbrowser.open("https://www.linkedin.com/in/shubham-kumar-bhardwaj-773368335/")  # Replace with your URL

# Function to open GitHub
def open_link2():
    webbrowser.open("https://github.com/ThorPandit/CMW500_Remote_CableLoss-Measurment/tree/main")  # Replace with your URL

# Function to update the JSON configuration
def update_config():
    try:
        # Collect CMW IP
        cmw_ip = cmw_ip_entry.get()
        if not cmw_ip:
            raise ValueError("CMW IP cannot be empty")

        # Collect selected predefined frequencies
        selected_frequencies = [
            freq for freq, var in predefined_freq_vars.items() if var.get()
        ]

        # Collect selected cmw type
        selected_cmw_type = [
            cmw_type for cmw_type, var in cmw_type_var.items() if var.get()
        ]

        # Collect selected predefined power levels
        selected_power_levels = [
            power for power, var in predefined_power_vars.items() if var.get()
        ]

        # Collect selected predefined attenuation
        selected_attenuation = [
            attenuation for attenuation, var in predefined_attenuation_vars.items() if var.get()
        ]

        # Collect custom frequencies, if provided
        if custom_freq_entry.get():
            custom_frequencies = [
                float(f.strip()) for f in custom_freq_entry.get().split(",")
            ]
            selected_frequencies.extend(custom_frequencies)

        # Collect custom power levels, if provided
        if custom_power_entry.get():
            custom_power_levels = [
                int(p.strip()) for p in custom_power_entry.get().split(",")
            ]
            selected_power_levels.extend(custom_power_levels)

        # Collect custom attenuation, if provided
        if custom_attenuation_entry.get():
            custom_attenuation = float(custom_attenuation_entry.get())
            selected_attenuation.append(custom_attenuation)

        # Update the JSON configuration
        config = {
            "cmw_ip": cmw_ip,
            "cmw_type":selected_cmw_type,
            "signal_generator": {
                "frequencies": selected_frequencies,
                "power_levels": selected_power_levels,
                "attenuation": selected_attenuation[0] if selected_attenuation else 2  # Default to 2
            },
            "signal_analyzer": {
                "attenuation": selected_attenuation[0] if selected_attenuation else 2
            },
            "timeout": 3000
        }

        # Save the updated configuration to Config.json
        with open(config_path, "w") as config_file:
            json.dump(config, config_file, indent=4)

        # Notify the user
        messagebox.showinfo("Success", "Configuration updated successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update configuration: {e}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Cable Loss Measurement with CMW500")

# CMW IP Section
tk.Label(root, text="CMW IP Address:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
cmw_ip_entry = tk.Entry(root, width=50)
cmw_ip_entry.grid(row=0, column=1, padx=10, pady=10)

# Predefined Frequencies Section
tk.Label(root, text="Select Frequencies (MHz):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
predefined_frequencies = [900e6, 1800e6, 2100e6, 2300e6, 2600e6]  # Hz
predefined_freq_vars = {}
for i, freq in enumerate(predefined_frequencies):
    var = IntVar()
    predefined_freq_vars[freq] = var
    tk.Checkbutton(root, text=f"{freq / 1e6} MHz", variable=var).grid(
        row=i + 2, column=0, padx=10, sticky="w"
    )


# Predefined Power Levels Section
tk.Label(root, text="Select CMW Type:").grid(
    row=len(predefined_frequencies) + 3, column=1, padx=10, pady=10, sticky="w"
)
CMW_type = ["CMW500", "CMW100"]  # dBm
cmw_type_var = {}
for i, cmw in enumerate(CMW_type):
    var = IntVar()
    cmw_type_var[cmw] = var
    tk.Checkbutton(root, text=f"{cmw}", variable=var).grid(
        row=len(predefined_frequencies) + 4 + i, column=1, padx=10, sticky="w"
    )


# Predefined Power Levels Section
tk.Label(root, text="Select Power Levels (dBm):").grid(
    row=len(predefined_frequencies) + 3, column=0, padx=10, pady=10, sticky="w"
)
predefined_power_levels = [-50, -40, -30, -20, -10, 0]  # dBm
predefined_power_vars = {}
for i, power in enumerate(predefined_power_levels):
    var = IntVar()
    predefined_power_vars[power] = var
    tk.Checkbutton(root, text=f"{power} dBm", variable=var).grid(
        row=len(predefined_frequencies) + 4 + i, column=0, padx=10, sticky="w"
    )

# Predefined Attenuation Section
tk.Label(root, text="Select Attenuation (dB):").grid(
    row=len(predefined_frequencies) + len(CMW_type) + 4, column=1, padx=10, pady=10, sticky="w"
)
predefined_attenuations = [0, 2]  # dB
predefined_attenuation_vars = {}
for i, attenuation in enumerate(predefined_attenuations):
    var = IntVar()
    predefined_attenuation_vars[attenuation] = var
    tk.Checkbutton(root, text=f"{attenuation} dB", variable=var).grid(
        row=len(predefined_frequencies) + len(CMW_type) + 5 + i, column=1, padx=10, sticky="w"
    )

# Custom Inputs Section
tk.Label(root, text="Custom Frequencies (MHz, comma-separated):").grid(
    row=1, column=1, padx=10, pady=10, sticky="w"
)
custom_freq_entry = tk.Entry(root, width=50)
custom_freq_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Custom Power Levels (dBm, comma-separated):").grid(
    row=3, column=1, padx=10, pady=10, sticky="w"
)
custom_power_entry = tk.Entry(root, width=50)
custom_power_entry.grid(row=4, column=1, padx=10, pady=10)

tk.Label(root, text="Custom Attenuation (dB):").grid(
    row=5, column=1, padx=10, pady=10, sticky="w"
)
custom_attenuation_entry = tk.Entry(root, width=50)
custom_attenuation_entry.grid(row=6, column=1, padx=10, pady=10)

# Buttons
update_button = tk.Button(root, text="Update Config", command=update_config)
update_button.grid(row=16, column=0, padx=10, pady=20)

run_button = tk.Button(root, text="Run Measurement", command=run_script)
run_button.grid(row=16, column=1, padx=10, pady=20)

tk.Label(root, text="Developed by Mr. Shubham Kumar Bhardwaj").grid(row=17, column=0, padx=10, pady=10, sticky="w")
# Add a label as a hyperlink
linkedin_label = tk.Label(root, text="LinkedIn Profile", fg="blue", cursor="hand2")
linkedin_label.grid(row=17, column=2, padx=10, pady=10, sticky="w")
linkedin_label.bind("<Button-1>", lambda e: open_link1())

#github_label = tk.Label(root, text="GitHub Repository", fg="blue", cursor="hand2")
#github_label.grid(row=17, column=3, padx=10, pady=10, sticky="w")
#github_label.bind("<Button-1>", lambda e: open_link2())

root.mainloop()
