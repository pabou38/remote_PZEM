
####################################
# generic wifi module
####################################

# Brownout detector was triggered

# https://docs.micropython.org/en/latest/library/network.html
# https://docs.micropython.org/en/latest/library/network.WLAN.html


from time import localtime, mktime, sleep, sleep_ms, time

import ntptime #  from https://github.com/micropython/micropython-lib/tree/master/micropython/net
import ubinascii # conversions between binary data and various encodings of it in ASCII form
# hex and base64
  
import network
import mynet

import machine
from micropython import const

#####################################################
# start wifi
# connect to ONE ssid
# own_ip None or str
# returns (wifi, ssid) or (None, None)
# const for max retry and wait between retry
# called by module trying all ssid
#####################################################

def one_wifi_connect(own_ip, ssid, psk):

  _max_retry = const(25)
  _between_retry_ms = const(1000)

  # own_ip not None, use as static

  i =0
  ok = True
  sta_if = network.WLAN(network.STA_IF)
  
  wlan_mac = sta_if.config('mac') # bytes
  # You're not getting back a hexadecimal string, you're getting a byte string. So if the MAC address contains the value 7A, 
  # then the byte string will contain z (which has ASCII value 122 (hex 7A)).
  #print("own MAC Address (bytes):", wlan_mac)  # Show MAC for peering
  # own MAC Address: b'\x8c\xaa\xb5\x85\xecT'

  mac = ubinascii.hexlify(wlan_mac, ':').decode()
  # Convert binary data to hexadecimal representation. Returns bytes string.
  print("own MAC Address :", mac)

  # set wifi interface active
  ######################
  ###### WTF.  wemos d32 on lipo_deep_sleep PCB. disconnect serial ?  seems can just reconnect serial using vscode/pymakr
  ######################
  sta_if.active(True)

  print("sta active ", sta_if.active())
  if not sta_if.active():
      raise Exception("sta if should be active")
  
  if own_ip is not None:
    print('set static IP: %s. CHECK IP of ROUTER' %own_ip)
    sta_if.ifconfig((own_ip, '255.255.255.0','192.168.1.1', '8.8.8.8'))

  else:
    print("use DHCP")

  print("sta active. connecting... ")
  sta_if.connect(ssid, psk)

  while not sta_if.isconnected():

    if not sta_if.active():
      raise Exception("sta if should be active while connecting")
    
    sleep_ms(_between_retry_ms)
    i = i + 1
    print(".", end='')
    if i >=_max_retry:
      ok=False
      break # cannot connect after too many tries
    else:
      pass # try again
        
  if ok == True: 
    sleep_ms(10)  

    # https://mpython.readthedocs.io/en/latest/library/micropython/network.html
    # ESP32 code 

    s = {1000 : "STAT_IDLE", 1001:"STAT_CONNECTING", 202:"STAT_WRONG_PASSWORD",201:"STAT_NO_AP_FOUND",1010: "STAT_GOT_IP", 203:"STAT_ASSOC_FAIL", 200:"STAT_BEACON_TIMEOUT", 204:"STAT_HANDSHAKE_TIMEOUT"}
    
    print('\n====> connected. network config:', sta_if.ifconfig())
    try:
      print ('link status: ', s[sta_if.status()]) # 1010 on ESP32 ?
    except:
      print ('link status: ', sta_if.status()) # no param, link status

    print('ssid: ', ssid)
    print('rssi ', sta_if.status('rssi')) # no []
    return (sta_if, ssid) 
    
  else:
    print('\n!!cannot connect to %s' %(ssid))
    sta_if.disconnect() # E (8652) wifi:sta is connecting, return error
    return(None, None)
  
# return None or sta_id


###############################################
# start wifi
# try ALL configured ssid

# credential for wifi stored in mynet.py
# update time with ntp
# can feed a dog

"""
net = [
['ssid1', 'pass1'] , \
['ssid2', 'pass2'] \
]
"""
# return wifi, ssid or None, None
###############################################


