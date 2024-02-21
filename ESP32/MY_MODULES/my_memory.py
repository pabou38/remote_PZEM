import gc
import micropython

###################
# memory constaints
#https://docs.micropython.org/en/latest/reference/constrained.html

# https://www.youtube.com/watch?v=H_xq8IYjh2w  
# https://github.com/orgs/micropython/discussions/11997

#object allocated from fixed size heap. becomes garbage when out of scope. garbage collector returns it to the free heap
#allocate large object early, to avoid fragmentation

# heap = ram = mem

# NOTE: even small module (secret.py) may cause memory exception if not frozen (fixed RAM use to just compile it)

# in bytes
#GC: total: 37952, used: 8112, free: 29840
#mem free 29840, mem alloc 8112, total 3795
# The free memory is just the total amount of free memory, it’s not necessarily contiguous, even if it’s allocating 1K it may still fail if there are no 1K free contiguous blocks.

# BLOCK = 16 bytes, ie 4 x pointers of 32bits(ie 4 bytes)

# Blocks are chunks of contiguous of memory in the heap. 
# The size is configured by MICROPY_BYTES_PER_GC_BLOCK. 
# The default is the size of 4 pointers, so 16 bytes on 32-bit arch and 32 bytes on 64-bit arch.
# If memory is needed, then the smallest amount of memory that can be allocated is a block.

# all below in block:
# No. of 1-blocks: 71, 2-blocks: 25, max blk sz: 72, max free sz: 1136

# 1-blocks are blocks memory that has been allocated for an object that requires <= the number of bytes in one block. Small objects like floats fit in to one block. 
# 2-blocks are two contiguous blocks which are allocated for object that are too big to fit in one block  but small enough to fit in two blocks.
# max blk sz: 72, max free sz: 328
# These numbers are all in blocks. 
# This means the largest object that has been allocated uses 72 contiguous blocks (max block sz)  and the largest contiguous region of unallocated blocks is 328 blocks (max free sz).
###################

import micropython

gc.collect()

# Automatic GC is provoked under the following circumstances. 
# When an attempt at allocation fails, a GC is performed and the allocation re-tried. 
# Only if this fails is an exception raised. 
# Secondly an automatic GC will be triggered if the amount  of free RAM falls below a threshold. 
# This threshold can be adapted as execution progresses:
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

micropython.mem_info(1) 
# Print a table of heap utilisation. (1) print map.
# Each byte corresponds to 8 bytes of memory. To allocate 4084 bytes would require 510 contiguous blocks.

# Each letter represents a single block of memory, a block being 16 bytes. 
# So each line of the heap dump represents 0x400 bytes or 1KiB of RAM.

# ESP8266: stack is 8192, ie  8K
# mem total, ie heap is 37952 

# https://docs.micropython.org/en/latest/reference/constrained.html

#stack: 3024 out of 8192
#GC: total: 37952, used: 8112, free: 29840
# No. of 1-blocks: 71, 2-blocks: 25, max blk sz: 72, max free sz: 1136
#mem free 29840, mem alloc 8112, total 37952

# gc.mem_free() and gc.memalloc() is the same as what mem_info report as GC used and free
# sum is indeed total




def print_mem(s = None):

  if s is not None:
    print("====> " + s)
  gc.collect()
  micropython.mem_info() 

  # this is the same as what mem_info report as GC used and free
  free = gc.mem_free()
  alloc = gc.mem_alloc()
  print("mem free %d, mem alloc %d, total %d, free %0.0f percent\n" %(free, alloc, free+alloc , 100.0 * float(free) / float((free+alloc))))




"""
The ESP8266 uses a 32bit processor with 16 bit instructions. 
It is Harvard architecture which mostly means that instruction memory and data memory are completely separate.

The ESP8266 has on die program Read-Only Memory (ROM) which includes some library code and a first stage boot loader. 
All the rest of the code must be stored in external Serial flash memory 
(provides only serial access to the data - rather than addressing individual bytes, the user reads or writes large contiguous groups of bytes in the address space serially).

The ESP8266 has a total of 64K of instruction memory, IRAM
  32 KiB instruction RAM
  32 KiB instruction cache RAM

80 KiB user-data RAM
There is 98KB of DRAM space.

External QSPI flash: up to 16 MiB is supported (512 KiB to 4 MiB typically included)

The RAM in an ESP8266 is fixed ... typically after loading the Espressif SDK ready for WiFi and TCP/IP, 
there is commonly about 40K of RAM remaining for applications

PRE-COMPILE .mpy (into file system)
If RAM is still insufficient to compile all modules one solution is to precompile modules. 
MicroPython has a cross compiler capable of compiling Python modules to bytecode. 
The resulting bytecode file has a .mpy extension; it may be copied to the filesystem and imported in the usual way. 

FROZEN MODULE (into firmware)
Frozen modules store the Python source with the firmware.

FROZEN BYTECODE (into firmware)
Frozen bytecode uses the cross compiler to convert the source to bytecode which is then stored with the firmware.
Alternatively some or all modules may be implemented as frozen bytecode: 
on most platforms this saves even more RAM as the bytecode is run directly from flash rather than being stored in RAM.

On the ESP32, code can either execute from flash or from IRAM, but not PSRAM. It is much faster to execute code from IRAM, so MicroPython puts a few performance-critical functions into IRAM. 
This does make a fairly significant performance increase

However, on the ESP32S3, it is possible to execute from PSRAM

Executable segment sizes:
ICACHE : 32768           - flash instruction cache 
IROM   : 231500          - code in flash         (default or ICACHE_FLASH_ATTR) 
IRAM   : 26217   / 32768 - code in IRAM          (IRAM_ATTR, ISRs...) 
DATA   : 1496  )         - initialized variables (global, static) in RAM/HEAP 
RODATA : 876   ) / 81920 - constants             (global, static) in RAM/HEAP 
BSS    : 25520 )         - zeroed variables      (global, static) in RAM/HEAP 
"""