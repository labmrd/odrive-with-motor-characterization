from __future__ import print_function

import sys
import time
import threading
import platform
import subprocess
import os
from fibre.utils import Event
from odrive.enums import errors

try:
    if platform.system() == 'Windows':
        import win32console
        import colorama
        colorama.init()
except ImportError:
    print("Could not init terminal features.")
    print("Refer to install instructions at http://docs.odriverobotics.com/#downloading-and-installing-tools")
    sys.stdout.flush()
    pass

_VT100Colors = {
    'green': '\x1b[92;1m',
    'cyan': '\x1b[96;1m',
    'yellow': '\x1b[93;1m',
    'red': '\x1b[91;1m',
    'default': '\x1b[0m'
}

class OperationAbortedException(Exception):
    pass

def dump_errors(odrv, clear=False):
    axes = [(name, axis) for name, axis in odrv._remote_attributes.items() if 'axis' in name]
    axes.sort()
    for name, axis in axes:
        print(name)

        # Flatten axis and submodules
        # (name, remote_obj, errorcode)
        module_decode_map = [
            ('axis', axis, errors.axis),
            ('motor', axis.motor, errors.motor),
            ('encoder', axis.encoder, errors.encoder),
            ('controller', axis.controller, errors.controller),
        ]

        # Module error decode
        for name, remote_obj, errorcodes in module_decode_map:
            prefix = ' '*2 + name + ": "
            if (remote_obj.error != errorcodes.ERROR_NONE):
                print(prefix + _VT100Colors['red'] + "Error(s):" + _VT100Colors['default'])
                errorcodes_tup = [(name, val) for name, val in errorcodes.__dict__.items() if 'ERROR_' in name]
                for codename, codeval in errorcodes_tup:
                    if remote_obj.error & codeval != 0:
                        print("    " + codename)
                if clear:
                    remote_obj.error = errorcodes.ERROR_NONE
            else:
                print(prefix + _VT100Colors['green'] + "no error" + _VT100Colors['default'])

data_rate = 10
plot_rate = 10
num_samples = 1000
def start_liveplotter(get_var_callback):
    """
    Starts a liveplotter.
    The variable that is plotted is retrieved from get_var_callback.
    This function returns immediately and the liveplotter quits when
    the user closes it.
    """

    import matplotlib.pyplot as plt

    cancellation_token = Event()

    global vals
    vals = []
    def fetch_data():
        global vals
        while not cancellation_token.is_set():
            try:
                data = get_var_callback()
            except Exception as ex:
                print(str(ex))
                time.sleep(1)
                continue
            vals.append(data)
            if len(vals) > num_samples:
                vals = vals[-num_samples:]
            time.sleep(1/data_rate)

    # TODO: use animation for better UI performance, see:
    # https://matplotlib.org/examples/animation/simple_anim.html
    def plot_data():
        global vals

        plt.ion()

        # Make sure the script terminates when the user closes the plotter
        def did_close(evt):
            cancellation_token.set()
        fig = plt.figure()
        fig.canvas.mpl_connect('close_event', did_close)

        while not cancellation_token.is_set():
            plt.clf()
            plt.plot(vals)
            plt.legend(list(range(len(vals))))
            fig.canvas.draw()
            fig.canvas.start_event_loop(1/plot_rate)

    fetch_t = threading.Thread(target=fetch_data)
    fetch_t.daemon = True
    fetch_t.start()
    
    plot_t = threading.Thread(target=plot_data)
    plot_t.daemon = True
    plot_t.start()
    

    return cancellation_token
    #plot_data()

