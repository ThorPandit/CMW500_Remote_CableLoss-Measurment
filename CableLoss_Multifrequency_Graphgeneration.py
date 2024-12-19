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
    cmw_type=config["cmw_type"]

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
    Gauss_BW=10
    Usermargin=10
    if(cmw_type=="CMW500"):
        print("Testing started for CMW500")
        for frequency in frequencies:
            for power_level in power_levels:
                try:
                    cmw.query("ROUTe:GPRF:GEN1:SCENario:SALone?")
                    cmw.write("ROUTe:GPRF:GEN1:SCENario:SALone RF1COM, TX1")
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
                    cmw.write("CONFigure:GPRF:MEAS2:POWer:MODE POWer")
                    cmw.write("CONFigure:GPRF:MEAS:POWer:FILTer:GAUSs:BWIDth 1E+4")
                    cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:ENPower {power_level}")
                    cmw.write(f"CONFigure:GPRF:MEAS2:RFSettings:UMARgin {Usermargin}")
                    cmw.write("INITiate:GPRF:MEAS2:POWer")
                    cmw.query("*OPC?")

                    raw_power = cmw.query("FETCh:GPRF:MEAS2:POWer:AVERage?").strip().split(',')
                    received_power = float(raw_power[1])
                    cmw.write("SOURce:GPRF:GEN1:STATe OFF")
                    cmw.write("ABORt:GPRF:MEAS2:POWer")

                    cable_loss = max(0, received_power - float(power_level))
                    #cable_loss=float(power_level)-received_power
                    results[power_level].append((frequency, cable_loss))
                    report_data.append({"Frequency (Hz)": frequency, "Power Level (dBm)": power_level,
                                        "Received Power (dBm)": received_power, "Cable Loss (dB)": cable_loss})
                except Exception as e:
                    logging.error(f"Error: {e}")
    else:
        print("Testing started for CMW100")
        for frequency in frequencies:
            # print(frequency)
            for power_level in power_levels:
                # print(power_level)
                try:
                    cmw.timeout = timeout
                    #print(f"going to test for {power_level} & {frequency}")
                    cmw.write("ROUTe:GPRF:GEN1:SCENario:SALone R118, TX11")
                    cmw.write("CONFigure:GPRF:GEN1:CMWS:USAGe:TX:ALL R118, ON, OFF, OFF, OFF, OFF, OFF, OFF, OFF")
                    cmw.query("*OPC?")
                    cmw.write("*CLS")
                    #print("Connector Setting error:", cmw.query("SYST:ERR?"))
                    #cmw.write("CONFigure:GPRF:GEN1:CMWS:USAGe:TX R11, OFF")
                    cmw.write(f"SOURce:GPRF:GEN1:RFSettings:FREQuency {frequency}")
                    cmw.write(f"SOURce:GPRF:GEN1:RFSettings:LEVel {power_level}")
                    cmw.write("SOURce:GPRF:GEN1:BBMode CW")
                    cmw.write(f"SOURce:GPRF:GEN1:RFSettings:EATTenuation {attenuation}")
                    cmw.timeout = timeout
                    cmw.write("SOURce:GPRF:GEN1:STATe ON")
                    cmw.query("*OPC?")
                    cmw.write("*CLS")
                    # print("Generator On cand clear the flags error:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

                    #print("going for measurment check")
                    cmw.write("ROUTe:GPRF:MEAS:SCENario:SALone R12, RX11")  # RXConnector & RFConverter
                    # print("Measurment setting", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

                    cmw.write(f"CONFigure:GPRF:MEAS:RFSettings:FREQuency {frequency}")
                    # print("Measurment setting", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
                    cmw.write(f"CONFigure:GPRF:MEAS:RFSettings:EATTenuation {attenuation}")
                    # print("Measurment setting", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

                    cmw.write("CONFigure:GPRF:MEAS:POWer:MODE POWer")
                    # print("Measurment setting Gauss_BW", cmw.query("SYST:ERR?"))

                    cmw.write("CONFigure:GPRF:MEAS:POWer:FILTer:TYPE GAUSs")
                    # print("Measurment setting Gauss_BW", cmw.query("SYST:ERR?"))

                    cmw.write(f"CONFigure:GPRF:MEAS:POWer:FILTer:GAUSs:BWIDth 1E+4")
                    # print("Measurment setting Gauss_BW", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

                    cmw.write(f"CONFigure:GPRF:MEAS:RFSettings:ENPower {power_level}")
                    # print("Measurment setting power_level", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

                    cmw.write(f"CONFigure:GPRF:MEAS:RFSettings:UMARgin {Usermargin}")
                    # print("Measurment setting Usermargin", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

                    cmw.timeout = timeout

                    cmw.write("INITiate:GPRF:MEAS:POWer")
                    #print("Measurment setting POWer", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

                    cmw.query("*OPC?")
                    # print(cmw.query("FETCh:GPRF:MEAS:POWer:AVERage?"))

                    raw_power = cmw.query("FETCh:GPRF:MEAS:POWer:AVERage?").strip().split(',')
                    cmw.timeout = timeout
                    #print("Query issue:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
                    #print(raw_power)

                    cmw.write("ABORt:GPRF:MEAS:POWer")
                    cmw.timeout = timeout

                    cmw.write("SOURce:GPRF:GEN1:STATe OFF")
                    cmw.timeout = timeout

                    received_power = float(raw_power[1])
                    print(f"Receive power: {received_power}")
                    print(f"Input Power: {float(power_level)}")

                    cable_loss = max(0,  float(power_level)-received_power)
                    #cable_loss=float(power_level)-received_power
                    print(f"For Power: {power_level} dBm, for Frequency: {frequency} Khz")
                    print(cable_loss)
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
