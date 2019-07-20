from .WAVReader import WAVFile
from .constants import pending_message, GREEN, RED, WHITE, START_MARKER, STOP_MARKER
import numpy as np


def decode_message(filepath):
    print("\n+==========================================================+")
    with pending_message('Reading file...'):
        audiofile = WAVFile(filepath)

    with pending_message('Reading messages...'):
        message = audiofile.read_message(START_MARKER, STOP_MARKER)

    if message:
        print(GREEN)
        print('Message successfuly read!', WHITE)
        print(message)
    else:
        print(RED, '\nNo message hidden in this file!', WHITE)
    print("+==========================================================+\n")
