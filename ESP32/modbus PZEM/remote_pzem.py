
##################################################
# remote PZEM
###################################################

# for eddi (wemos D32 on lipo PCB) 
# and victron AC IN (nodeMCU on relay PCB)

# NOTE: cannot use uname() to distingish wemos d32 from nodemmcu
# NOTE: relay PCB has led (green for wifi, yellow for connected to python client)

################
# OLED 128x64. 64, ie 6,4 lines
    
# BEFORE wifi:
# line 0: app or error modbus/wifi or initial volt read (time stamp)
# line 1: modbus stat or error modbus/wifi or initial volt read (value)

# AFTER wifi:
# line 0: ssid ()
# line 1: current time stamp (mn) (periodic read w/ thread)
# line 2: counter and current modbus power value (periodic read)
# line 3: socket status (connected, accept, errot)
# line 4: time stamp (mn) last python client read 
# line 5: last value sent to python client
################


version = "1.31"
version = 1.53  # use float
# PCB, nodemcu/relay and wemos d32/lipo


# PCB fix for wemos d32/lipo
# pzem 5v on 8266 header (jumper wire from D32 vusb). 
# pzem gnd from gnd on serial header 
# oled gnd provided by connecting grove gnd (connected to oled gnd) to actual gnd on top 4 pins (upper right)
# PCB error, wemos D32 SDA not connected to peripheral SDA, but esp82266 SDA is, so jumper wire to D32 GPIO1 header (D13)

app = "PZEM" # short to display version on same line

server_port = 5000
#own_ip=None  # dhcp


pcb = "relay"

if pcb == "relay":

    ##############################
    # nodeMCU  victron ACIN, PCB
    ##############################

    #os.uname() (sysname='esp32', nodename='esp32', release='1.21.0', version='v1.21.0 on 2023-10-05', machine='Generic ESP32 module with ESP32')

    own_ip="192.168.1.176" # static
    gpio_sda = 21
    gpio_scl = 22
    gpio_reset = None # for Wemos s2 pico

    # uart
    gpio_rx = 16  # rx2,  gx in2
    gpio_tx = 4 # gx in1

    # led. use None if not available
    gpio_led_g = 17 # tx2, aux in2
    gpio_led_y = 5 # aux in1

if pcb == "lipo":

    ###################
    # Wemos d32 eddi
    ###################
    #os.uname() (sysname='esp32', nodename='esp32', release='1.21.0', version='v1.21.0 on 2023-10-05', machine='Generic ESP32 module with ESP32')

    own_ip="192.168.1.177" # static
    gpio_sda = 13 # PCB error, wemos SDA not connected to SDA, but esp82266 header is, so jumper wire to D32 GPIO1 header (D13)
    gpio_scl = 22
    gpio_reset = None # only for Wemos s2 pico

    # uart
    # do not use tx0 rx0, conflict with repl ?
    gpio_rx = 27  # GPIO 1 header on PCB
    gpio_tx = 26

    # led. use None if not available
    gpio_led_g = None
    gpio_led_y = None


from utime import ticks_ms, ticks_diff
start_time=ticks_ms() # note t=time() is in seconds. to measure execution time

print('\n\n=== remote PZEM 004T modbus micropython. version %0.2f. ===\n' %(version))


#pzem red led on AC side  = AC
#red led on tx/rx side = 5v supplied by microcontroler. present even if AC Off. need 5V and rx connected WTF. lit even if gnd not connected
#seems actually rx led red led when tx and rx


import gc
import os
import sys

from utime import sleep_ms, sleep, sleep_us, localtime, gmtime, mktime
from machine import Pin, RTC, I2C, ADC, reset, Timer, DEEPSLEEP, deepsleep, reset_cause, DEEPSLEEP_RESET, PWRON_RESET, HARD_RESET  
from machine import UART

import socket
import json

import _thread


