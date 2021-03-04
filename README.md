IN PROGRESS - this work is unfinished. Estimated completion date: April 9, 2021.

This repository contains work done by the University of Minnesota Medical Robotics and Devices lab. It is a spinoff of the ODrive project, taking the main firmware and software of the ODrive (used for brushless DC motor control, primarily for robotics) and augmenting it with test input and data collection features to aid in motor characterization for fast tuning.

For more information on the ODrive, see their [product website](https://odriverobotics.com/), [user guide](https://docs.odriverobotics.com/), [developer guide](https://docs.odriverobotics.com/developer-guide), and [github](https://github.com/odriverobotics/ODrive).

### Repository Structure
 * **Firmware**: ODrive firmware
 * **tools**: Python library & tools
 * **docs**: Documentation

### MRD Lab Edits
 * **Test Inputs**: Axis class edited to add user-configurable voltage inputs
 * **Data Collection**: communication protocol and Axis class edited to add a ring buffer of data saved during test inputs
 * **Data Export**: odrivetool edited to access ring buffer, plot results, and export to CSV
