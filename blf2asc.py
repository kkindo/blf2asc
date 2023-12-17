import os
import datetime
import argparse
import glob
from to_asc import to_asc

# Get the argment
def get_arg():
    usage = 'blf2asc.exe [--filter] [--help]'
    description = 'Convert blf file to asc file (very similar format to Vector asc file)'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument( '--filter', action='store_true', help="")
    args = parser.parse_args()
    return args

# Get Configuration setting
def get_config():
    config_filename = 'blf2csv_config.txt'
    KEY1 = 'log_folderpath'
    KEY2 = 'filter_config_filepath'
    config_datas = {KEY1:'', KEY2:''}    
    print("Read config file ( %s )" % config_filename)
    if os.path.exists(config_filename):
        fp_config_file = open(config_filename, "r", encoding="utf-8")
        lines = fp_config_file.readlines()
        fp_config_file.close()
        for line in lines:
            if (line.find(',') > 0):
                parameter = line.split(',')
                #print("parameter =",parameter)
                parameter_key = parameter[0].strip()
                config_datas[parameter_key] = parameter[1].strip()
                print("%-29s = %s" %(parameter_key, config_datas[parameter_key]))
        canlog_path     = config_datas[KEY1]
        frame_cfg_path  = config_datas[KEY2]
        if canlog_path == '':
            raise Exception("ERROR : " + KEY1 + " is not input in " + config_filename)
    else:
        raise Exception("ERROR : " + config_filename + " is not found in the current directory.")
    return canlog_path, frame_cfg_path

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
    # Get the argment
    args = get_arg()
    # Get Configuration setting
    canlog_folderpath, frame_cfg_path = get_config()
    if not os.path.isdir(canlog_folderpath):
        raise Exception(f"ERROR : folderpath ( {canlog_folderpath} ) was not found.")    
    # Get filter configuration
    if args.filter == True:
        filtered_canids = get_filtered_canids(frame_cfg_path)
    else:
        filtered_canids = []
    # retrieve input file names, recursively
    blf_filepaths = glob.glob(canlog_folderpath + '/**/*.blf', recursive=True)
    asc_filepaths = glob.glob(canlog_folderpath + '/**/*.asc', recursive=True)
    canlog_file_paths = blf_filepaths + asc_filepaths
    if canlog_file_paths == []:
        raise Exception("ERROR! Input log file(s) was not found.")
    output_dir = os.getcwd()
    output_dir = output_dir + "\\" + 'output_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs(output_dir)
    print(f"Outputting to directory : {output_dir}")
    for canlog_file_path in canlog_file_paths:
        print("")
        print("Start converting...")
        print(f"Input filepath  : {canlog_file_path}")
        start_time_one_file = datetime.datetime.now()
        to_asc(canlog_file_path, output_dir, filtered_canids)
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