# Installing is easy - just copy the modbus folder to your MicroPython board. It can live either in the root, or in a /lib folder.
import modbus # a directory under /. contains init.py
import modbus.defines as cst # modbus/defines.py
from modbus import modbus_rtu # modbus/modbus_rtu.py  (rtu is async version , vs tcp)

#import struct
# converting between strings of bytes and native Python data types such as numbers and strings.
# format specifiers made up of characters representing the type of the data and optional count and endian-ness indicators

"""
endianness = [
    ('@', 'native, native'),
    ('=', 'native, standard'),
    ('<', 'little-endian'),
    ('>', 'big-endian'),
    ('!', 'network'),
    ]
"""

# http://pymotw.com/2/struct/
# s = struct.Struct('I 2s f')    to pack unsigned Integer (4 bytes), 2char,  float (4 bytes)
# https://docs.python.org/2.7/library/struct.html#format-characters   for ALL format
# h short 2 bytes  <h little indian


import binascii
# binascii.hexlify to print as hex ascii  binascii.hexlify(packed_data) 0100000061620000cdcc2c40
# packed_data = binascii.unhexlify('0100000061620000cdcc2c40')


##############
# import
##############

# add with append or insert 
# name of dir in ESP32 file system
# this name exists on Windows file system (in micropython project directory)
# and is symlinked to HOME/Blynk/Blynk_client and HOME/micropython/"my modules" in Windows file system
# those dir are expected to be downloaded  (eg pymakr sync project) to ESP32 to /
# ESP32 file system
sys.path.append("/my_modules")
sys.path.insert(1,"/Blynk")
print("updated import path: ", sys.path)


import secret # application agnostic, in my_modules
#import my_sensors



##############
# logging
##############
import my_log

log = my_log.get_log(app, level = "debug")
log.info ("logger created")

######################
# GPIO
######################



######################
# Pin
######################

if gpio_led_g is not None:
    led_g = Pin(gpio_led_g, Pin.OUT, value=0)
else:
    led_g = None

if gpio_led_y is not None:
    led_y = Pin(gpio_led_y, Pin.OUT, value=0)
else:
    led_y = None

# generic, can be used on PCB where no led exists. will do nothin
# expect Pin object
def set_led(led, s):
    if led is not None:
        if s == "on":
            led.on()
        if s == "off":
            led.off()
    else:
        pass

set_led(led_y, "off")
set_led(led_g, "off")


# pulse both led at start
set_led(led_g, "on")
set_led(led_y, "on")
sleep(1)
set_led(led_g, "off")
set_led(led_y, "off")

###############################
# list of Pin object, not gpio number
###############################

# will be set to low at deep sleep
pin_to_power_down = []

# configure (from output) to input mode with no pull resistor, ie floating to minimize consumption ?
pin_to_input = []

# disable pull for input pins. assumes decreases consumption
pull_to_disable = []


##############
# intro
##############
import deep_sleep
deep_sleep.print_reset_cause()
import intro

##############
# webrepl
##############
import my_webrepl


############
# ADC
#############
#import my_adc_esp32
#vbat = my_adc_esp32.esp32_adc()
#print('read vbat with adc: %0.2f' %vbat)

############
# RTC
############
#import my_RTC

#r = my_RTC.init_RTC([1,1,0,0,0])
#print("RTC: temp state, lipo state, temp error counter, lipo error counter, watchdog popped counter")


##############
# I2c
###############
import my_i2c
port = 0
i2c = my_i2c.create_i2c(port, gpio_scl= gpio_scl, gpio_sda= gpio_sda)

if i2c is None:
    print("no i2c devices detected")

    ###### do not reset. let the system runs without oled.
    #sleep(10)
    #reset() 
else:
    print("i2c created AND device(s) detected")

import my_ssd1306

W= 128
H= 64

