import pyvisa_py
import json
import pyvisa
import logging
import matplotlib.pyplot as plt
import csv
import os


def main():
    print("Starting Cable Loss Measurement...")

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load configuration
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "Config.json")

    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print(f"Configuration file '{config_path}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON configuration: {e}")
        return

    sg_config = config["signal_generator"]
    sa_config = config["signal_analyzer"]
    timeout = config["timeout"]

    frequencies = sg_config["frequencies"]
    power_levels = sg_config["power_levels"]
    attenuation = sg_config["attenuation"]
    sa_attenuation = sa_config["attenuation"]

    # VISA connection
    rm = pyvisa.ResourceManager()
    cmw = rm.open_resource(f"TCPIP::{config['cmw_ip']}::INSTR")
    cmw.write('*RST; *OPC?; *CLS; *OPC')
    cmw.timeout = timeout

    results = {power_level: [] for power_level in power_levels}
    report_data = []

    for frequency in frequencies:
        for power_level in power_levels:
            try:
                cmw.write("ROUTe:GPRF:GEN:SCENario:SALone RF1COM, TX1")
                cmw.write(f"SOURce:GPRF:GEN1:RFSettings:FREQuency {frequency}")
                cmw.write(f"SOURce:GPRF:GEN1:RFSettings:LEVel {power_level}")
                cmw.write("SOURce:GPRF:GEN1:BBMode CW")
                cmw.write(f"SOURce:GPRF:GEN1:RFSettings:EATTenuation {attenuation}")
                cmw.write("SOURce:GPRF:GEN1:STATe ON")
                cmw.query("*OPC?")

                cmw.write("*CLS")
                cmw.write("ROUTe:GPRF:MEAS2:SCENario:SALone RF2C, RX1")
                cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:FREQuency {frequency}")
                cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:EATTenuation {sa_attenuation}")
                cmw.write("INITiate:GPRF:MEAS2:POWer")
                cmw.query("*OPC?")

                raw_power = cmw.query("FETCh:GPRF:MEAS2:POWer:AVERage?").strip().split(',')
                received_power = float(raw_power[1])

                cable_loss = max(0, received_power - float(power_level))
                results[power_level].append((frequency, cable_loss))
                report_data.append({"Frequency (Hz)": frequency, "Power Level (dBm)": power_level,
                                    "Received Power (dBm)": received_power, "Cable Loss (dB)": cable_loss})
            except Exception as e:
                logging.error(f"Error: {e}")

    cmw.close()

    csv_file = os.path.join(base_dir, "Cable_Loss_Report.csv")
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Frequency (Hz)", "Power Level (dBm)", "Received Power (dBm)", "Cable Loss (dB)"])
        writer.writeheader()
        writer.writerows(report_data)

    plt.figure(figsize=(10, 6))
    for power_level, data in results.items():
        freqs, losses = zip(*data)
        plt.plot(freqs, losses, marker='o', label=f"{power_level} dBm")
        for x, y in zip(freqs, losses):
            plt.text(x, y, f"{y:.2f}", fontsize=8)

    plt.title("Cable Loss vs Frequency")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Cable Loss (dB)")
    plt.legend()
    plt.grid()
    plot_path = os.path.join(base_dir, "Cable_Loss_Plot.png")
    plt.savefig(plot_path)
    plt.show()


if __name__ == "__main__":
    main()
