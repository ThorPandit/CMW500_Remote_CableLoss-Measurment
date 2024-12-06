# CMW500_Remote_CableLoss-Measurment
With this application user can take CMW500 on remote using SCIP commands and will give final result on different frequencies. 

**Objective**: Measure RF cable losses by transmitting a signal and measuring the received power at the other end.
**Steps**:
Transmit a known power signal from the CMW500.
Measure the power received at the other end using another port or device.
Calculate the cable loss as the difference between transmitted and received power.
SCPI Commands:
Use SOURce:POWer to set the power level.
Use MEASure:POWer or FETCh:MEASure to measure the power.
Output:
Cable loss in dB displayed in Python and optionally logged for records.
