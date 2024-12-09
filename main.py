import json
import pyvisa
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to load configuration from JSON
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print(f"Configuration file '{file_path}' not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON configuration: {e}")
        exit(1)

# Load configuration
config = load_config('Config.json')

# Parse configuration values
RFGenerator_Config = config["signal_generator"]
MEASAnalyzer_Config = config["signal_analyzer"]
timeout = config["timeout"]

frequency = RFGenerator_Config["frequencies"]
power_level = RFGenerator_Config["power_levels"]
attenuation = RFGenerator_Config["attenuation"]

# Initialize VISA connection
rm = pyvisa.ResourceManager()
cmw = rm.open_resource("TCPIP::192.10.9.91::INSTR")

# Reset and initialize
cmw.write('*RST; *OPC?; *CLS; *OPC')
logging.info(f'CMW_Identity:, {cmw.query("*IDN?")}')
cmw.timeout = timeout

# Configure signal generator on RF1COM
cmw.write("ROUTe:GPRF:GEN:SCENario:SALone RF1COM, TX1")
cmw.write(f"SOURce:GPRF:GEN1:RFSettings:FREQuency {frequency}")
cmw.write(f"SOURce:GPRF:GEN1:RFSettings:LEVel {power_level}")
cmw.write("SOURce:GPRF:GEN1:BBMode CW")
cmw.write(f"SOURce:GPRF:GEN1:RFSettings:EATTenuation {attenuation}")
cmw.write("SOURce:GPRF:GEN1:STATe ON")
print(cmw.query("*OPC?"))
cmw.timeout = timeout

# Confirm generator is ON
print(f"Signal Generator State: {cmw.query('SOURce:GPRF:GEN1:STATe?')}")

cmw.write("*CLS")

# Configure signal analyzer on RF2COM
Measurment_frequency = MEASAnalyzer_Config["frequency"]
Measurment_attenuation = MEASAnalyzer_Config["attenuation"]

print(f'{cmw.query("ROUTe:GPRF:MEAS2?")}')
cmw.write("ROUTe:GPRF:MEAS2:SCENario:SALone RF2C, RX1")
cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:FREQuency {Measurment_frequency}")
cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:EATTenuation {Measurment_attenuation}")
logging.info(f'Attenuation Errors:, {cmw.query("SYST:ERR?")}')

# Start and fetch received power measurement
cmw.write("INITiate:GPRF:MEAS2:POWer")
cmw.query("*OPC?")

# Fetch received power 'Average for static result'
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
    print(f'{cmw.query("SOURce:GPRF:GEN1:RFSettings:FREQuency?")}')
    print(f'{cmw.query("FETCh:GPRF:MEAS2:EPSensor?")}')
    print(f"Cable Loss: {cable_loss:.2f} dB")

except ValueError as e:
    print(f"Error parsing received power: {e}")
    logging.error(f"Error parsing received power: {e}")

# Close connection
cmw.close()
