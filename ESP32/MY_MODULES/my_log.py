
import logging 
from time import localtime

# from micropython-lib-master  a single logging.py vs logging dir
# https://github.com/micropython/micropython-lib/tree/master/python-stdlib/logging/examples

def get_stamp():
# set by ntp, but still UTC

  # TZ
  # localtime is RTC, always UTC.
  #t=mktime(localtime())
  #t = t + 2*3600
  #(year, month, mday, hour, minute, second, weekday, yearday) = localtime(t)

  (year, month, mday, hour, minute, second, weekday, yearday) = localtime()
  s = "%d/%d:%d" %(mday, hour, minute)
  return(s)


def get_log(app, level = "debug"):

    print("init log. app %s, level %s" %(app, level))
    if level == "debug":
        logging.basicConfig(level=logging.DEBUG) #  will display on stdout
    elif level == "info":
        logging.basicConfig(level=logging.INFO) #  will display on stdout
    elif level == "warning":
        logging.basicConfig(level=logging.WARNING) #  will display on stdout
    elif level == "error":
        logging.basicConfig(level=logging.ERROR) #  will display on stdout
    elif level == "critical":
        logging.basicConfig(level=logging.CRITICAL) #  will display on stdout
    else:
        print("%s unknown" %level)
        return(None)

    # can use logging.info
    logging.info("ecs v2 starting (using logging.info)") 
    # INFO:root:remote PZEM starting

    # or specific log.info
    log = logging.getLogger(app)
    log.info("creating logger for app %s" %app)
    # INFO:pzem:starting
    return(log)

"""
# same info, just formatted
class MyHandler(logging.Handler):
    def emit(self, record):
        print(record.__dict__)
        print("levelname=%(levelname)s name=%(name)s message=%(message)s" % record.__dict__)


logging.getLogger().addHandler(MyHandler())
logging.info("remote PZEM starting") 
# levelname=INFO name=root message=remote PZEM starting
"""

#######################
##### NOTE: also consider standard logging module

# write log into disk for futher analysis
# SHOULD NOT crash. even if file system full
# WARNING. MAKE SURE to prevent vscode pymakr from erasing it on flash (when updating) because this file does not exist on windows
######################
def to_file(s, file = "crash.txt"):

    print("appending to crash file ", s, file)

    try:
        # Note that the default mode when opening a file is to open it in read-only mode, and as a text file. Specify 'wb' as the second argument to open() to open for writing in binary mode, 
        # and 'rb' to open for reading in binary mode.
        # append mode is supported 
        # but carefull as pymakr synch project will erase crash.txt on esp, as it does not exists on windows (unless configured with pymakr.conf) 
        with open(file, "a") as f:
            f.write(s+'\n')
    except Exception as e:
        print("exception logging crash to disk. SHOULD NOT HAPPEND", str(e))

    try:
        with open(file, "r") as f:
            # if vscode delete crash.txt because does not exist on windows, this only contains log since last vscode download
            print("reading back crash file content:")
            print(f.read())

    except Exception as e:
        print("exception reading back crash file. SHOULD NOT HAPPEND", str(e))


