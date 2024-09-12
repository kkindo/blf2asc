import os
import datetime
import argparse
import pathlib
import glob
from to_asc import to_asc
import sys

# Get the argment
def get_arg():
    usage = 'blf2asc.exe path [--filter] [--help]'
    description = "Convert blf file to asc file."
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument('path', type=pathlib.Path, help="Input filepath or folderpath")
    parser.add_argument('--filter', action='store_true', required=False, help="Input filter configuration file path")
    args = parser.parse_args()
    return args

# Get frame filter configuration
def get_filtered_canids(frame_cfg_path):
    filtered_canids = []
    if not os.path.isfile(frame_cfg_path):
        raise Exception("ERROR! Frame filter config file ( %s ) was not found." % frame_cfg_path)        
    print("Read frame filter config file ( %s )" % frame_cfg_path)
    fp_frame_config = open(frame_cfg_path, "r", encoding="utf-8")
    lines = fp_frame_config.readlines()
    fp_frame_config.close()
    ignore_chrs = ['\n', ' ', '\t', ',']
    #for line_input in lines:
    for line_idx, line_input in enumerate(lines):
        line = line_input
        for ignore_chr in ignore_chrs:
            line = line.replace(ignore_chr, '')            
        comment_pos = line.find('//')
        #print(comment_pos)
        if(comment_pos == 0):
            continue
        elif(comment_pos == -1):
            frame_id_hex = line
        else:
            frame_id_hex = line[0:comment_pos]                
        #print("hex_string is %s" % frame_id_hex)
        if frame_id_hex !='':
            id_hex_error = False
            try:            
                #print("%0x %d" % (int(frame_id_hex, 16) ,int(frame_id_hex, 16) ) )
                filtered_canids.append(int(frame_id_hex, 16))
            except Exception as e:
                #print("%s is not hex value" % frame_id_hex)
                #print(e)
                print("ERROR! Invalid character detected in line %d : %s" % (line_idx +1, line_input))
                id_hex_error = True
            if (id_hex_error == True):
                raise Exception("Could not start the process because of incorrect filter definition.")
    print("Filter set : ", end = "")
    for frame_id in filtered_canids:
        print("%3X, "  % frame_id , end = "")
    print("\b\b \n")
    #print (filtered_canids)
    return filtered_canids
    
def main():
    #sys.tracebacklimit = 0
    exe_filepath = os.path.abspath(sys.argv[0])
    exe_dir = os.path.dirname(exe_filepath)
    # Get the argment
    args = get_arg()
    # Get input path
    input_path = args.path
    input_path = str(input_path)
    blf_filepaths = []
    asc_filepaths = []
    canlog_filepaths = []
    output_dir = ""
    if os.path.isdir(input_path):
        blf_filepaths = glob.glob(input_path + '/**/*.blf', recursive=True) # retrieve input file names, recursively
        asc_filepaths = glob.glob(input_path + '/**/*.asc', recursive=True) # retrieve input file names, recursively
        canlog_filepaths = blf_filepaths + asc_filepaths
        if canlog_filepaths == []:
            raise Exception("ERROR! Input log file(s) was not found.")
        output_dir = input_path
    elif os.path.isfile(input_path):
        if input_path[-4:] == '.blf':
            blf_filepaths = [input_path]
        elif input_path[-4:] == '.asc':
            asc_filepaths = [input_path]
        else:
            raise Exception("ERROR! Input file extension is not supported.")
        canlog_filepaths = blf_filepaths + asc_filepaths
        output_dir = os.path.dirname(input_path)
    else:
        raise Exception(f"ERROR : input path ( {input_path} ) was not found.")
    #output_dir = os.getcwd()
    #output_dir = output_dir + "\\" + 'output_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    #os.makedirs(output_dir)
    print(f"Outputting to directory : {output_dir}")
    # Get filter configuration
    if args.filter == True:
        filter_config_filepath = os.path.join(exe_dir, 'blf2asc_filter_config.txt')
        filtered_canids = get_filtered_canids(filter_config_filepath)
    else:
        filtered_canids = []
    for canlog_filepath in canlog_filepaths:
        print("")
        print("Start converting...")
        print(f"Input filepath  : {canlog_filepath}")
        start_time_one_file = datetime.datetime.now()
        to_asc(canlog_filepath, output_dir, filtered_canids)
        end_time_one_file = datetime.datetime.now()
        diff_time = str(end_time_one_file - start_time_one_file)
        hours, str_minutes, str_float_seconds = diff_time.split(':')
        minutes_sec = int(str_minutes) * 60
        float_sec = float(str_float_seconds[:6])
        print("Finished 1 file. Process time : " + str(minutes_sec + float_sec)[:6] + " sec")

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    main()
    end_time =   datetime.datetime.now()
    diff_time = str(end_time - start_time)
    hours, str_minutes, str_float_seconds = diff_time.split(':')
    minutes_sec = int(str_minutes) * 60
    float_sec = float(str_float_seconds[:6])
    print("\nFinished all files. Total process time : " + str(minutes_sec + float_sec)[:6] + " sec")
