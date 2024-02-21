: v2.1

: : is not displayed. rem is displayed

rem for micropython

rem WARNING !!!! search for COMMAND PROMPT (not powershell) and run as admin
rem WARNING. edit cd to micropython project dir

: ==================== to use ============================
: to run cut and paste below AFTER updating cd above
: c:\Users\pboud\micropython_app\"MY_MODULES"\create_sym_links.bat
: =========================================================

: structure on windows:
: HOME/micropython_app
: HOME/Blynk


: sym link generic modules located in ../my modules (ie HOME/micropython/my modules) and ../../Blynk (ie HOME/Blynk)
: those are Windows directory
: HOME/Blynk also used for windows / python app - add to sys.path
: Home/Blynk also used on linux/raspberry


: WHY symlink for micropython ? 
: file needs to be in vscode project folder for pymakr upload (can be in any dir if this dir is included in sys.path of micropython script)
: edits when developping application will ACCUMULATE in a single (cross application) version. single version of "last version".
: WARNING: other application may need to be modified to adapt to the lastest version. necessary pain I guess

:creates sym link to point to generic micropython modules
:both my modules and Blynk
:delete before creating


cd c:\users\pboud\micropython_app

: === >WARNING cd to project directory
:eg cd "modbus PZEM"

cd "modbus PZEM"


rem deleting old symlink
rmdir my_modules
rmdir Blynk
rmdir mpy


mkdir mpy
rem copy output of mpy-cross there, and insert in sys.path BEFORE my_modules to use frozen bytecode version
rem PS C:\Users\pboud\micropython\dallas\my_modules> mpy-cross .\my_log.py
rem PS C:\Users\pboud\micropython\dallas\my_modules> mv *.mpy ../mpy


: mklink
: cannot be called from powershell.   
: COULD do cmd /c mklink ..   BUT need to sort out filename / vs \
: or just run from admin cmd


: default is soft (aka symbolink) link
: pointer, can point to void if target file deleted
: regular file AND DIR

: mklink /h
: hard link, alternate name
: only for regular file

: note /d for directory
: RD folder or DEL file

: mpremote mount .
: >>> os.listdir('/remote/mpy') = os.listdir('./mpy)   = windows file system
: >>> os.listdir('/mpy') = ESP32 file system

: BUT  (because symlink) ??
: >>> os.listdir("./Blynk")  EPERM
: >>> os.listdir("/Blynk")  ESP32

: idea is to use mpremote mount . to import LIB from windows file system (vs from ESP32 flash), allowing edit of libs without reflashing
: this does not works if lib (Blynk, my_modules) are symlink. 
: this works however for main app as it is a regular file(as . point to /remote , ie windows)

: could make it work by not creating symlink to directoty, but a  bunch of hard links to files in my_modules (using powershell scripts)
: as hard links work with mpremote mount
: PS> mklink /h ..\"modbus PZEM"\mpy\hard_created.py test_hard.py
: then on REPL with ./mpy in sys.path
: import hard_created  OK

: =========== TO DO



: 

mklink /D my_modules ..\"MY_MODULES"\

: if linking entiere Blynk, pymakr sync project will copy blynk server data, START etc ..
: Blynk\Blynk _client is the code to be imported, rest of Blynk is server
: from micropython/<app> to Blynk/Blynk_client
mklink /D Blynk ..\..\Blynk\Blynk_client


: mpy, Blynk and my_modules are windows dir, will be uploaded to ESP flash under /

:make sure /mpy, /my_modules and /Blynk are in micropython sys.path
:see above for importing from windows (development mode) using mpremote mount . and sys.path   './Blynk' , 'Blynk'. first is windows, 2nd is flash