if i2c is not None:

    oled = my_ssd1306.create_ssd1306(W,H,i2c)
    sleep(1)

    if oled is None:
        """
        print("cannot create oled. reset")
        sleep(10)
        reset()
        """
        print("cannot create oled. keep going")
    else:
        print("oled created")

else:
    print("do not create oled, as i2c is no there. continue anyway")
    oled = None
    # app cope with oled == None

    """
    print("testing oled")
    my_ssd1306.lines_oled(oled, ["line 1", "line 2", "line 3", "line 4", "line 5", "line 6", "line7"])
    sleep(5)

    for n in range(8):
        my_ssd1306.line_oled(oled, n, "over %d over" %n)
        sleep(2)

    sys.exit(1)
    """

# greating message. multiple lines
my_ssd1306.lines_oled(oled, ["%s %0.2f" %(app, version), "starting"])
sleep(0.5)

#############
# wifi
# WTF connecting to wifi disconnect REPL on wemos d32 (v1.20 and v.1.21). ok with nodemcu
#############

def create_uart(nb, tx, rx):
    print('create uart %d. tx: %d, rx %d' %(nb, tx, rx))

    # ESP32 legacy
    # UART 2 @ ESP32. rx 16, tx 17
    # UART0 is used by REPL. vscode'
    # uart1 tx gpio10 rx gpio9  may not be exposed, used by flash
    # https://www.engineersgarage.com/micropython-esp8266-esp32-uart/

    # ESP32 C3
    # uart 0: firmware and log rx=20, tx=21
    # uart 1; "AT" rx= 6, tx=7
    """
    MicroPython allows multiplexing any GPIO with the hardware UARTs of ESP32. 
    Therefore, irrespective of which default pins are exposed or not, all three UARTs can be used in a MicroPython script. 
    While instantiating a UART object for ESP32, the Rx and Tx pins should also be passed as arguments.
    """
   
    uart = UART(nb, 9600, bits=8, parity=None, stop=1, timeout=1000, timeout_char=50,
        tx=tx, rx=rx, flow =0, invert=0) # invert tx not ok
        # invert = 0 invert=UART.INV_TX. default idle = high
        # parity: 0 even

    print("uart:" , uart)
    return(uart)


####################
# PZEM functions
####################

def create_modbus_master(uart):
#master = modbus_rtu.RtuMaster(uart, serial_prep_cb=serial_prep) # in example, toggle cts

    print("create modbus")
    try:
        master = modbus_rtu.RtuMaster(uart)
        print('RTU master created')
        return(master)
    except Exception as e:
        log.critical("cannot create RTU master %s" %str(e))
        print('exception: cannot create RTU master ', str(e))
        return(None)

# Usage is the same as for modbus-tk, meaning that aside from initialisation any Python script written for modbus-tk should work with micropython-modbus.
# 'execute' returns tuple of int , one or 2 int

# volt address 0, 1 word 01 04 00 00 00 01 CRC  register start at 0 , 1 word
# amps address 1 , 2 word
# power adress 3, 2 word

# return None for error

def get_volt(master, nb_retry=5):

    for i in range(nb_retry):
        try:
            # slave address 1, read starts at register 0, read 1 words  1LSB = 0.1v
            volt = master.execute(1, cst.READ_INPUT_REGISTERS, 0x00, 1) # (2323,) <class 'tuple'>  int
            
            volt = volt[0]/10.0
            return (volt)

        except Exception as e:

            print('exception read input register: ', i, str(e))
            i = i + 1
            sleep(1)  # observe 2sec in salea between try. 

    print("cannot read modbus after %d tries" %i)
    log.critical("exception: cannot read modbus")
    return(None)

    # 01 04 00 00 00 01 CRC  register start at 0 , 1 word
    # 01 04 02 09 09 CRC 0x0909 = 2313   231.1v