def start_wifi(own_ip=None, wdt=None):

  wifi_ok = False


  print("start wifi. tries all configured ssid")
  print("wifi config:", mynet.net)
  print("own ip: ", own_ip)

  ### try all possible ssid

  for i in range(len(mynet.net)):

    # WDT
    if wdt is not None:
      wdt.feed()

    print("\ntrying to connect to wifi %s ..." %(mynet.net[i][0]))
    print("passwd: %s" %(mynet.net[i][1]))

    # try one ssid
    wifi, ssid = one_wifi_connect(own_ip, mynet.net[i][0], mynet.net[i][1])

    if wifi != None:
      (ip, _,_,_) = wifi.ifconfig()
      print('\n******** wifi connected to %s. local IP: %s *********\n' %(ssid, ip))
      wifi_ok = True
      break
    else:
      print("cannot connect to %s. try next" %(mynet.net[i][0]))


  # loop breaked if success or exaust
  if (wifi_ok == False):
    print('could not connect to any wifi')
    return(None, None)
    
  else:
    ##################################
    # set local time from ntp server. 
    ##################################

    # https://bhave.sh/micropython-ntp/
    # https://github.com/micropython/micropython-lib/blob/master/micropython/net/ntptime/ntptime.py
    print('RTC time before ntp: ', localtime())  # RTC sec to tuple

    for i in range(4): # retry in case of TIMEOUT

      try: # protect from timeout in ntp
        print('set RTC UTC from ntp')

        ntptime.host = 'fr.pool.ntp.org'
        ntptime.timeout = 4
        ntptime.settime()  # set RTC with UTC

      except Exception as e:
        print('exception npt: ', str(e))
        sleep(2)

      else: # no exceptions

        # micropython utime
        # MicroPython counts time since 1st Jan 2000 instead of 1st Jan 1970
        # time.time() Returns the number of seconds, as an integer, since the Epoch
        # localtime(sec), gmtime(sec)  sec/RTC -> str
        # Convert the time secs expressed in seconds since the Epoch (see above) into an 8-tuple
        # if secs is not provided or None, then the current time from the RTC is used.
        # (year, month, mday, hour, minute, second, weekday, yearday) 
        # weekday is 0-6 for Mon-Sun yearday is 1-366
        # time.mktime() This is inverse function of localtime.  str -> sec


        # micropython RTC
        # RTC.datetime([datetimetuple]) Get or set the date and time of the RTC.
        # 8-tuple (year, month, day, weekday, hours, minutes, seconds, subseconds)
        # RTC.now() Get get the current datetime tuple.
        # RTC.init(datetime) Initialise the RTC. Datetime is a tuple of the form:
        #(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])

        (year, month, mday, hour, minute, second, weekday, yearday) = localtime() # get from RTC
        print('RTC time after ntp (UTC/GMT): ', localtime()) # tuple (year, month, mday, hour, minute, second, weekday, yearday)

        # get UTC RTC in sec 
        sec=mktime(localtime()) #  convert into sec from year 2000
        sec1 = time() # sec from year 2000 , should be equal to sec

        sec = sec + 2*3600 # add to sec,  1 or 2 depending on daylight saving

        # this returns a tuple; does not adjust RTC
        # handle all wrap around
        (year, month, mday, hour, minute, second, weekday, yearday) = localtime(sec)
        print('local time after adding 2h TZ: ', localtime(sec)) # localtime can take an arg , sec 

        try:
          # set RTC to time with timezone
          # machine.RTC().datetime(tuple)  
          rtc = machine.RTC()

          print("set RTC time")
          rtc.datetime((year, month, mday, weekday, hour, minute, second, 0) ) # tuple
          #print('rtc now', rtc.now()) # exception setting RTC time 'RTC' object has no attribute 'now'

          print('rtc: ', localtime())

        except Exception as e:
          print('exception setting RTC time', str(e))

        break # from from i in range

  return (wifi, ssid)


#####################
# to unit test
# includes below in main.py
"""
print("unit test wifi")
import sys
sys.path.append("/my_modules")
import my_wifi
my.wifi.unit_test_wifi()
my.wifi.unit_test_wifi("192.168.1.177")
"""
#####################

def unit_test_wifi(own_ip=None):
  
  print('unit test. start wifi. own_ip %s' %own_ip)

  from machine import reset

  wifi, ssid = start_wifi(own_ip=own_ip)

  if wifi == None:
    print('unit test: cannot start wifi')
    return(None)

  else:
    print("unit test: connected to %s" %ssid)
    print('rssi ', wifi.status('rssi')) # no []
    return(wifi)
      

if __name__ == "__main__":

  ####################################
  # copy below to main.py to run as unit test
  ####################################
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

