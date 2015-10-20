""" Entry point of navigation system."""
from brain import commander
import os

ACC_X_DATA_FILE = "acc_x.txt"
ACC_Y_DATA_FILE = "acc_y.txt"
ACC_Z_DATA_FILE = "acc_z.txt"
COMPASS_DATA_FILE = "compass.txt"
DATA_RATE_FILE = "data_rate.txt"

def remove_previous_data_files():
    try:
        os.remove(ACC_X_DATA_FILE)
    except OSError:
        pass
    try:
        os.remove(ACC_Y_DATA_FILE)
    except OSError:
        pass
    try:
        os.remove(ACC_Z_DATA_FILE)
    except OSError:
        pass
    try:
        os.remove(COMPASS_DATA_FILE)
    except OSError:
        pass
    try:
        os.remove(DATA_RATE_FILE)
    except OSError:
        pass

    print 'previous data files removed'

if __name__ == "__main__":
    remove_previous_data_files()
    commander.start()