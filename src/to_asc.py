import os
import can

VERSION = '1.0.0'
PRINT_STEP = 0 # 1sec step
LEN_DOT_EXTENTION = 4
PROGRESS_STEP = 1
PROGRESS_BAR_LEN = 100

def to_asc(canlog_filepath, output_dir, filtered_canids):
    # Extract messages from input CAN log file
    is_asc = False
    file_extension = canlog_filepath[-LEN_DOT_EXTENTION:]
    if file_extension == '.asc':
        is_asc = True
        try:
            messages = can.io.asc.ASCReader(canlog_filepath)  # Read asc file, getting a generator object
        except Exception as e:
            print(e)
            return
        with open(canlog_filepath, "r", encoding="utf-8") as f:
            lines = f.readlines() 
            message_num = len(lines)  # Get the number of lines to calculate progress, as it's impossible to get the info from a generator object
            print("Total N of lines : %d" % message_num)
    else:
        is_asc = False
        try:
            messages = can.io.blf.BLFReader(canlog_filepath)  # Read blf file, getting a generator object
        except Exception as e:
            print(e)
            return
        #message_num = messages.object_count    # Unused, as object_count doesn't always stand for N of can frames
        #print("Total message number : %d" % message_num)
        timestamp_stop = messages.stop_timestamp 
    # Create ASC file
    _ , canlog_filename = os.path.split(canlog_filepath)
    output_filepath = os.path.join(output_dir, canlog_filename[0:-LEN_DOT_EXTENTION] + "_" + canlog_filename[-(LEN_DOT_EXTENTION - 1):] + '.asc')
    output_ascfile = can.io.asc.ASCWriter(output_filepath)
    # Preprocess for filtering
    if len(filtered_canids) > 0:
        should_filter = True
    else:
        should_filter = False
    should_write = False
    # Loop for outputting messages to asc file
    message_idx = 1
    timestamp_start = 0
    timestamp_current = 0
    last_progress = 0
    for message in messages:
        # apply filter
        if should_filter == True:
            should_write = False
            for can_id in filtered_canids:
                if can_id == message.arbitration_id:
                    should_write = True
                    break
        else:
            should_write = True
        # write to asc file
        if should_write == True:
            output_ascfile.on_message_received(message)
        # Show progressbar
        if is_asc == True:
            progress = int(((message_idx / message_num) * 100) / PROGRESS_STEP)
        else:
            if timestamp_start == 0:
                timestamp_start = message.timestamp
                timestamp_stop = timestamp_stop - timestamp_start
                int_timestamp_stop = int(timestamp_stop)
            timestamp_current = message.timestamp - timestamp_start
            int_timestamp_current = int(timestamp_current)
            progress = int(((int_timestamp_current / int_timestamp_stop) * 100) / PROGRESS_STEP)
        if progress > last_progress:
            last_progress = progress
            progressbar = ''.join([">" for _ in range(progress)])
            progressbar = progressbar + ''.join(["_" for _ in range(PROGRESS_BAR_LEN - progress)])
            print("Progress : " + progressbar + "| " + str(progress * PROGRESS_STEP).rjust(3) + " %" , end = "\r")
        message_idx += 1
    progressbar = ''.join([">" for _ in range(PROGRESS_BAR_LEN)])
    print("Progress : " + progressbar + "| 100 %", end = "\n")
    output_ascfile.stop()
    print("Output filepath : %s" % output_filepath)