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


**Overview of the Setup**
RF1COM: Used as the signal output port for generating the RF signal.
RF2COM: Used as the signal input port for measuring the RF signal after passing through the cable.
Cable: Connects RF1COM to RF2COM for loss measurement.
Goal: Measure the signal attenuation (loss) introduced by the cable by comparing transmitted and received signal levels.

Process:-
1. Input the frequecny range using config.json file.
2. Enter the power level & attaentuation.
3. This will test the cable loss on the given frequency inputs.
4. A CSV will be created and a graph will be generated.
5. Final CSV and Graph will be used.

UI open as below:
![image](https://github.com/user-attachments/assets/1db627aa-49e2-4a8e-bd7f-9bd1e939ee77)

CMW500 IP address entry is mandatory. select the required frequencies, power and attenuation for graph generation.

result will be as:
![image](https://github.com/user-attachments/assets/a7dbf96d-20b3-4817-bf7d-0d001a3ae5e8)

## Download the Executable
You can download the precompiled `.exe` file from the https://github.com/ThorPandit/CMW500_Remote_CableLoss-Measurment/releases/tag/v1.0.0

If you have any issue can contact me on: **shubham.kumar.bhardwaj@gmail.com** Please mark subject as: **GITHUB Issue: CMW500_Remote_CableLoss-Measurment**