def get_amps(master, nb_retry=5):

    # 01 04 00 01 00 02 CRC    register start from 1 , 2 words
    # 25 ms
    # 01 04 04 00 15 00 00 CRC   0x15  = 21   returns 4 bytes
    #amps low ma:  21   amp high ma:  0

    for i in range(nb_retry):

        try:
            # reg address 0x01 (low 16 bit) and 0x02 (high 16 bits)
            # 1LSB = 1 ma
            f_word_pair = master.execute(1, cst.READ_INPUT_REGISTERS, 0x01, 2)
            
            amp_low = f_word_pair[0] # low 16 bits   65536 ma = 65 amps. max read for me. can safely disgard high 16 bits 
            amp_high = f_word_pair[1] # high 16 bits, to create 32 bit integer (representing ma)

            assert (amp_high == 0)

            amps = amp_low /1000.0 # assume same indianess
            return(amps)

        except Exception as e:
            print('exception read input register: ', str(e))
            i = i + 1
            sleep(1)

    print("cannot read modbus after %d tries" %i)
    log.critical("exception cannot read modbus %s" %str(e))
    return (None)

def get_power(master, nb_retry=5):

    for i in range(nb_retry):

        try:

            # reg address 0x01 (low 16 bit) and 0x02 (high 16 bits) 
            # 1LSB = 0.1W
            f_word_pair = master.execute(1, cst.READ_INPUT_REGISTERS, 0x03, 2) 
            
            pow_low = f_word_pair[0] # low 16 bits   
            pow_high = f_word_pair[1] # high 16 bits, to create 32 bit integer (representing 0.1W)
        
            power = pow_high * 2 **16 + pow_low
            # Re-pack the pair of words into a single byte, then un-pack into a float
            #<h short 2 bytes , little indian
            # val = struct.unpack('<f', struct.pack('<h', int(f_word_pair[1])) + struct.pack('<h', int(f_word_pair[0])))[0]

            power = power /10.0 # assume same indianess
            return(power)

        except Exception as e:
            print('exception MODBUS read input register: ', str(e))
            i = i + 1
            sleep(1)

    print("cannot read modbus after %d tries" %i)
    log.error("cannot read modbus after %d tries" %i)

    return (None)


# returns None on error
def get_func(value:str):
    if value == "power":
        return(get_power)
    elif value == "amps":
        return(get_amps)
    elif value == "volt":
        return(get_volt)
    else:
        raise Exception("unknown PZEM command")
            

##########################
# MAIN
##########################


##### create UART
    
# define tx and rx pins

# The ESP32-C3 chip has 2 UART controllers
# c3 using uart0 generates error (used by WEPL ?)
if os.uname().machine in ['ESP32C3 module with ESP32C3']:
    # _ = Pin(21,Pin.OUT, drive=Pin.DRIVE_0, value=0)
    # AI C3 dual usb ESP32-C3-mini-1
    #tx = 21; rx=20  # U0TXD, U0RXD, exposed  do no use those ? used by console and/or webrepl
    # use available pin
    tx = 7; rx = 6
    unit = 1 

# The ESP32-S2 chip has 2 UART controllers 
elif os.uname().machine in ['LOLIN_S2_PICO with ESP32-S2FN4R2']:
    # S2 pico U0RXD 44, UOTXD 43, but not exposed to headers
    # D+ 20, D- 19, connected to USB C connector
    # use available pin
    tx = 37; rx = 38
    unit = 1

else:
    # Esp32 dev kit , 3 uart
    # The ESP32-S3 chip has 3 UART controllers 
    # use default pin TX2, RX2
    tx = gpio_tx; rx = gpio_rx
    unit = 2 # could use unit 1 ?


uart = create_uart(unit, tx=tx, rx=rx)

""" 
# test uart in loopback
# with firmware c3 with usb
# ok pin labeled tx and rx, can see tx  and rx led flashing
# PC USB C cable on "usb" connected, not the CH340 
if os.uname().machine in ['ESP32C3 module with ESP32C3']:
    # test uart
    while True:
        uart.write('test uart')
        print(uart.read())
"""

