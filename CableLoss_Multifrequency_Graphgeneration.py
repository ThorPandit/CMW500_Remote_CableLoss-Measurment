#for any  query contact on Shubham.kumar.bhardwaj@gmail.com with tag:GITHUB ISSUE XXXISSUEXXX
import json
import pyvisa
import logging
import matplotlib.pyplot as plt  # For graphing
import csv  # For report generation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to load configuration from JSON
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Configuration file '{file_path}' not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON configuration: {e}")
        exit(1)

# Load configuration
config = load_config('Config.json')

# Parse configuration values
sg_config = config["signal_generator"]
sa_config = config["signal_analyzer"]
timeout = config["timeout"]

# Use fixed frequencies from JSON
frequencies = sg_config["frequencies"]  # Fixed list of frequencies
power_levels = sg_config["power_levels"]  # List of power levels
attenuation = sg_config["attenuation"]
sa_attenuation = sa_config["attenuation"]

# Initialize VISA connection
rm = pyvisa.ResourceManager()
cmw = rm.open_resource("TCPIP::192.10.9.126::INSTR")

# Reset and initialize
cmw.write('*RST; *OPC?; *CLS; *OPC')
logging.info(f'17-Identity:, {cmw.query("*IDN?")}')
cmw.timeout = timeout

# Data storage for plotting and reporting
results = {power_level: [] for power_level in power_levels}
report_data = []  # For CSV report generation

# Loop through fixed frequencies and power levels
for frequency in frequencies:
    for power_level in power_levels:
        print(f"\nTesting for Frequency: {frequency} Hz at Power Level: {power_level} dBm")

        # Configure signal generator on RF1COM
        cmw.write("ROUTe:GPRF:GEN:SCENario:SALone RF1COM, TX1")
        cmw.write(f"SOURce:GPRF:GEN1:RFSettings:FREQuency {frequency}")
        cmw.write(f"SOURce:GPRF:GEN1:RFSettings:LEVel {power_level}")
        cmw.write("SOURce:GPRF:GEN1:BBMode CW")
        cmw.write(f"SOURce:GPRF:GEN1:RFSettings:EATTenuation {attenuation}")
        cmw.write("SOURce:GPRF:GEN1:STATe ON")
        cmw.query("*OPC?")  # Ensure signal is active

        cmw.timeout = timeout

        # Confirm generator is ON
        print(f"Signal Generator State: {cmw.query('SOURce:GPRF:GEN1:STATe?')}")

        cmw.write("*CLS")

        # Power Measurment at RF2C
        cmw.write("ROUTe:GPRF:MEAS2:SCENario:SALone RF2C, RX1")
        cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:FREQuency {frequency}")
        cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:EATTenuation {sa_attenuation}")
        logging.info(f'Attenuation Errors:, {cmw.query("SYST:ERR?")}')

        #Start the Measurment
        cmw.write("INITiate:GPRF:MEAS2:POWer")
        cmw.query("*OPC?")

        # Fetch received power
        received_power_raw = cmw.query("FETCh:GPRF:MEAS2:POWer:AVERage?")
        print(f"Raw Received Power Response: {received_power_raw}")

        # Parse and calculate cable loss
        try:
            received_power_status, received_power_value = received_power_raw.strip().split(',')
            received_power = float(received_power_value)

            print(f"Received Power: {received_power} dBm")

            # Calculate cable loss
            transmitted_power = float(power_level)
            if(received_power>=transmitted_power):
                cable_loss =  received_power-transmitted_power
                print(f"Cable Loss: {cable_loss:.2f} dB")
            else:
                cable_loss=0

            # Store results for plotting
            results[power_level].append((frequency, cable_loss))

            # Append data to report list
            report_data.append({
                "Frequency (Hz)": frequency,
                "Power Level (dBm)": power_level,
                "Received Power (dBm)": received_power,
                "Cable Loss (dB)": cable_loss
            }

            )

        except ValueError as e:
            print(f"Error parsing received power: {e}")
            logging.error(f"Error parsing received power: {e}")

        print('reaching end')
        cmw.write("SOURce:GPRF:GEN1:STATe OFF")
        print(report_data.append)
        cmw.timeout = timeout

# Close connection
cmw.close()

# Generate CSV Report
csv_file = "Cable_Loss_Report.csv"
with open(csv_file, mode='w', newline='') as file:
    fieldnames = ["Frequency (Hz)", "Power Level (dBm)", "Received Power (dBm)", "Cable Loss (dB)"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(report_data)

print(f"\nReport generated: {csv_file}")

# plot the results
plt.figure(figsize=(10, 6))
for power_level, data in results.items():
    freqs, losses = zip(*data)  # Separate frequencies and cable loss
    plt.plot(freqs, losses, marker='o', label=f"Power Level: {power_level} dBm")


    # Add values at each data point
    for x, y in zip(freqs, losses):
        plt.text(x, y + 0.2, f"{y:.2f}", fontsize=9, ha='center', color='blue')  # Annotate with cable loss values


plt.title("Cable Loss vs Frequency",fontsize=14)
plt.xlabel("Frequency (MHz)",fontsize=12)
plt.ylabel("Cable Loss (dB)",fontsize=12)

# Add grid, legend, and adjust layout
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=10)
plt.tight_layout()

# Save the plot as an image
image_file = "Cable_Loss_Plot.png"
plt.savefig(image_file)
print(f"\nPlot image saved: {image_file}")

# Show the plot
plt.show()

# Close the plot to stop the script
plt.close()
print("Script execution completed.")
