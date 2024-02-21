# tuto bytes

# bytes is SEQUENCE of 8 bits byte 

#  Bytes and bytearray objects contain single bytes
# The bytes() method returns an immutable bytes object initialized with the given size and data.
# returns a bytes object of the given size and initialization values

# when printing, will convert to ascii if possible

# use literals , need to define as string
b = b'titi'  

# define bytes as hex string, when mostly char
b = b'\x0f\xfeA'  # array len 3  NEED to use [0]
# b[0] as int is 15
print(b, len(b), type(b)) # b'\x0f\xfeA' 3 <class 'bytes'>

# define bytes as hex array , when mostly hex    Must be iterable of integers between 0 <= x < 256
b = bytes([0x0f, 0xfe, ord('B')])   # USE ord , not int()
# note b = bytes(0xff) is array of 255 NULL
print(b, len(b), type(b)) # b'\x0f\xfeB' 3 <class 'bytes'>

# convert to int
print('%d' %b[0]) # b array
print(int(b[0]))

b = 0x0f
print(b, type(b)) # 15 <class 'int'>

# binary reprsentation
print(bin(b))

# constructors
# if source is string followed by encoding, and error
b = bytes("test", 'utf-8') # string to bytes
# when printing bytes, will convert to ascii if possible
print (b, type(b))

# same as
b = 'test'.encode('utf-8')  # string to bytes
print (b, type(b), len(b)) # b'test' <class 'bytes'> 4

# decode bytes to string
b1 = b.decode()
print(b1, type(b1), len(b1)) #test <class 'str'> 4


# HEX
# each 8 bits byte converted to 2 number, hex representation char 0 to F, then stored as str or bytes 

# convert BIN to HEX str
b1 = b.hex()
print(b1, type(b1), len(b1)) # 74657374 <class 'str'> 8  LEN x2

# convert BIN to HEX bytes
import binascii # to binary from ASCII or hex, and vice versa.

b1=binascii.hexlify(b) # converts the binary representation of the data to hexadecimal
# Every byte is converted to a 2-digit hexadecimal representation. LEN x2
print(b1, type(b1), len(b1))  # b'74657374' <class 'bytes'> 8

#  mutable version, use the bytearray() method.
b = bytearray("test", "utf-8")
print(b)
b[0]= 0x02
print(b) # bytearray(b'\x02est')

# source int, array of size n
b = bytes(5) # array of size n, init with NULL
# b'\x00\x00\x00\x00\x00'

# source iterable  Must be iterable of integers between 0 <= x < 256
b = bytes ([1,2,3])
print(b)
# b'\x01\x02\x03'
# 
b = bytes ([0x01,0x41, ord('B')]) # cannot use ['\x01'] string cannot be interpreted as int 
print(b) # b'\x01A'   when printing, will convert to ascii if possible

# x hex, c single char
print('0x%x char%c 0x%x' %(b[0], b[1], b[2])) # 0x1 charA 0x42

import struct # convert the native data types of Python into string of bytes and vice versa.
# can concatenate various types
# By default, C types are represented in the machine’s native format and byte order, and properly aligned by skipping pad bytes if necessary
#  first character of the format string can be used to indicate the byte order, size and alignment of the packed data
#  @ native native native

# https://docs.python.org/3/library/struct.html

# s requires bytes object
b = struct.pack('4s i', b'test', 10) # b'test\n\x00\x00\x00'    n000 is 10 as 32 bits int

b1=struct.unpack('4si', b)
print(b1, type(b1)) # (b'test', 10) <class 'tuple'>

b = struct.pack('4s h', b'test', 10) # b'test\n\x00' 
b = struct.pack('>4s h', b'test', 10) # b'test\x00\n'
print(b)
b = struct.pack('<4s h', b'test', 10) # b'test\n\x00'
print(b)
# c requites bytes object of len 1
b = struct.pack('c f', b't', 2.5) # b't\x00\x00\x00\x00\x00 @'
print(b)



"""
Character

Byte order

Size

Alignment

@

native

native

native

=

native

standard

none

<

little-endian

standard

none

>

big-endian

standard

none

!

network (= big-endian)

standard

none


"""

"""
c char            bytes of length 1
b signed char       integer
B unsigned char     integer
h short             integer 2 bytes
H unsigned short    integer




"""