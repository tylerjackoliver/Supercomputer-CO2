import glob
from time import sleep
from tqdm import tqdm
import numpy as np
import os

XEON_POWER_LOAD = 330 / 1000 # W
CO2_PER_KWH = 0.233 / 1000 # tonnes - https://bulb.co.uk/carbon-tracker/
SKIPPED_FILES = 0

def reverse_readline(filename: str, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename, encoding='latin-1') as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first 
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment


def get_cpu_time(alternate_path='./') -> float:
    global SKIPPED_FILES
    file_list = glob.glob(alternate_path+"slurm-*")
    if not file_list: # Empty file lists are false-ish
        raise RuntimeError("No slurm files were found!")
    # Slurm files are formatted as thus:
    #   - Header (job info)
    #   - stdout
    #   - Bunch of "========"
    #   - Finishes with epilogue script, which always has same format (i.e. CPU time used always in same place)
    # So: hacky 'read from end' onto correct line
    cpu_time = 0
    for f_name in tqdm(file_list):
        # Generator to read in reverse
        reverse_generator = reverse_readline(f_name)
        line_found = False
        # Iterate through lines, look for desired line. There are two desired types, so check for both. E.g.:
        # CPU Utilized: 43-23:03:01
        # OR
        # Elapsed tme : 00:00:08 (Timelimit=2-00:00:00)
        for line in reverse_generator:
            if "CPU Utilized:" in line:
                line_found = True
                time_string = line.split(':')[1:]
                # Did we do more than one day?
                if "-" in time_string[0]:
                    days, hours = time_string[0].split("-")
                    minutes, seconds = time_string[1:]
                    cpu_time += int(days)*86400 + int(hours)*3600 + int(minutes)*60 + int(seconds)
                else:
                    hours, minutes, seconds = time_string
                    cpu_time += int(hours)*3600 + int(minutes)*60 + int(seconds)
                # Found line, move onto next file
                break
            elif "Elapsed time :" in line:
                line_found = True
                time_string = line.split(':')[1:] # Move to e.g. [00, 00, 08 (Timelimit=2-00), 00]
                if '-' in time_string[0]:
                    days, hours = time_string[0].split('-')
                    minutes = time_string[1]
                    seconds = time_string[2].split('(')[0]
                    cpu_time += int( days ) * 86400 + int(hours) * 3600 + int(minutes) * 60 + int(seconds)
                else:
                    hours = time_string[0]
                    minutes = time_string[1]
                    seconds = time_string[2].split('(')[0]
                    cpu_time += int(hours)*3600 + int(minutes)*60 + int(seconds)
                break
        if not line_found:
            SKIPPED_FILES += 1
    return cpu_time


def main():
    
    path_prefix = input("Enter path to slurm files [Enter for ./]: ")
    if not path_prefix: # Empty strings are false-ish
        cpu_time = get_cpu_time()
    else:
        cpu_time= get_cpu_time(path_prefix)
    print(f"Unfortunately, {SKIPPED_FILES} files could not be decoded.")
    print(f"You have used {cpu_time} seconds of CPU time. This is {cpu_time / 3600: .2f} hours, or {cpu_time / 86400: .2f} days, or {cpu_time / (86400 * 365.26): .2f} years of continuous computation time.")
    print(f"Your carbon footprint is therefore {cpu_time / 3600 * XEON_POWER_LOAD * CO2_PER_KWH:.2f} tonnes!")
    print(f"This is {cpu_time / 3600 * XEON_POWER_LOAD * CO2_PER_KWH / 24:.2f} family cars, or {cpu_time / 3600 * XEON_POWER_LOAD * CO2_PER_KWH / 40:.2f} return flights to New York!")


if __name__ == "__main__":
    main()

