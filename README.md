This repository contains work done by the University of Minnesota Medical Robotics and Devices lab. It is a spinoff of the ODrive project, taking the main firmware and software of the ODrive (used for brushless DC motor control, primarily for robotics) and augmenting it with test input and data collection features to aid in motor characterization for fast tuning and/or more sophisticated control design. This project uses ODrive software/firmware v0.4.11 on a v3.6-24V board.

NOTE: This is the v0.4.11 version of a project that has since been updated to v0.5.1. This version is still functional and its reference materials are internally consistent, but the report, data, etc. will be more up-to-date in the main (v5) branch.

For project-specific information (including a [full report writetup](https://github.com/labmrd/odrive-with-motor-characterization/blob/v4/docs/references/Goldberg_plan_B_report.pdf) with example data and analysis), see the references folder of docs. For a quick list of code changes, see the [summary of contributions](https://github.com/labmrd/odrive-with-motor-characterization/blob/v4/docs/references/Summary-of-Contributions.pdf).

For more information on the ODrive, see their [product website](https://odriverobotics.com/), [user guide](https://docs.odriverobotics.com/), [developer guide](https://docs.odriverobotics.com/developer-guide), and [github](https://github.com/odriverobotics/ODrive).

### Repository Structure
 * **Firmware**: ODrive firmware
 * **tools**: Python library & tools
 * **docs**: Documentation (including references and example data/analysis)

### MRD Lab Edits
 * **Test Inputs**: Axis class edited to add user-configurable voltage inputs
 * **Data Collection**: communication protocol and Axis class edited to add a ring buffer of data saved during test inputs
 * **Data Export**: odrivetool edited to access ring buffer, plot results, and export to CSV
