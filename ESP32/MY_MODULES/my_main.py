
print("running main")

#print("start app from main")
#import temp

################################
# debug mode
# objective is to edit (mostly app) files and run them on esp WITHOUT having to reflash
################################

# do not import app to run it at boot

# option 1:  mpremote run remote_pzem.py
# from powershell

# edit app in vscode, save it
# then from PS: mpremote run remote_pzem.py
#    will copy new version on ESP32 RAM and run from there
#    - ALL libs need to be in ESP32 file system
#    - need both PS and REPL terminal.  
#    + can run app/unit_test multiple time

#     NOTE: look ar far rigth of VScode pane: square > is REPL, losange >_ is powershell
#     NOTE: disconnect from REPL, otherwize mpremote cannot find serial
#     NOTE: test connection with mpremote ie see if it finds a serial


# option 2: mpremote mount .
# from REPL >>> import remote_pzem
# BUT:
#  - import only works once (reload??)
#  + could also run libs from windows if not using symlinks

#  libs (everything not in .) need to be in flash (if using dir symlinks). 
#   Alternative 1: use file hard link
#   Alternative 2: temporaly copy one lib file to . (so that this version will be imported from windows), debug. but then this version need to go back to single version of thruth, MESSY ??

print("main does not run app (debug mode). use mpremote to run application")

import sys
sys.path.append("/my_modules")
print(sys.path)

print("\nGO .. DEBUG\n")