#######################
# create modbus
#######################
master = create_modbus_master(uart)
if master is None:

    #############
    # error modbus, reset
    ##############
    d = 5
    my_ssd1306.lines_oled(oled,["Modbus error", "reset in", "%d sec" %d])
    log.error("modbus error. reset in %d sec" %d)
    sleep(d)
    reset()

else:

    my_ssd1306.line_oled(oled, 1, "Modbus created")


################
# read PZEM at start to make sure it is OK
# display line 1 and 2, will be overwritten by periodic read thread
# reset in case of error
# wifi not created, so ntp not updated
################
volt = get_volt(master)

if volt is None:
    d=5
    my_ssd1306.lines_oled(oled,["volt error", "reset in", "%d sec" %d])
    log.error("cannot read volt. reset in %d sec" %d)
    sleep(d)
    reset()

else:

    #my_ssd1306.line_oled(oled, 1, my_log.get_stamp())
    my_ssd1306.line_oled(oled, 1, "test modbus") # ntp not yet updated
    my_ssd1306.line_oled(oled, 2, "%0.0f volt" %volt) 
    print("modbus OK. volt %0.1f" %volt)
    sleep(2) # time to read


# concurent access: remote pzem and local thread
lock = _thread.allocate_lock()


#################
# read power and display on oled (with timestamp)
# used to make sure micropython app is running
# run as thread 
# line 1: time stamp
# line 2: incrementing counter and power value
##################


def periodic_power(master, sleep_time):

    counter = 0
 
    # read power
    # manage mutex
    # write to OLED
    # manage counter to see thread running (on top of time stamp)
    # sleep

    while True:

        print("periodic power read %d" %counter)

        # lock.acquire(waitflag=1, timeout=-1)
        lock.acquire()
        power = get_power(master, nb_retry=5)
        lock.release()
        
        counter = counter + 1
        if counter == 10000:
            counter = 0
                
        my_ssd1306.line_oled(oled, 1, my_log.get_stamp())

        if power is not None:
            my_ssd1306.line_oled(oled, 2, "#%d: %0.0fW" %(counter, power))
        else:
            my_ssd1306.line_oled(oled, 2, "#%d: power error" %counter)
            
        sleep(sleep_time)



##########################
# start wifi
# move to after testing pzem. 
##########################

import my_wifi

print('start wifi')

my_ssd1306.line_oled(oled, 0, "wifi connect..")

set_led(led_g, "off") # green led lit when wifi is OK

wifi, ssid = my_wifi.start_wifi(own_ip=own_ip)
if wifi is None:
    d = 30
    print('cannot start wifi. reset in a %d sec' %d)
    my_ssd1306.lines_oled(oled, ["wifi error", "reset in", "%d sec" %d])
    
    del(wifi)
    sleep(d)
    reset()

else:
    print("wifi ok", ssid)
    #my_ssd1306.lines_oled(oled, [ssid, "wifi ok"])
    my_ssd1306.line_oled(oled, 0 ,ssid) # line 0 keeps displaying ssid during operation

    # use green led to say wifi ok
    set_led(led_g, "on")


# start after wifi to get ntp to update localtime
p = 60
print("start periodic power read thread with period %d sec" %p)
_thread.start_new_thread(periodic_power, (master, p))

##########################
# socket
##########################

# https://realpython.com/python-sockets/
sock = socket.socket()

### try to bind FOREVER
while True:
    try:
        sock.bind(("", server_port ))
        s = "socket bound on %d" %server_port
        print(s)
        log.info(s)
        break
    except Exception as e:
        print("exception binding ", str(e))
        sleep(10)


sock.listen()

#####################
# endless loop waiting for connection
# green led used for wifi
# yellow led used for connected to client
#####################

