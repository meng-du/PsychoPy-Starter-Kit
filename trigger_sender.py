#
# Meng Du
# October 2017
#

"""
This script automatically send triggers by generating keyboard presses.
Install pyautogui before running this script:
    http://pyautogui.readthedocs.io/en/latest/install.html
It takes three command line arguments. Usage:
    python trigger_sender.py <trigger key> <number of triggers> <time interval between two triggers (in seconds)>
Example:
    python trigger_sender.py t 500 1

Note: Before starting actual key presses, the key will first be pressed 20 times
continuously to determine the average time required to press this key. Make sure
you discard the first 20 triggers. You can change the number below.
"""

from __future__ import print_function
import sys
import time
import timeit
import pyautogui

# the key will first be pressed for this number of times
# to calculate an average time required
NUM_PRE_RUN = 20


def main():
    try:
        # get command line arguments
        key = sys.argv[1]
        if key not in pyautogui.KEYBOARD_KEYS:
            raise ValueError
        num = int(sys.argv[2])
        interval = float(sys.argv[3])

        # get an average time of key press
        def keypress():
            pyautogui.press(key)

        avg_time = timeit.timeit(keypress, number=NUM_PRE_RUN) / NUM_PRE_RUN
        if avg_time > interval:
            raise RuntimeError('Time required for the keyboard press is longer than '
                               'the requested time interval between triggers.')
        interval -= avg_time
        start_time = time.time()

        # press key
        for _ in range(num):
            pyautogui.press(key)
            time.sleep(interval)
        duration = time.time() - start_time
        print('\nPressed ' + str(num) + ' "' + key + '"s in ' + str(duration) + ' seconds\n')

    except (IndexError, ValueError):
        print('Invalid argument.\n'
              'Usage: python trigger_sender.py '
              '<trigger key> '
              '<number of triggers> '
              '<time interval between two triggers (in seconds)>')


if __name__ == '__main__':
    main()