#ERG - modeled off of start_liveplotter; exports motorCharacterizeData to CSV
def start_datarecorder(odrv):
    """
    Starts a datarecorder.
    The variable that is recorded is retrieved from get_var_callback.
    This function returns immediately and the datarecorder quits when
    the user closes the plot window.
    """

    #ERG TODO - delete this once I'm done editing and want it to be an argument instead
    dir = "C:\\Users\\Emily\\Documents\\1Graduate School\\2021 Spring\\Lab\\TestExports"

    import matplotlib.pyplot as plt

    cancellation_token = Event()
    sample_rate = 150
    graph_rate = 10

    global vals
    vals = []
    def fetch_data(dir):
        global vals
        from datetime import datetime

        start_time = datetime.now()
        time_string = start_time.strftime("%m%d%Y_%H%M%S")
        file_name = dir + '\\motorData' + time_string + '.csv'

        with open(file_name, "a+") as file:
            file.write('%Motor characterization data\n')
            file.write("%Each row's values were recorded on the same timestep\n\n")
            file.write('%Operator:\n')
            file.write('%Motor type:\n')
            file.write('%ODrive axis:\n')
            file.write('%Date:,' + start_time.strftime("%d/%m/%Y") + '\n')
            file.write('%Start time:,' + start_time.strftime("%H:%M:%S") + '\n\n')
            file.write('%timestep (8Hz),voltage,position,velocity\n')
            file.write('%[#],[V],[rad],[rad/s]\n')

            while not cancellation_token.is_set():
                try:
                    idx = odrv.motorCharacterizeData_pos #ERG TODO - rename one of the pos to avoid ambiguity
                    data = [odrv.get_motorCharacterizeData_timestep(idx),
                            odrv.get_motorCharacterizeData_voltage(idx),
                            odrv.get_motorCharacterizeData_pos(idx),
                            odrv.get_motorCharacterizeData_vel(idx)]
                except Exception as ex:
                    print(str(ex))
                    time.sleep(1)
                    continue
                
                #Save latest line and write it to csv
                #TODO - if I can flush the whole buffer, write all new lines in vals
                vals.append(data[1:4])
                str_data = map(str,data)
                file.write(",".join(str_data) + ';\n')

                if len(vals) > num_samples:
                    vals = vals[-num_samples:]
                time.sleep(1/sample_rate)

    def plot_data():
        global vals

        plt.ion()

        # Make sure the script terminates when the user closes the plotter
        def did_close(evt):
            cancellation_token.set()
        fig = plt.figure()
        fig.canvas.mpl_connect('close_event', did_close)

        while not cancellation_token.is_set():
            plt.clf()
            plt.plot(vals, scalex=True, scaley=False)
            plt.ylim(-odrv.axis0.motor.config.current_lim, odrv.axis0.motor.config.current_lim)
            plt.legend(('Voltage','Position','Velocity'))
            fig.canvas.draw()
            fig.canvas.start_event_loop(1/graph_rate)

    fetch_t = threading.Thread(target=fetch_data, args=(dir,))
    fetch_t.daemon = True
    fetch_t.start()
    
    plot_t = threading.Thread(target=plot_data)
    plot_t.daemon = True
    plot_t.start()

    return cancellation_token

def run_motor_characterize_input(odrv):
    """
    Runs data collection for motor characterization.
    Note: must be set to gimbal motor mode and current control. Make sure current limit is set appropriately.
    Runs configured test input and records time, voltage command, position, and velocity to csv in dir.
    """

    #ERG TODO - delete this once I'm done editing and want it to be an argument instead
    dir = "C:\\Users\\Emily\\Documents\\1Graduate School\\2021 Spring\\Lab\\TestExports"

    from datetime import datetime
    start_time = datetime.now()
    time_string = start_time.strftime("%m%d%Y_%H%M%S")
    file_name = dir + '\\motorData' + time_string + '.csv'
    
    #ERG TODO - is there a way to do this in a more robust way?
    AXIS_STATE_MOTOR_CHARACTERIZE_INPUT = 11
    timeout = 30 # [s]
    vals = []

    with open(file_name, "a+") as file:
        file.write('%Motor characterization data\n')
        file.write("%Each row's values were recorded on the same timestep\n\n")
        file.write('%Operator:\n')
        file.write('%Motor type:\n')
        file.write('%ODrive axis:\n')
        file.write('%Date:,' + start_time.strftime("%d/%m/%Y") + '\n')
        file.write('%Start time:,' + start_time.strftime("%H:%M:%S") + '\n\n')
        file.write('%timestep (8Hz),voltage,position,velocity\n')
        file.write('%[#],[V],[rad],[rad/s]\n')
        file.flush()

        #Set motor requested state
        print("Input starting...")
        odrv.axis0.requested_state = AXIS_STATE_MOTOR_CHARACTERIZE_INPUT

        started = False
        finished = False
        finish_counter = 0
        while not finished:
            try:            
                idx = odrv.motorCharacterizeData_pos
                if idx < 128:
                    data = [odrv.get_motorCharacterizeData_timestep(idx),
                            odrv.get_motorCharacterizeData_voltage(idx),
                            odrv.get_motorCharacterizeData_pos(idx),
                            odrv.get_motorCharacterizeData_vel(idx)]
                else:
                    print("Warning: invalid motorCharacterizeData_pos")
                    data = [float("NaN"), float("NaN"), float("NaN"), float("NaN")]
            except Exception as ex:
                print(str(ex))
                time.sleep(1)
                continue
            
            vals.append(data)
            
            if not started and data[0] > 0:
                started = True
                
            if started:
                if data[0] < 1:
                    finish_counter += 1
                else:
                    finish_counter = 0

                if finish_counter > 5:
                    finished = True

            elapsed = (datetime.now() - start_time).seconds
            if elapsed > timeout:
                print("Timeout: data collection took more than " + elapsed + "seconds")
                finished = True

            if finished:
                print("Input finished. Recording data...")
                for line in vals:
                    str_data = map(str,line)
                    file.write(",".join(str_data) + ';\n')
                    file.flush()
                print("Data saved at: " + file_name)
    return

