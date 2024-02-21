# main.py -- put your code here!
print("\nrunning main")


######################
# deployment mode
######################
print("import app from main to run it automatically at boot")
import remote_pzem

################################
# some unit test
################################

#print("unit test PZEM")
#import pzem_unit_test

################################
# debug mode
# objective is to edit files and run them on esp WITHOUT having to reflash
################################

# do not import app to run it at boot

# option 1:  mpremote run remote_pzem.py
# from powershell

# edit app in vscode, save it
# then from PS: mpremote run remote_pzem.py
#    will copy new version on ESP32 RAM and run from there
#    - ALL libs need to be in ESP32 file system
#    - need both PS and REPL terminal
#    + can run app multiple time


# option 2: mpremote mount .
# from REPL >>> import remote_pzem
# BUT:
#  - import only works once (reload??)
#  + could also run libs from windows if not using symlinks

#  libs (everything not in .) need to be in flash (if using dir symlinks). 
#   Alternative 1: use file hard link
#   Alternative 2: temporaly copy one lib file to . (so that this version will be imported from windows), debug. but then this version need to go back to single version of thruth, MESSY ??

#print("main does not run app (debug mode). use mpremote to run application")


def test_wifi():
  print("unit test wifi running from main")
  import sys
  sys.path.append("/my_modules")
  import my_wifi

  wifi = my_wifi.unit_test_wifi()
  if wifi is not None:
    print("main: unit test successfull")
    print("disconnect")
    wifi.disconnect()
  else:
    print("main: unit test FAILED")

  #my_wifi.unit_test_wifi("192.168.1.177")


