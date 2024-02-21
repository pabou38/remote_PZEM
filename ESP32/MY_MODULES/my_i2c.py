
from machine import Pin, I2C

try:
  import i2c_addresses

except: # file used as main, so this import was not done
  import sys
  sys.path.append("/my_modules")
  import i2c_addresses

##########
# i2c
##########

# ESP32
# classmachine.I2C(id, *, scl, sda, freq=400000, timeout=50000)
# There are two hardware I2C peripherals with identifiers 0 and 1. 
# Any available output-capable pins can be used for SCL and SDA but the defaults are given below. 
# default pin
# i2c = I2C(1, scl=Pin(25), sda=Pin(26), freq=400000)
# i2c = I2C(0, scl=Pin(18), sda=Pin(19), freq=400000)


# Software I2C (using bit-banging) works on all output-capable pins, and is accessed via the machine.SoftI2C class:
# classmachine.SoftI2C(scl, sda, *, freq=400000, timeout=50000)

# GPIO number, not pins
def create_i2c(port, gpio_scl= None, gpio_sda= None):
  print("start i2c. port %d, sda %d, scl %d; and scan" %(port, gpio_sda, gpio_scl))

  # scl should be a pin object specifying the pin to use for SCL.
  i2c = I2C(port,scl=Pin(gpio_scl), sda=Pin(gpio_sda))

  #  if not (0, Warning: I2C(-1, ...) is deprecated, use SoftI2C(...) instead

  print("i2c scan..")
  devices = i2c.scan()

  if len(devices) == 0:
    print("no i2c devices")
    return(None)

  else:
    print ("devices list: ", devices) 
    print ("devices in hexa:", end= " ")
    for x in devices:
      print (hex(x), end= ' ')
    print(' ')

    for x in devices:
      try:
          print("==> found: %s" %i2c_addresses.i2c_addresses[x] , end = ' ')
      except Exception as e:
          pass
      print(' ')

    return(i2c)

if __name__ == "__main__":

  ########################
  # !!!!!! does not work with micropython
  # if main.py includes import my_i2c
  #  rather copy my_i2c.py to main.py
  ########################

  print("testing i2c")

  port = 0
  gpio_sda = 21
  gpio_scl = 22

  print("hw port %d (0 or 1), sda %d, scl %d" %(port, gpio_sda, gpio_scl))

  # scl should be a pin object specifying the pin to use for SCL.

  i2c = create_i2c(0, Pin(gpio_scl), Pin(gpio_sda)) 
  
  if i2c is None:
    print("cannot create i2c")
  else:
    print("i2c created")

    print("i2c scan..")
    devices = i2c.scan()
    print(devices)