def print_drv_regs(name, motor):
    """
    Dumps the current gate driver regisers for the specified motor
    """
    fault = motor.gate_driver.drv_fault
    status_reg_1 = motor.gate_driver.status_reg_1
    status_reg_2 = motor.gate_driver.status_reg_2
    ctrl_reg_1 = motor.gate_driver.ctrl_reg_1
    ctrl_reg_2 = motor.gate_driver.ctrl_reg_2
    print(name + ": " + str(fault))
    print("DRV Fault Code: " + str(fault))
    print("Status Reg 1: " + str(status_reg_1) + " (" + format(status_reg_1, '#010b') + ")")
    print("Status Reg 2: " + str(status_reg_2) + " (" + format(status_reg_2, '#010b') + ")")
    print("Control Reg 1: " + str(ctrl_reg_1) + " (" + format(ctrl_reg_1, '#013b') + ")")
    print("Control Reg 2: " + str(ctrl_reg_2) + " (" + format(ctrl_reg_2, '#09b') + ")")

def show_oscilloscope(odrv):
    size = 18000
    values = []
    for i in range(size):
        values.append(odrv.get_oscilloscope_val(i))

    import matplotlib.pyplot as plt
    plt.plot(values)
    plt.show()

def rate_test(device):
    """
    Tests how many integers per second can be transmitted
    """

    # import matplotlib.pyplot as plt
    # plt.ion()

    print("reading 10000 values...")
    numFrames = 10000
    vals = []
    for _ in range(numFrames):
        vals.append(device.axis0.loop_counter)

    loopsPerFrame = (vals[-1] - vals[0])/numFrames
    loopsPerSec = (168000000/(2*10192))
    FramePerSec = loopsPerSec/loopsPerFrame
    print("Frames per second: " + str(FramePerSec))

    # plt.plot(vals)
    # plt.show(block=True)

def usb_burn_in_test(get_var_callback, cancellation_token):
    """
    Starts background threads that read a values form the USB device in a spin-loop
    """

    def fetch_data():
        global vals
        i = 0
        while not cancellation_token.is_set():
            try:
                get_var_callback()
                i += 1
            except Exception as ex:
                print(str(ex))
                time.sleep(1)
                i = 0
                continue
            if i % 1000 == 0:
                print("read {} values".format(i))
    threading.Thread(target=fetch_data, daemon=True).start()

def yes_no_prompt(question, default=None):
    if default is None:
        question += " [y/n] "
    elif default == True:
        question += " [Y/n] "
    elif default == False:
        question += " [y/N] "

    while True:
        print(question, end='')

        choice = input().lower()
        if choice in {'yes', 'y'}:
            return True
        elif choice in {'no', 'n'}:
            return False
        elif choice == '' and default is not None:
            return default
