import json
import pyvisa
import logging
import numpy as np  # For frequency range generation
import matplotlib.pyplot as plt  # For graphing

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

# Parse frequency range and power levels
frequency_range = sg_config["frequency_range"]
start_freq = frequency_range["start"]
stop_freq = frequency_range["stop"]
step_freq = frequency_range["step"]
frequencies = np.arange(start_freq, stop_freq + step_freq, step_freq)  # Generate frequency range

power_levels = sg_config["power_levels"]  # List of power levels
attenuation = sg_config["attenuation"]
sa_attenuation = sa_config["attenuation"]

# Initialize VISA connection
rm = pyvisa.ResourceManager()
cmw = rm.open_resource("TCPIP::192.10.9.79::INSTR")

# Reset and initialize
cmw.write('*RST; *OPC?; *CLS; *OPC')
logging.info(f'17-Identity:, {cmw.query("*IDN?")}')
cmw.timeout = timeout

# Data storage for plotting
results = {power_level: [] for power_level in power_levels}

# Loop through frequencies and power levels
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

        # Confirm generator is ON
        print(f"Signal Generator State: {cmw.query('SOURce:GPRF:GEN1:STATe?')}")

        cmw.write("*CLS")

        # Configure signal analyzer on RF2COM
        cmw.write("ROUTe:GPRF:MEAS2:SCENario:SALone RF2C, RX1")
        cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:FREQuency {frequency}")
        cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:EATTenuation {sa_attenuation}")
        logging.info(f'Attenuation Errors:, {cmw.query("SYST:ERR?")}')

        # Start and fetch received power measurement
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
            cable_loss = transmitted_power - received_power
            print(f"Cable Loss: {cable_loss:.2f} dB")

            # Store results for plotting
            results[power_level].append((frequency, cable_loss))

        except ValueError as e:
            print(f"Error parsing received power: {e}")
            logging.error(f"Error parsing received power: {e}")


# Close connection
cmw.close()

# Plot the results
plt.figure(figsize=(10, 6))
for power_level, data in results.items():
    freqs, losses = zip(*data)  # Separate frequencies and cable loss
    plt.plot(freqs, losses, marker='o', label=f"Power Level: {power_level} dBm")

plt.title("Cable Loss vs Frequency")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Cable Loss (dB)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
