import pyvisa
import logging

# Configure the logging settings
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format of log messages
)

rm = pyvisa.ResourceManager()
cmw = rm.open_resource("TCPIP::192.10.9.56::INSTR")

cmw.timeout=1000

# Initial system-reset
cmw.write('*RST; *OPC?; *CLS; *OPC')
logging.info(f'17-Identity:, {cmw.query("*IDN?")}')
cmw.timeout=2000

print(f'L20: {cmw.query("ROUTe:GPRF:GEN1?")}')  #SALone: An RF signal is generated (standalone scenario), IQOut: The generated baseband signal is sent to I/Q out (digital baseband interface)
print(f'L22: {cmw.query("ROUTe:GPRF:GEN1:SCENario?")}')

cmw.timeout=2000

#route RF signal to RF1COM
cmw.query("ROUTe:GPRF:GEN1:SCENario:SALone RF1C, TX1")  #<TXConnector>, <TXConverter>
cmw.timeout=2000

#Configure the sequencer list entry: frequency, level, signal type.
cmw.write('SOURce:GPRF:GEN1:RFSettings:FREQuency 1.000000E+009')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')
cmw.timeout=1000
cmw.write('SOURce:GPRF:GEN1:RFSettings:LEVel -70')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')
cmw.timeout=1000
cmw.write('SOURce:GPRF:GEN1:RFSettings:PEPower?')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')
cmw.timeout=1000
cmw.write('SOURce:GPRF:GEN1:BBMode CW')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')
cmw.timeout=1000

# Route output signal for R&S CMW100
# Select the connector bench.
# Activate the first four connectors / deactivate the last four.
# Deactivate the first connector.

cmw.write('ROUTe:GPRF:GEN:SCENario:SALone R118, TX1')
logging.info(f'26-Errors:, {cmw.query("SYST:ERR?")}')
cmw.timeout=1000

cmw.write('CONFigure:GPRF:GEN:CMWS:USAGe:TX:ALL R118, ON, ON, ON, ON, OFF, OFF, OFF, OFF')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')

cmw.write('CONFigure:GPRF:GEN:CMWS:USAGe:TX R11, OFF')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')

#Define external attenuation.
cmw.write('SOURce:GPRF:GEN:RFSettings:EATTenuation 2')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')
cmw.timeout=1000

#Set repetition to continuous.
cmw.write('SOURce:GPRF:GEN:SEQuencer:REPetition CONT')
logging.info(f'Errors:, {cmw.query("SYST:ERR?")}')
cmw.timeout=1000

#Switch on the sequencer. With command synchronization, the queried
print(f"{cmw.query('SOURce:GPRF:GEN:SEQuencer:STATe ON; *OPC?')}")
cmw.query('SOURce:GPRF:GEN:SEQuencer:STATe?')

#GPRF Generator

