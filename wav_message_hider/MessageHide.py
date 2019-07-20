from .WAVReader import WAVFile
from .constants import START_MARKER, STOP_MARKER, pending_message, RED, WHITE, GREEN
import numpy as np
import time


def encode_message(message, filepath, new_name):
    message_to_hide = START_MARKER + message + STOP_MARKER
    required_bits = len(message_to_hide) * 8

    print("\n+==========================================================+")
    with pending_message('Reading file...'):
        audiofile = WAVFile(filepath)

    if required_bits > len(audiofile.data):
        raise ValueError('Message is too long. {} bits required but only {} available.'.format(required_bits, audiofile.subchunk_2_size))

    print("\nUse entropy detection coding? y/n:")
    print(RED, "[WARNING]", WHITE, " This will significantly extend the execution time!", sep='')
    if input("Answer: ").lower() not in ('n', 'no'):
        entropy_time = time.clock()
        start_bit = audiofile.select_entropy(required_bits)
        entropy_time = time.clock() - entropy_time
        print("Best place for message found at: {} sample!".format(start_bit))
        print(GREEN, "Entropy calculation took: ", entropy_time, " seconds!", WHITE, sep='')
    else:
        start_bit = 0

    with pending_message('\nHiding yout message...'):
        hide_time = time.clock()
        audiofile.hide_message(message_to_hide, start_bit)
        hide_time = time.clock() - hide_time

    with pending_message('Saving result...'):
        audiofile.save_to(new_name)

    print(GREEN)
    print("Message hidden successfuly!")
    print("Hiding took", hide_time, "seconds!", WHITE)
    print("+==========================================================+")