while True:

    print("waiting for socket connection ....")
    log.info("socket accepting")
    my_ssd1306.line_oled(oled, 3, "accept") # line 3 is socket status
    set_led(led_y, "off")

    con , addr = sock.accept()

    print("socket connected to ", addr)
    log.info("socket connected")
    my_ssd1306.line_oled(oled, 3, "connected")
    set_led(led_y, "on") # yellow led = socket connected


    #####################
    # endless loop receiving data and processing data
    #####################

    while True:

        # block waiting for data. can it creates hang ? ie client cannot connect ?
        try:
            data = con.recv(32) # The bufsize argument is the maximum amount

        except Exception as e:
            s= "exception recv socket %s" %str(e)

            # exception recv socket [Errno 104] ECONNRESET when aborting client
            print(s)
            log.error(s)
            #my_ssd1306.lines_oled(oled,["recv excp", "break"])
            # do not overwrite lines above (ssid, periodic read)
            my_ssd1306.line_oled(oled,3, "recv excpt") # almost impossible to read, overwritten by accept
            
            break # exit loop recv data. clean up done after break

        if not data:  # returns an empty bytes object, b'', that signals that the client closed the connection
            s= "data empty. socket closed by client"

            print(s)
            log.error(s)
            my_ssd1306.line_oled(oled,3, "sock closed") # almost impossible to read, overwritten by accept
            #my_ssd1306.lines_oled(oled,["socket", "closed", "by client", "break"])
            break # exit loop recv data


        """
        The .send() method also behaves this way. It returns the number of bytes sent, which may be less than the size of the data passed in. 
        You’re responsible for checking this and calling .send() as many times as needed to send all of the data:
        Unlike send(), this method continues to send data from bytes until either all data has been sent or an error occurs. 
        None is returned on success.”
        """

        # got payload
        s = data.decode('utf-8') # bytes to str
        payload = json.loads(s) # str to dict

        # "data" is a str "power", "amps" or "volt"
        print("\nreceived " , payload, payload.keys()) # dict # received  {'nb_retry': 2, 'data': 'volt'} dict_keys(['nb_retry', 'data'])
        x = payload["data"]  # value being asked

        #########################
        # call PZEM
        # protected by mutex
        #########################

        lock.acquire()
        value = get_func(x) (master, nb_retry=payload["nb_retry"])
        lock.release()

        # received from socket b'{"value": 0.0, "data": "power"}' 

        if value == None:   # local PZEM error
            v = "None" # to signal to client that the error is on the server (ESP32) side
        else:
            #v = "%0.1f" %value # send as str
            v = value # send as float

        #########################
        # write status to oled at each request from python client
        #########################

        # def line_oled(oled, line_nb, s): # line number starts at 0
        
        my_ssd1306.line_oled(oled,4, my_log.get_stamp())
        my_ssd1306.line_oled(oled,5, str(v)+"W") # 0.0, as received in json

        ###########################
        # send back result
        # returned as "value"
        ###########################
        resp = {"data": x , "value": v}
        payload = json.dumps(resp)
        payload = bytes(payload, "utf-8")

        #payload = bytes(payload, encoding="utf-8") # NotImplementedError: keyword argument(s) not implemented - use normal args instead

        print("sending response:", payload) # sending  b'{"value": 240.1, "data": "volt"}'

        if con.sendall(payload) != None:
            s= "error sending response"
            print(s)
            log.error(s)
            my_ssd1306.lines_oled(oled,["error send", "resp"])
            break

    # while true read data
    # endless loop receiving data


    ###############
    # break from loop receiving data.
    # close socket and start again accepting inbound connection
    ###############

    s = "break from endless recv loop. close socket and go back to accept"
    log.error(s)
    print(s)

    try:
        con.close()  # because of break. will go to accept again
    except:
        pass

    set_led(led_y, "off")

    # if connection closed by client or exception, go back to accept
    # con (data connection) is closed. sock is still in listen mode
    
    #### IDIOT. do not break here
    # vscode detect code below is unreachable
    # if I add break, it becomes reachabledd