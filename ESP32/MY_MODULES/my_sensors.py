from machine import Pin
from utime import sleep_ms


##############################################
# DS18B20 aka dallas 
# vcc 3 to 5V 
# 4.7k resistor between vcc and data
# arg is a GPIO number. Pin object created inside
# nb (of sensor) not really used
# return list
##############################################

def read_dallas(gpio, nb=2):

  import onewire, ds18x20

  print('my_sensors: read %d temp sensors on gpio %d' %(nb, gpio) ) # nb not used

  nb_try = 5
  i = 0

  dat = Pin(gpio, Pin.OUT)
  # create the onewire object
  ds = ds18x20.DS18X20(onewire.OneWire(dat))

  while True:

    try:
      roms = ds.scan() # scan for devices on the bus
      print('ds18b20 scan, found devices: ', roms)
      # no exception in no sensors found: ds18b20 scan, found devices:  []

    except Exception as e:
      print("exception scanning for devices", str(e))

    if roms != []:
      try:
        temp = []
        ds.convert_temp() 
        # Note that you must execute the convert_temp() function to initiate a temperature reading, then wait at least 750ms before reading the value.
        sleep_ms(750)
        
        for rom in roms: # read all sensors on this gpio bus
          
          #2 sensors on same bus (ie data GPIO). how do I know which one is one ? . may be better to have each sensor on a separate bus. 
          
          t = ds.read_temp(rom)
          t = round(t,1)
          #print('dallas: ', t)
          temp.append(t)
        
        print('temp array: ' , temp)

        if len(temp) != nb:
          return(temp) # handle error later
        else:
          return(temp) # which is which ? seems should be interpreted as (mid, top)

      except Exception as e:
        print('exception reading temp sensors ' , str(e))
        # try again
    
    else:
      # no rom found
      pass

    # did not return, so either scan or temp read error
    i = i + 1
    if i > nb_try:
      print("temp sensor: give up, too many errors")
      return([])
    else:
      print("temp sensor: either scan or read failed. try again")
      sleep_ms(500)
      # try again
	
	
####################################################
# read lipo gauge
#####################################################
def read_lipo_gauge(i2c, nb_retry = 5):

  # import only if needed to preserve heap (ESP8266)
  from pb_max17043 import max17043

  vcell = -1 # 
  soc = -1

  try:
    print('read lipo gauge')
    sleep_ms(300)
    """
    use modified library. create i2c object in main, and pass to library
    can use same i2c for multiple sensors
    original library had hardcoded i2c pins for pyboard
    """
    m = max17043(i2c)

    for i in range(nb_retry): # multiple read to stabilize ?
      vcell = round(m.getVCell(), 1)
      soc = round(m.getSoc(), 0)
      print(i,vcell, soc)
      if vcell > 4.3 or vcell < 2.8:
        sleep_ms(500) # assumes bad reading
      else:
         break

      # if >100, likely powered via usb
      soc = min(soc,100)

    print('Lipo vcell %0.1f, soc %0.0f: '% (vcell, soc))
    # print everything about the battery and the max17043 module
    # call the __str__ method
    #print(m)
    # restart the module
    #m.quickStart()
    # close the connection to the module
    #m.deinit()
    return(vcell, soc)

  except Exception as e:
    print('exception reading Lipo gauge ' , str(e))
    return(None,None)
	
	
def neo():
	#############
	# ws1812 
	# panic on ESP32 
	############

	# os.uname() (sysname='esp32', nodename='esp32', release='1.20.0', version='v1.20.0-124-g17c3f6b6aa on 2023-05-08', machine='LOLIN_S2_PICO with ESP32-S2FN4R2')
	# sys.platform 'esp32
	if os.uname().machine in ['ESP32C3 module with ESP32C3']:

		import neopixel

		neo_pin = Pin(8,Pin.OUT, value=0)
		neo = neopixel.NeoPixel(neo_pin,1) # default 3 RGB

		neo.fill((128,0,0))
		neo.write()
		sleep(1)
		neo.fill((0,255,0))
		neo.write()
		sleep(1)
		neo.fill((0,0,60))
		neo.write()
		sleep(1)
		neo.fill((0,0,0))
		neo.write()



if __name__ == "_main__":

  gpio_temp = 10

  l = read_dallas(gpio_temp, nb=2) # Pin created in function
  if l != []:
      print(l)
  else:
    print('error temp')