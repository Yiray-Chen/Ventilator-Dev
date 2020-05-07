import pigpio
import time
import vent.io as io
from random import random

hal = io.Hal(config_file='vent/io/config/devices.ini')

print('PWM Frequency: ', hal._control_valve.frequency)


breath_time = 10
insp_time = 5
inhale_time = insp_time / 3.0
n_ramp_steps = 5
pip = 25
KP = 0.0001
KD = 0.0
KI = 0.0
dc = 0

hal._pressure_sensor.calibrate()

def cycle(dc):
    
    # Get cycle start time:
    
    tick_cycle = time.time()
    p = hal.pressure
    f = hal.flow
    

    # Ramp up to PIP over inhale time
    for i in range(n_ramp_steps+1):
        tick_loop = time.time()
        setpt = pip / n_ramp_steps * i
        do_cont = 0
        
        prev_error = 0
        sum_error = 0
        
        dc = 0.4 / n_ramp_steps * i + 0.6
        hal.setpoint = max(min(1, dc), 0)*100
        
        while(do_cont == 0):
            error = setpt - p
            dc += (error * KP) + (prev_error * KD) + (sum_error * KI)
            hal.setpoint = max(min(1, dc), 0)*100
            p = hal.pressure
            f = hal.flow
            print('PWM: %3.2f Req. Pressure: %5.4f Actual Pressure: %5.4f Flow: %5.2f '%(dc,setpt,p,f),end='\r')
            tock_loop = time.time()
            if((tock_loop - tick_loop) > 10):
                do_cont = 1
            prev_error = error
            sum_error += error
            time.sleep(0.005)
            
             
    hal.setpoint = 0
    time.sleep(3)            

    print('\n Done')

try:
    cycle(dc)
finally:
    hal._inlet_valve.close()
    hal._control_valve.close()





