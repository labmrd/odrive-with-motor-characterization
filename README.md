This repository contains work done by the University of Minnesota Medical Robotics and Devices lab. It is based on the ODrive project, taking the main firmware and software of the ODrive (used for brushless DC motor control, primarily for robotics) and augmenting it with test input and data collection features to aid in motor characterization for fast tuning and/or more sophisticated controller design. This project uses ODrive software/firmware v0.5.1 on a v3.6-24V board.

For project-specific information (including a [full report writetup](https://github.com/labmrd/odrive-with-motor-characterization/blob/main/docs/motor_characterization_references/report/Goldberg_plan_B_report.pdf) and presentation with example data and analysis), see the motor_characterization_references folder of docs. For a quick list of code changes, see the [summary of contributions](https://github.com/labmrd/odrive-with-motor-characterization/blob/main/docs/motor_characterization_references/report/Summary%20of%20Contributions_v5.pdf).

For more information on the ODrive, see their [product website](https://odriverobotics.com/), [user guide](https://docs.odriverobotics.com/), [developer guide](https://docs.odriverobotics.com/developer-guide), and [github](https://github.com/odriverobotics/ODrive).

### Repository Structure
 * **Firmware**: ODrive firmware
 * **tools**: Python library & tools
 * **docs**: Documentation

### MRD Lab Edits
 * **Test Inputs**: Axis class edited to add user-configurable voltage inputs
 * **Data Collection**: communication protocol and Axis class edited to add a ring buffer of data saved during test inputs
 * **Data Export**: odrivetool edited to access ring buffer, plot results, and export to CSV
