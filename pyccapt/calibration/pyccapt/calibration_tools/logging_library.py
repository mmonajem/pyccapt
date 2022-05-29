import logging
import sys

def logger_creator(script_name,file_handler=None):
    """
    The function is used to instantiate and configure logger object for logging.
    The function use python native logging library.

    Attributes:
        Does not accept any arguments
    Returns:
        Returns the logger object which could be used log statements of following level:
            1. INFO: "Useful information"
            2. WARNING: "Something is not right"
            3. DEBUG: "A debug message"
            4. ERROR: "A Major error has happened."
            5. CRITICAL "Fatal error. Cannot continue"
    """
    log_creator = logging.getLogger(script_name)
    log_creator.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s',
                                  '%m-%d-%Y %H:%M:%S')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    log_creator.addHandler(stdout_handler)

    if file_handler is None:
        return  log_creator
    else:
        if 'path' not in file_handler or 'log_file_name' not in file_handler:
            print("Please provide the path and log_file_name in the dictionary")
        elif file_handler['log_file_name'][-4:] != '.log':
            print("Please provide log file name with .log extension")
        else:
            log_creator_file_handler = add_file_handler(log_creator,formatter,file_handler)
            return log_creator_file_handler

    

def add_file_handler(log_creator,formatter,file_handler):
    print("add_file_handler called",file_handler)
    path = file_handler['path']
    log_file_name = file_handler['log_file_name']
    file_handler_creator = logging.FileHandler(path + '/' + log_file_name)
    file_handler_creator.setLevel(logging.DEBUG)
    file_handler_creator.setFormatter(formatter)
    log_creator.addHandler(file_handler_creator)
    return log_creator

