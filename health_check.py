#!/usr/bin/python3.7
import time
from gpiozero import CPUTemperature
import psutil
import sys
from datetime import datetime

def check_temp(threshold=70):
    '''
    uses gpiozero to measure the cpu temp of the pi
    returns a data structure with the  result, a status flag
    and a string representation of what is going on.
    '''
    cpu = CPUTemperature()
    temp_C = cpu.temperature
    alert = int(temp_C) >= threshold
    alert_str = f'The temp is: {temp_C}'

    return {'result': temp_C,
            'alert_status': alert,
            'message': alert_str}

def get_memory(threshold=95):
    '''
    using psutil determine how much free memory (RAM) there is.
    uses the .free method which returns memory not used at all (zeroed) that is
    readily available - note that this does not reflect the actual memory
    available
    param threshold is expressed as a percent
    '''
    vm = psutil.virtual_memory()
    free_m = vm.free/1073741824
    return {'message': f'% of memory used: {vm.percent}\nGB free is: {free_m:.2f}',
            'alert_status': vm.percent>threshold,
            'result': f'{vm.percent}%'}

def get_cpu(duration=4, all_cpu=True, threshold=90):
    '''
    using psutil determine how much cpu is being used over duration.
    uses .cpu_percent method with takes two parameters
    interval (duration) and percpu (all_cpu)
    returns a float representing the current system-wide CPU utilization
    as a % when percpu is True returns a list of floats representing
    the utilization as a % for each CPU.

    '''
    usage = psutil.cpu_percent(duration, all_cpu)
    avg = sum(usage)/len(usage)
    return {'result': usage,
            'alert_status': avg > threshold,
            'message': f'cpu usage over {duration} seconds is {usage}'}

def parse_args(arg):
    '''
    helper to parse the command line argument
    which should provide the number of times to cycle through
    the tests
    returns (True, <number of cycles as int>)
    or if the input is invalid (None, None)
    '''

    try:
        valid = type(int(arg)) == int
        return (valid, int(arg))
    except Exception as Error:
        print('please provide a number as an argument for the number of tests that you wish to run')
        return (None, None)

health_functions = [check_temp]

if __name__ == '__main__':
    repeat = 1
    count = 0
    if len(sys.argv) == 2:
        valid, arg = parse_args(sys.argv[1])
        if valid:
            repeat = arg
    while count < repeat:
        print('\n')
        for f in health_functions:
            check = f()
            m_str = f"{datetime.now()}: {check['message']}"
            if check['alert_status']:
                print('ALERT!')
                print(m_str)
            else:
                print(m_str)
        count +=1
        time.sleep(30)
