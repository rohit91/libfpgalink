#!/usr/bin/env python
#
# Copyright (C) 2009-2014 Chris McClelland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

## @namespace fpgalink
#
# The <b>FPGALink</b> library makes it easier to talk to an FPGA over USB (via a suitable micro).
#
# It performs four classes of function:
# - Load device firmware and EEPROM (specific to Cypress FX2LP).
# - Program an FPGA or CPLD using JTAG or one of the proprietary serial or parallel algorithms.
# - Read and write (over USB) up to 128 byte-wide data channels in the target FPGA.
# - Manipulate microcontroller digital I/O & SPI port(s).
#
import array
import time
import sys
from ctypes import *

## @cond FALSE
class FLContext(Structure):
    pass
class FLException(Exception):
    pass
FLHandle = POINTER(FLContext)
FLStatus = c_uint
FL_SUCCESS = 0
uint32 = c_uint
uint16 = c_ushort
uint8 = c_ubyte
size_t = c_size_t
ErrorString = c_char_p

def enum(**enums):
    return type('Enum', (), enums)

PinConfig = enum(
    HIGH  = uint8(0x01),
    LOW   = uint8(0x02),
    INPUT = uint8(0x03)
)
LogicalPort = enum(
    MISO = uint8(0x01),
    MOSI = uint8(0x02),
    SS   = uint8(0x03),
    SCK  = uint8(0x04)
)
BitOrder = enum(
    MSBFIRST = uint8(0x00),
    LSBFIRST = uint8(0x01)
)
Shift = enum(
    ZEROS = cast(0, c_char_p),
    ONES = cast(-1, c_char_p)
)
class ReadReport(Structure):
    _fields_ = [("data", POINTER(uint8)),
                ("requestLength", uint32),
                ("actualLength", uint32)]

# Get DLL
if ( sys.platform.startswith("linux") ):
    cdll.LoadLibrary("libfpgalink.so")
    fpgalink = CDLL("libfpgalink.so")
elif ( sys.platform == "darwin" ):
    cdll.LoadLibrary("libfpgalink.dylib")
    fpgalink = CDLL("libfpgalink.dylib")
elif ( sys.platform == "win32" ):
    windll.LoadLibrary("libfpgalink.dll")
    fpgalink = WinDLL("libfpgalink.dll")
else:
    raise FLException("Unrecognised platform: " + sys.platform)

# Miscellaneous Functions
fpgalink.flInitialise.argtypes = [c_int, POINTER(ErrorString)]
fpgalink.flInitialise.restype = FLStatus
fpgalink.flFreeError.argtypes = [c_char_p]
fpgalink.flFreeError.restype = None

# Connection Lifecycle
fpgalink.flOpen.argtypes = [c_char_p, POINTER(FLHandle), POINTER(ErrorString)]
fpgalink.flOpen.restype = FLStatus
fpgalink.flClose.argtypes = [FLHandle]
fpgalink.flClose.restype = None

# Device Capabilities and Status
fpgalink.flIsDeviceAvailable.argtypes = [c_char_p, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flIsDeviceAvailable.restype = FLStatus
fpgalink.flIsNeroCapable.argtypes = [FLHandle]
fpgalink.flIsNeroCapable.restype = uint8
fpgalink.flIsCommCapable.argtypes = [FLHandle]
fpgalink.flIsCommCapable.restype = uint16
fpgalink.flGetFirmwareID.argtypes = [FLHandle]
fpgalink.flGetFirmwareID.restype = uint16
fpgalink.flGetFirmwareVersion.argtypes = [FLHandle]
fpgalink.flGetFirmwareVersion.restype = uint32

# CommFPGA Operations
fpgalink.flSelectConduit.argtypes = [FLHandle, uint8, POINTER(ErrorString)]
fpgalink.flSelectConduit.restype = FLStatus
fpgalink.flIsFPGARunning.argtypes = [FLHandle, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flIsFPGARunning.restype = FLStatus
fpgalink.flReadChannel.argtypes = [FLHandle, uint8, size_t, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flReadChannel.restype = FLStatus
fpgalink.flWriteChannel.argtypes = [FLHandle, uint8, size_t, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flWriteChannel.restype = FLStatus
fpgalink.flSetAsyncWriteChunkSize.argtypes = [FLHandle, uint16, POINTER(ErrorString)]
fpgalink.flSetAsyncWriteChunkSize.restype = FLStatus
fpgalink.flWriteChannelAsync.argtypes = [FLHandle, uint8, size_t, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flWriteChannelAsync.restype = FLStatus
fpgalink.flFlushAsyncWrites.argtypes = [FLHandle, POINTER(ErrorString)]
fpgalink.flFlushAsyncWrites.restype = FLStatus
fpgalink.flAwaitAsyncWrites.argtypes = [FLHandle, POINTER(ErrorString)]
fpgalink.flAwaitAsyncWrites.restype = FLStatus
fpgalink.flReadChannelAsyncSubmit.argtypes = [FLHandle, uint8, uint32, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flReadChannelAsyncSubmit.restype = FLStatus
fpgalink.flReadChannelAsyncAwait.argtypes = [FLHandle, POINTER(ReadReport), POINTER(ErrorString)]
fpgalink.flReadChannelAsyncAwait.restype = FLStatus

# NeroProg Operations
fpgalink.flProgram.argtypes = [FLHandle, c_char_p, c_char_p, POINTER(ErrorString)]
fpgalink.flProgram.restype = FLStatus
fpgalink.flProgramBlob.argtypes = [FLHandle, c_char_p, uint32, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flProgramBlob.restype = FLStatus
fpgalink.jtagScanChain.argtypes = [FLHandle, c_char_p, POINTER(uint32), POINTER(uint32), uint32, POINTER(ErrorString)]
fpgalink.jtagScanChain.restype = FLStatus
fpgalink.progOpen.argtypes = [FLHandle, c_char_p, POINTER(ErrorString)]
fpgalink.progOpen.restype = FLStatus
fpgalink.progClose.argtypes = [FLHandle, POINTER(ErrorString)]
fpgalink.progClose.restype = FLStatus
fpgalink.jtagShift.argtypes = [FLHandle, uint32, c_char_p, POINTER(uint8), uint8, POINTER(ErrorString)]
fpgalink.jtagShift.restype = FLStatus
fpgalink.jtagClockFSM.argtypes = [FLHandle, uint32, uint8, POINTER(ErrorString)]
fpgalink.jtagClockFSM.restype = FLStatus
fpgalink.jtagClocks.argtypes = [FLHandle, uint32, POINTER(ErrorString)]
fpgalink.jtagClocks.restype = FLStatus
fpgalink.progGetPort.argtypes = [FLHandle, uint8]
fpgalink.progGetPort.restype = uint8
fpgalink.progGetBit.argtypes = [FLHandle, uint8]
fpgalink.progGetBit.restype = uint8
fpgalink.spiSend.argtypes = [FLHandle, uint32, c_char_p, uint8, POINTER(ErrorString)]
fpgalink.spiSend.restype = FLStatus
fpgalink.spiRecv.argtypes = [FLHandle, uint32, POINTER(uint8), uint8, POINTER(ErrorString)]
fpgalink.spiRecv.restype = FLStatus

# Firmware Operations
fpgalink.flLoadStandardFirmware.argtypes = [c_char_p, c_char_p, POINTER(ErrorString)]
fpgalink.flLoadStandardFirmware.restype = FLStatus
fpgalink.flFlashStandardFirmware.argtypes = [FLHandle, c_char_p, POINTER(ErrorString)]
fpgalink.flFlashStandardFirmware.restype = FLStatus
fpgalink.flSaveFirmware.argtypes = [FLHandle, uint32, c_char_p, POINTER(ErrorString)]
fpgalink.flSaveFirmware.restype = FLStatus
fpgalink.flLoadCustomFirmware.argtypes = [c_char_p, c_char_p, POINTER(ErrorString)]
fpgalink.flLoadCustomFirmware.restype = FLStatus
fpgalink.flFlashCustomFirmware.argtypes = [FLHandle, c_char_p, uint32, POINTER(ErrorString)]
fpgalink.flFlashCustomFirmware.restype = FLStatus

# Utility functions
fpgalink.flSleep.argtypes = [uint32]
fpgalink.flSleep.restype = None
fpgalink.flLoadFile.argtypes = [c_char_p, POINTER(size_t)]
fpgalink.flLoadFile.restype = POINTER(uint8)
fpgalink.flFreeFile.argtypes = [POINTER(uint8)]
fpgalink.flFreeFile.restype = None
fpgalink.flSingleBitPortAccess.argtypes = [FLHandle, uint8, uint8, uint8, POINTER(uint8), POINTER(ErrorString)]
fpgalink.flSingleBitPortAccess.restype = FLStatus
fpgalink.flMultiBitPortAccess.argtypes = [FLHandle, c_char_p, POINTER(uint32), POINTER(ErrorString)]
fpgalink.flMultiBitPortAccess.restype = FLStatus
## @endcond

##
# @name Miscellaneous Functions
# @{

##
# @brief Initialise the library with the given log level.
#
# This may fail if LibUSB cannot talk to the USB host controllers through its kernel driver
# (e.g a Linux kernel with USB support disabled, or a machine lacking a USB host controller).
#
# @param debugLevel 0->none, 1, 2, 3->lots.
# @throw FLException if there were problems initialising LibUSB.
# 
def flInitialise(debugLevel):
    error = ErrorString()
    status = fpgalink.flInitialise(debugLevel, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
# @}

##
# @name Connection Lifecycle
# @{

##
# @brief Open a connection to the FPGALink device at the specified VID & PID.
#
# Connects to the device and verifies it's an FPGALink device, then queries its capabilities.
#
# @param vp The Vendor/Product (i.e VVVV:PPPP) of the FPGALink device. You may also specify
#            an optional device ID (e.g 1D50:602B:0004). If no device ID is supplied, it
#            selects the first device with matching VID:PID.
# @returns An opaque reference to an internal structure representing the connection. This must be
#            freed at some later time by a call to \c flClose(), or a resource-leak will ensue.
# @throw FLException
#     - If there was a memory allocation failure.
#     - If the VID:PID is invalid or the device cannot be found or opened.
#     - If the device is not an FPGALink device.
#
def flOpen(vp):
    handle = FLHandle()
    error = ErrorString()
    status = fpgalink.flOpen(vp.encode('ascii'), byref(handle), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    return handle

##
# @brief Close the connection to the FPGALink device.
#
# @param handle The handle returned by \c flOpen().
#
def flClose(handle):
    fpgalink.flClose(handle)

# @}

##
# @name Device Capabilities and Status
# @{

##
# @brief Await renumeration - return true if found before timeout.
#
# This function will wait for the specified VID:PID to be added to the system (either due to a
# renumerating device, or due to a new physical connection). It will wait for a fixed period of
# 1s and then start polling the USB bus looking for the specified device. If no such device is
# detected within \c timeout deciseconds after the initial delay, it returns \c False, else it
# returns \c True.
#
# @param vp The Vendor/Product (i.e VVVV:PPPP) of the FPGALink device. You may also specify
#            an optional device ID (e.g 1D50:602B:0004). If no device ID is supplied, it
#            awaits the first device with matching VID:PID.
# @param timeout The number of tenths-of-a-second to wait, after the initial 1s delay.
# @throw FLException if the VID:PID is invalid or if no USB buses were found (did you remember to
#            call \c flInitialise()?).
#
def flAwaitDevice(vp, timeout):
    error = ErrorString()
    isAvailable = uint8()
    fpgalink.flSleep(1000);
    while ( True ):
        fpgalink.flSleep(100);
        status = fpgalink.flIsDeviceAvailable(vp.encode('ascii'), byref(isAvailable), byref(error))
        if ( status != FL_SUCCESS ):
            s = str(error.value)
            fpgalink.flFreeError(error)
            raise FLException(s)
        timeout = timeout - 1
        if ( isAvailable ):
            return True
        if ( timeout == 0 ):
            return False

##
# @brief Check to see if the device supports NeroProg.
#
# NeroProg is the collective name for all the various programming algorithms supported by
# FPGALink, including but not limited to JTAG. An affirmative response means you are free to
# call \c flProgram(), \c jtagScanChain(), \c progOpen(), \c progClose(),
# \c jtagShiftInOut(), \c jtagClockFSM() and \c jtagClocks().
#
# @param handle The handle returned by \c flOpen().
# @returns \c True if the device supports NeroProg, else \c False.
#
def flIsNeroCapable(handle):
    if ( fpgalink.flIsNeroCapable(handle) ):
        return True
    else:
        return False

##
# @brief Check to see if the device supports CommFPGA.
#
# CommFPGA is a set of channel read/write protocols. The micro may implement several
# different CommFPGA protocols, distinguished by the chosen conduit. A micro will typically
# implement its first CommFPGA protocol on conduit 1, and additional protocols on conduits
# 2, 3 etc. Conduit 0 is reserved for communication over JTAG using a virtual TAP
# state machine implemented in the FPGA, and is not implemented yet.
#
# This function returns \c True if the micro supports CommFPGA on the chosen conduit, else
# \c False.
#
# Note that this function can only know the capabilities of the micro itself; it cannot determine
# whether the FPGA contains suitable logic to implement the protocol, or even whether there is
# an FPGA physically wired to the micro in the first place.
#
# An affirmative response means you are free to call \c flReadChannel(),
# \c flReadChannelAsyncSubmit(), \c flReadChannelAsyncAwait(), \c flWriteChannel(),
# \c flWriteChannelAsync() and \c flIsFPGARunning().
#
# @param handle The handle returned by \c flOpen().
# @param conduit The conduit you're interested in (this will typically be 1).
# @returns \c True if the device supports CommFPGA, else \c False.
#
def flIsCommCapable(handle, conduit):
    if ( fpgalink.flIsCommCapable(handle, conduit) ):
        return True
    else:
        return False

##
# @brief Get the firmware ID.
#
# Each firmware (or fork of an existing firmware) has its own 16-bit ID, which this function
# retrieves.
#
# @param handle The handle returned by \c flOpen().
# @returns A 16-bit unsigned integer giving the firmware ID.
#
def flGetFirmwareID(handle):
    return fpgalink.flGetFirmwareID(handle)

##
# @brief Get the firmware version.
#
# Each firmware knows the GitHub tag from which is was built, or if it was built from a trunk,
# it knows the date on which it was built. This function returns a 32-bit integer giving that
# information. If printed as a hex number, it gives an eight-digit ISO date.
#
# @param handle The handle returned by \c flOpen().
# @returns A 32-bit unsigned integer giving the firmware version.
#
def flGetFirmwareVersion(handle):
    return fpgalink.flGetFirmwareVersion(handle)
# @}

##
# @name CommFPGA Operations
# @{

##
# @brief Select a different conduit.
#
# Select a different conduit for CommFPGA communication. Typically a micro will implement its
# first CommFPGA protocol on conduit 1. It may or may not also implement others on conduit 2, 3,
# 4 etc. It may also implement comms-over-JTAG using a virtual TAP FSM on the FPGA. You can use
# \c flIsCommCapable() to determine whether the micro supports CommFPGA on a given conduit.
#
# If mixing NeroProg operations with CommFPGA operations, it *may* be necessary to switch
# conduits. For example, if your PCB is wired to use some of the CommFPGA signals during
# programming, you will have to switch back and forth. But if the pins used for CommFPGA are
# independent of the pins used for NeroProg, you need only select the correct conduit on startup
# and then leave it alone.
#
# @param handle The handle returned by \c flOpen().
# @param conduit The conduit to select (current range 0-15).
# @throw FLException if the device doesn't respond, or the conduit is out of range.
#
def flSelectConduit(handle, conduit):
    error = ErrorString()
    status = fpgalink.flSelectConduit(handle, conduit, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Check to see if the FPGA is running.
#
# This may only be called if \c flIsCommCapable() returns \c True. It merely verifies that
# the FPGA is asserting that it's ready to read commands on the chosen conduit. Some conduits
# may not have the capability to determine this, and will therefore just optimistically report
# \c True. Before calling \c flIsFPGARunning(), you should verify that the FPGALink device
# actually supports CommFPGA using \c flIsCommCapable(), and select the conduit you wish to
# use with \c flSelectConduit().
#
# @param handle The handle returned by \c flOpen().
# @returns \c True if the FPGA is ready to accept commands, else \c False.
# @throw FLException if the device does not support CommFPGA.
#
def flIsFPGARunning(handle):
    error = ErrorString()
    isRunning = uint8()
    status = fpgalink.flIsFPGARunning(handle, byref(isRunning), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    if ( isRunning ):
        return True
    else:
        return False

##
# @brief Synchronously read one or more bytes from the specified channel.
#
# Read \c length bytes from the FPGA channel \c chan. Before calling \c flReadChannel(), you
# should verify that the FPGALink device actually supports CommFPGA using \c flIsCommCapable().
#
# Because this function is synchronous, it will block until the data has been returned.
#
# @param handle The handle returned by \c flOpen().
# @param chan The FPGA channel to read.
# @param length The number of bytes to read.
# @returns Either a single integer (0-255) or a \c bytearray.
# @throw FLException 
#     - If a USB read or write error occurred.
#     - If the device does not support CommFPGA.
#     - If there are async reads in progress.
#
def flReadChannel(handle, chan, length = 1):
    error = ErrorString()
    if ( length == 1 ):
        # Read a single byte
        buf = uint8()
        status = fpgalink.flReadChannel(handle, chan, 1, byref(buf), byref(error))
        returnValue = buf.value
    else:
        # Read multiple bytes
        byteArray = bytearray(length)
        BufType = uint8*length
        buf = BufType.from_buffer(byteArray)
        status = fpgalink.flReadChannel(handle, chan, length, buf, byref(error))
        returnValue = byteArray
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    return returnValue

##
# @brief Synchronously write one or more bytes to the specified channel.
#
# Write data to FPGA channel \c chan from \c values, which may be a single integer (0-255), a
# \c bytearray or the name of a file to read the data from. Before calling \c flWriteChannel(),
# you should verify that the FPGALink device actually supports CommFPGA using \c flIsCommCapable().
#
# Because this function is synchronous, it will block until the OS has confirmed that the data
# has been correctly sent over USB and received by the micro. It cannot confirm that the data
# has been received by the FPGA however: it may be waiting in the micro's output buffer.
#
# @param handle The handle returned by \c flOpen().
# @param chan The FPGA channel to write.
# @param values The data to be written synchronously to the FPGA.
# @throw FLException
#     - If a USB write error occurred.
#     - If the device does not support CommFPGA.
#     - If there are async reads in progress.
#
def flWriteChannel(handle, chan, values):
    error = ErrorString()
    if ( isinstance(values, bytearray) ):
        # Write the contents of the byte array:
        numValues = len(values)
        BufType = uint8*numValues
        buf = BufType.from_buffer(values)
        status = fpgalink.flWriteChannel(handle, chan, numValues, buf, byref(error))
    elif ( isinstance(values, int) ):
        # Write a single integer
        if ( values > 0xFF ):
            raise FLException("Supplied value won't fit in a byte!")
        status = fpgalink.flWriteChannel(handle, chan, 1, (uint8*1)(values), byref(error))
    else:
        # Write the contents of a file
        fileLen = size_t()
        fileData = fpgalink.flLoadFile(values.encode('ascii'), byref(fileLen))
        if ( fileData == None ):
            raise FLException("Cannot load file!")
        status = fpgalink.flWriteChannel(handle, chan, fileLen, fileData, byref(error))
        fpgalink.flFreeFile(fileData)
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Set the chunk size to be used for future async writes.
#
# By default, the \c flWriteChannelAsync() function buffers up to 64KiB of data before sending
# anything over USB. Chunking the data in this way is more efficient than sending lots of little
# messages. However, the choice of chunk size affects the steady-state throughput in interesting
# ways. If you need to, you can choose to make the chunks smaller than 64KiB.
#
# You should not call this when there is some send data buffered. You should either call this
# before the first call to \c flWriteChannelAsync(), or call it immediately after a call to
# \c flFlushAsyncWrites().
#
# @param handle The handle returned by \c flOpen().
# @param chunkSize The new chunksize in bytes. Passing zero sets the chunkSize to 64KiB.
# @throw FLException if there is some outstanding send data.
#
def flSetAsyncWriteChunkSize(handle, chunkSize):
    error = ErrorString()
    status = fpgalink.flSetAsyncWriteChunkSize(handle, chunkSize, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Asynchronously write one or more bytes to the specified channel.
#
# Write data to FPGA channel \c chan from \c values, which may be a single integer (0-255), a
# \c bytearray or the name of a file to read the data from. Before calling \c flWriteChannelAsync(),
# you should verify that the FPGALink device actually supports CommFPGA using \c flIsCommCapable().
#
# This function is asynchronous. That means it will return immediately, usually before anything
# has been actually sent over USB. If the operation fails, you will not be notified of the
# failure until a future call to \c flAwaitAsyncWrites() or \c flReadChannelAsyncAwait(). The
# data is copied internally, so there's no need to worry about preserving the data: it's safe to
# call \c flWriteChannelAsync() on a stack-allocated array, for example.
#
# @param handle The handle returned by \c flOpen().
# @param chan The FPGA channel to write.
# @param values The data to be written asynchronously to the FPGA.
# @throw FLException
#     - If we ran out of memory.
#     - If a USB write error occurred.
#     - If the device does not support CommFPGA.
#
def flWriteChannelAsync(handle, chan, values):
    error = ErrorString()
    if ( isinstance(values, bytearray) ):
        # Write the contents of the byte array:
        numValues = len(values)
        BufType = uint8*numValues
        buf = BufType.from_buffer(values)
        status = fpgalink.flWriteChannelAsync(handle, chan, numValues, buf, byref(error))
    elif ( isinstance(values, int) ):
        # Write a single integer
        if ( values > 0xFF ):
            raise FLException("Supplied value won't fit in a byte!")
        status = fpgalink.flWriteChannelAsync(handle, chan, 1, (uint8*1)(values), byref(error))
    else:
        # Write the contents of a file
        fileLen = uint32()
        fileData = fpgalink.flLoadFile(values.encode('ascii'), byref(fileLen))
        if ( fileData == None ):
            raise FLException("Cannot load file!")
        status = fpgalink.flWriteChannelAsync(handle, chan, fileLen, fileData, byref(error))
        fpgalink.flFreeFile(fileData)
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Flush out any pending asynchronous writes.
#
# Flush any writes that have been buffered up, or do nothing if no writes have been buffered.
# This only triggers the send over USB; it does not guarantee the micro successfully received
# the data. See \c flAwaitAsyncWrites().
#
# @param handle The handle returned by \c flOpen().
# @throw FLException
#     - If a USB write error occurred.
#     - If the device does not support CommFPGA.
#
def flFlushAsyncWrites(handle):
    error = ErrorString()
    status = fpgalink.flFlushAsyncWrites(handle, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Wait for confirmation that pending asynchronous writes were received by the micro.
#
# The first thing this does is to call \c flFlushAsyncWrites() to flush out any outstanding
# write commands. It will then block until the OS confirms that all the asynchronous write
# commands sent by \c flWriteChannelAsync() were correctly sent over USB and recieved by the
# micro. It cannot confirm that that the writes were received by the FPGA however: they may be
# waiting in the micro's output buffer.
#
# @param handle The handle returned by \c flOpen().
# @throw FLException
#     - If one of the outstanding async operations failed.
#     - If the device does not support CommFPGA.
#     - If there are async reads in progress.
#
def flAwaitAsyncWrites(handle):
    error = ErrorString()
    status = fpgalink.flAwaitAsyncWrites(handle, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Submit an asynchronous read of one or more bytes from the specified channel.
#
# Submit an asynchronous read of \c length bytes from the FPGA channel \c chan. You can request
# at most 64KiB of data asynchronously. Before calling \c flReadChannelAsyncSubmit(), you should
# verify that the FPGALink device actually supports CommFPGA using \c flIsCommCapable().
#
# This function is asynchronous. That means it will return immediately, usually before the read
# request has been sent over USB. You will not find out the result of the read until you later
# call \c flReadChannelAsyncAwait() - this will give you your data, or tell you what went wrong.
#
# You should always ensure that for each call to \c flReadChannelAsyncSubmit(), there is a
# matching call to \c flReadChannelAsyncAwait(). You should not call any of
# \c flSetAsyncWriteChunkSize(), \c flAwaitAsyncWrites(), \c flWriteChannel() or
# \c flReadChannel() between a submit...await pair.
#
# USB host controllers typically need just one level of nesting of submit...await pairs to keep
# them busy. That means sequences like submit, submit, await, submit, await, submit, ..., await,
# await.
#
# @param handle The handle returned by \c flOpen().
# @param chan The FPGA channel to read.
# @param length The number of bytes to read, <= 64KiB (hence \c uint32 rather than \c size_t).
# @throw FLException
#     - If a USB read or write error occurred.
#     - If the device does not support CommFPGA.
#
def flReadChannelAsyncSubmit(handle, chan, length = 1):
    error = ErrorString()
    status = fpgalink.flReadChannelAsyncSubmit(handle, chan, length, None, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Await the data from a previously-submitted asynchronous read.
#
# Block until the outcome of a previous call to \c flReadChannelAsyncSubmit() is known. If the
# read was successful, you are given the resulting data. If not, an error code/message.
#
# On successful outcome, a \c ReadReport object is returned with a pointer to the data, the
# number of bytes read, etc. This gives access to the raw memory owned by the FPGALink DLL. It is
# guaranteed to remain valid until your next call to any of the CommFPGA functions. You can copy
# it into a string with something like ctypes.string_at(readReport.data, readReport.actualLength).
#
# @param handle The handle returned by \c flOpen().
# @returns A \c ReadReport object which points to the data read, and the number of bytes.
# @throw FLException if one of the outstanding async operations failed.
#
def flReadChannelAsyncAwait(handle):
    readReport = ReadReport(None, 0, 0)
    error = ErrorString()
    status = fpgalink.flReadChannelAsyncAwait(handle, byref(readReport), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    return readReport
# @}

##
# @name NeroProg Operations
# @{

##
# @brief Program a device using the given config string and either a file-name or a bytearray.
#
# This will program an FPGA or CPLD using the specified microcontroller ports and the specified
# programming file or an in-memory \c bytearray containing the configuration information. Several
# programming algorithms are supported (JTAG, Xilinx Slave-Serial, Xilinx SelectMap). In each case,
# it's necessary to tell the micro which ports to use. Here are some examples:
#
# A Digilent board using JTAG: <code>progConfig="J:D0D2D3D4"</code>:
# - TDO: PD0
# - TDI: PD2
# - TMS: PD3
# - TCK: PD4
#
# MakeStuff LX9 using JTAG: <code>progConfig="J:A7A0A3A1"</code>:
# - TDO: PA7
# - TDI: PA0
# - TMS: PA3
# - TCK: PA1
#
# EP2C5 Mini Board using Altera Passive-Serial: <code>progConfig="AS:B5B6B1B2"</code> (note that
# the board normally connects MSEL[1:0] to ground, hard-coding it in Active-Serial mode. For
# Passive-Serial to work you need to lift pin 85 and pull it up to VCC):
# - nCONFIG: PD5
# - CONF_DONE: PD6
# - DCLK: PD1
# - DATA0: PD2
#
# Aessent aes220 using Xilinx Slave-Serial: <code>progConfig="XS:D0D5D1D6A7[D3?,B1+,B5+,B3+]"</code>:
# - PROG_B: PD0
# - INIT_B: PD5
# - DONE: PD1
# - CCLK: PD6
# - DIN: PA7
# - Tristate DOUT (PD3)
# - Drive M[2:0]="111" (PB1, PB5, PB3) for Slave-Serial
#
# Aessent aes220 using Xilinx SelectMAP: <code>progConfig="XP:D0D5D1D6A01234567[B4-,D2-,D3?,B1+,B5+,B3-]"</code>:
# - PROG_B: PD0
# - INIT_B: PD5
# - DONE: PD1
# - CCLK: PD6
# - D[7:0]: PA[7:0]
# - Drive RDWR_B="0" (PB4)
# - Drive CSI_B="0" (PD2)
# - Tristate DOUT (PD3)
# - Drive M[2:0]="110" (PB1, PB5, PB3) for SelectMAP
#
# Note that this approach of specifying and implementing many disparate programming algorithms
# on the host side in terms of a much smaller set of building-block operations on the
# microcontroller is optimized for microcontrollers which support efficient remapping of I/O
# pins. For example the FX2 has a Von Neumann architecture where both code and data are stored
# in a single RAM-based address space, so port remapping can easily be achieved with
# self-modifying code. Conversely, the AVRs have Harvard architecture, where code and data are
# in separate address spaces, with code in flash so it cannot be self-modified. And actually,
# the AVR firmware is more likely to be tuned to a specific board layout than the more generic
# FX2 firmware.
#
# So, the bottom line is, even if you're using a microcontroller whose port pins are hard-coded,
# you still have to supply the port pins to use when you call functions expecting \c progConfig.
#
# You can either append the programming filename to the end of \c progConfig (e.g
# \c "J:A7A0A3A1:fpga.xsvf") or you can supply the programming filename separately in
# \c progFile.
#
# @param handle The handle returned by \c flOpen().
# @param progConfig The port configuration described above.
# @param progFile The name of the programming file, or NULL if it's already given in progConfig.
# @throw FLException
#     - If we ran out of memory during programming.
#     - If a USB error occurred.
#     - If the programming file is unreadable or an unexpected format.
#     - If an XSVF file contains an unsupported command.
#     - If an XSVF file contains an unsupported XENDDR/XENDIR.
#     - If an XSVF command is too long.
#     - If an SVF file is unparseable.
#     - If \c progConfig is malformed.
#     - If the micro was unable to map its ports to those given.
#     - If the micro refused to accept programming data.
#     - If the micro refused to provide programming data.
#     - If the micro refused to begin a JTAG shift operation.
#     - If the micro refused to navigate the TAP state-machine.
#     - If the micro refused to send JTAG clocks.
#     - If an SVF/XSVF compare operation failed.
#     - If an SVF/XSVF unknown command was encountered.
#     - If the FPGA failed to start after programming.
#     - If the micro refused to configure one of its ports.
#
def flProgram(handle, progConfig, progFile = None):
    error = ErrorString()
    if ( isinstance(progFile, bytearray) ):
        length = len(progFile)
        BufType = uint8*length
        buf = BufType.from_buffer(progFile)
        status = fpgalink.flProgramBlob(handle, progConfig.encode('ascii'), length, buf, byref(error))
    else:
        if ( progFile != None ):
            progFile = progFile.encode('ascii')
        status = fpgalink.flProgram(handle, progConfig.encode('ascii'), progFile, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Scan the JTAG chain and return an array of IDCODEs.
#
# @param handle The handle returned by \c flOpen().
# @param portConfig The port bits to use for TDO, TDI, TMS & TCK, or NULL to use the default.
# @returns An array of IDCODEs for each discovered device, in chain order.
# @throw FLException
#     - If \c portConfig is malformed.
#     - If the micro was unable to map its ports to those given.
#     - If the micro refused to accept programming data.
#     - If the micro refused to provide programming data.
#     - If the micro refused to begin a JTAG shift operation.
#     - If the micro refused to navigate the TAP state-machine.
#     - If the micro refused to configure one of its ports.
#
def jtagScanChain(handle, portConfig):
    error = ErrorString()
    ChainType = (uint32 * 16)  # Guess there are fewer than 16 devices
    chain = ChainType()
    length = uint32(0)
    status = fpgalink.jtagScanChain(handle, portConfig, byref(length), chain, 16, byref(error))
    if ( length.value > 16 ):
        # We know exactly how many devices there are, so try again
        ChainType = (uint32 * length.value)
        chain = ChainType()
        status = fpgalink.jtagScanChain(handle, portConfig, None, chain, length.value, byref(error))
    result = []
    for id in chain[:length.value]:
        result.append(id)
    return result

##
# @brief Open an SPI/JTAG connection.
#
# Open a SPI/JTAG connection using the supplied \c portConfig. You must open a connection
# before calling \c jtagShiftInOut(), \c jtagClockFSM(), \c jtagClocks(), \c spiSend() or
# \c spiRecv(). And you must close the connection when you're finished, with \c progClose().
#
# @param handle The handle returned by \c flOpen().
# @param portConfig The port bits to use for MISO(TDO), MOSI(TDI), SS(TMS) & SCK(TCK).
# @throw FLException
#     - If \c portConfig is malformed.
#     - If the micro refused to map its ports to those given.
#     - If the micro refused to configure one of its ports.
#
def progOpen(handle, portConfig):
    error = ErrorString()
    status = fpgalink.progOpen(handle, portConfig.encode('ascii'), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Close an SPI/JTAG connection.
#
# Close an SPI/JTAG connection previously opened by \c progOpen(), and tri-state the four lines.
#
# @param handle The handle returned by \c flOpen().
# @throw FLException if the micro refused to configure one of its ports.
#
def progClose(handle):
    error = ErrorString()
    status = fpgalink.progClose(handle, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

# Helper function: return the number of bytes needed to store x bits
def _bitsToBytes(x):
    return (x >> 3) if ( x & 7 == 0 ) else (x >> 3) + 1

##
# @brief Shift data into and out of the JTAG state-machine.
#
# Shift \c numBits bits from \c inData into TDI, at the same time shifting the same number of
# bits from TDO into a \c bytearray, to be returned. If \c isLast is \c True, leave the TAP
# state-machine in \c Shift-xR, otherwise \c Exit1-xR. If you want \c inData to be all zeros
# you can use \c Shift.ZEROS, or if you want it to be all ones you can use \c Shift.ONES,
# otherwise you can pass in explicit data in the form of a \c bytes instance or a
# \c bytearray instance. Each byte is sent in order, LSB-first. The TDO data is returned as
# a \c bytearray, in order, LSB-first.
#
# @param handle The handle returned by \c flOpen().
# @param numBits The number of bits to clock into the JTAG state-machine.
# @param inData The source data, or \c Shift.ZEROS or \c Shift.ONES.
# @param isLast Either \c False to remain in \c Shift-xR, or \c True to exit to \c Exit1-xR.
# @returns A \c bytearray containing the TDO data.
# @throw FLException
#     - If the micro refused to accept programming data.
#     - If the micro refused to provide programming data.
#     - If the micro refused to begin a JTAG shift operation.
#
def jtagShiftInOut(handle, numBits, inData, isLast = False):
    numBytes = _bitsToBytes(numBits)
    BufType = uint8*numBytes
    if ( not isinstance(inData, c_char_p) ):
        if ( numBytes != len(inData) ):
            raise FLException("Expecting %d bytes inData" % numBytes)
        if ( isinstance(inData, bytearray) ):
            inData = BufType.from_buffer(inData)
        inData = cast(inData, c_char_p)
    outData = bytearray(numBytes)
    outDataBuf = BufType.from_buffer(outData)
    error = ErrorString()
    status = fpgalink.jtagShift(
        handle, numBits, inData, outDataBuf, 0x01 if isLast else 0x00, error)
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    return outData

##
# @brief Shift data into the JTAG state-machine.
#
# Shift \c numBits bits from \c inData into TDI, throwing away the bits clocked out of TDO.
# If \c isLast is \c True, leave the TAP state-machine in \c Shift-xR, otherwise \c Exit1-xR.
# If you want \c inData to be all zeros you can use \c Shift.ZEROS, or if you want it to be
# all ones you can use \c Shift.ONES, otherwise you can pass in explicit data in the form of
# a \c bytes instance or a \c bytearray instance. Each byte is sent in order, LSB-first.
#
# @param handle The handle returned by \c flOpen().
# @param numBits The number of bits to clock into the JTAG state-machine.
# @param inData The source data, or \c Shift.ZEROS or \c Shift.ONES.
# @param isLast Either \c False to remain in \c Shift-xR, or \c True to exit to \c Exit1-xR.
# @returns A \c bytearray containing the TDO data.
# @throw FLException
#     - If the micro refused to accept programming data.
#     - If the micro refused to provide programming data.
#     - If the micro refused to begin a JTAG shift operation.
#
def jtagShiftInOnly(handle, numBits, inData, isLast = False):
    numBytes = _bitsToBytes(numBits)
    BufType = uint8*numBytes
    if ( not isinstance(inData, c_char_p) ):
        if ( numBytes != len(inData) ):
            raise FLException("Expecting %d bytes inData" % numBytes)
        if ( isinstance(inData, bytearray) ):
            inData = BufType.from_buffer(inData)
        inData = cast(inData, c_char_p)
    error = ErrorString()
    status = fpgalink.jtagShift(
        handle, numBits, inData, None, 0x01 if isLast else 0x00, error)
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Clock \c transitionCount bits from \c bitPattern into TMS, starting with the LSB.
#
# Navigate the TAP state-machine by clocking an arbitrary sequence of bits into TMS.
#
# @param handle The handle returned by \c flOpen().
# @param bitPattern The pattern of bits to clock into TMS, LSB first.
# @param transitionCount The number of bits to clock.
# @throw FLException if the micro refused to navigate the TAP state-machine.
#
def jtagClockFSM(handle, bitPattern, transitionCount):
    error = ErrorString()
    status = fpgalink.jtagClockFSM(handle, bitPattern, transitionCount, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Toggle TCK \c numClocks times.
#
# Put \c numClocks clocks out on TCK.
#
# @param handle The handle returned by \c flOpen().
# @param numClocks The number of clocks to put out on TCK.
# @throw FLException if the micro refused to send JTAG clocks.
#
def jtagClocks(handle, numClocks):
    error = ErrorString()
    status = fpgalink.jtagClocks(handle, numClocks, byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Get the physical port and port-bit of the specified logical port.
#
# Get the physical port and bit numbers assigned to the specified logical port by the
# preceding call to \c progOpen(). This is just a convenience function to avoid re-parsing
# the port config, which is typically supplied by the user as a string. For example, to send
# data to a SPI peripheral, you'll probably want to assert \c SS. So you'll want to call
# \c progGetPort(handle, LogicalPort.SS) to find out which physical port and bit \c SS was
# assigned to. If it was assigned to port D7, this function will return (3, 7).
#
# @param handle The handle returned by \c flOpen().
# @param logicalPort The \c LogicalPort to query for.
# @returns A tuple pair of (physicalPort, physicalBit) mapped to the given \c LogicalPort.
#
def progGetPort(handle, logicalPort):
    return (
        fpgalink.progGetPort(handle, logicalPort),
        fpgalink.progGetBit(handle, logicalPort)
    )

##
# @brief Send a number of whole bytes over SPI, either LSB-first or MSB-first.
#
# Shift \c buf into the microcontroller's SPI bus (if any), either MSB-first or LSB-first. You
# must have previously called \c progOpen().
#
# @param handle The handle returned by \c flOpen().
# @param buf The bytes to send (either \c bytes or \c bytearray).
# @param bitOrder Either \c BitOrder.MSBFIRST or \c BitOrder.LSBFIRST.
# @throw FLException
#     - If there was a memory allocation failure.
#     - If the device does not support SPI.
#     - If USB communications failed whilst sending the data.
#
def spiSend(handle, buf, bitOrder):
    numBytes = len(buf)
    if ( isinstance(buf, bytearray) ):
        buf = BufType.from_buffer(buf)
        buf = cast(buf, c_char_p)
    error = ErrorString()
    status = fpgalink.spiSend(
        handle, numBytes, buf, bitOrder, error)
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Receive a number of whole bytes over SPI, either LSB-first or MSB-first.
#
# Return (as a \c bytearray) \c numBytes bytes shifted out of the microcontroller's SPI bus,
# either MSB-first or LSB-first. You must have previously called \c progOpen().
#
# @param handle The handle returned by \c flOpen().
# @param numBytes The number of bytes to receive.
# @param bitOrder Either \c BitOrder.MSBFIRST or \c BitOrder.LSBFIRST.
# @throw FLException
#     - If the device does not support SPI.
#     - If USB communications failed whilst receiving the data.
#
def spiRecv(handle, numBytes, bitOrder):
    BufType = uint8*numBytes
    recvData = bytearray(numBytes)
    recvDataBuf = BufType.from_buffer(recvData)
    error = ErrorString()
    status = fpgalink.spiRecv(
        handle, numBytes, recvDataBuf, bitOrder, error)
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    return recvData
# @}

##
# @name Firmware Operations
# @{

##
# @brief Load standard \b FPGALink firmware into the FX2's RAM.
#
# Load the FX2 chip at the "current" VID/PID with a precompiled firmware such that it will
# renumerate as the "new" VID/PID. The firmware is loaded into RAM, so the change is not
# permanent. Typically after calling \c flLoadStandardFirmware() applications should wait for
# the renumeration to complete by calling \c flIsDeviceAvailable() repeatedly until the "new"
# VID/PID becomes active.
#
# @param curVidPid The current Vendor/Product (i.e VVVV:PPPP) of the FX2 device.
# @param newVidPid The Vendor/Product/Device (i.e VVVV:PPPP:DDDD) that you \b want the FX2
#            device to renumerate as.
# @throw FLException
#     - If one of the VID/PIDs was invalid or the current VID/PID was not found.
#     - If there was a problem talking to the FX2.
#     - If there was a memory allocation failure.
#
def flLoadStandardFirmware(curVidPid, newVidPid):
    error = ErrorString()
    status = fpgalink.flLoadStandardFirmware(curVidPid.encode('ascii'), newVidPid.encode('ascii'), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Flash standard FPGALink firmware into the FX2's EEPROM.
#
# @warning This function will make permanent changes to your hardware. Remember to make a
# backup copy of the existing EEPROM firmware with \c flSaveFirmware() before calling it.
#
# Overwrite the FX2's EEPROM with a precompiled FPGALink firmware such that the board will
# enumerate on power-on with the "new" Vendor/Product/Device IDs.
#
# @param handle The handle returned by \c flOpen().
# @param newVidPid The Vendor/Product/Device (i.e VVVV:PPPP:DDDD) you want the FX2 to
#            enumerate as on power-on.
# @throw FLException
#     - \c If there was a memory allocation failure.
#     - \c If the VID:PID was invalid.
#     - \c If there was a problem talking to the FX2.
#
def flFlashStandardFirmware(handle, newVidPid):
    error = ErrorString()
    status = fpgalink.flFlashStandardFirmware(handle, newVidPid.encode('ascii'), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Load custom firmware (<code>.hex</code>) into the FX2's RAM.
#
# Load the FX2 chip at the given VID:PID with a <code>.hex</code> firmware file. The firmware
# is loaded into RAM, so the change is not permanent.
#
# @param curVidPid The current Vendor/Product (i.e VVVV:PPPP) of the FX2 device.
# @param fwFile A <code>.hex</code> file containing new FX2 firmware to be loaded into the
#            FX2's RAM.
# @throw FLException
#     - If there was a memory allocation failure.
#     - If the VID:PID was invalid.
#     - If there was a problem talking to the FX2.
#     - If \c fwFile has a bad extension or could not be loaded.
#
def flLoadCustomFirmware(curVidPid, fwFile):
    error = ErrorString()
    status = fpgalink.flLoadCustomFirmware(curVidPid.encode('ascii'), fwFile.encode('ascii'), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

##
# @brief Flash a custom firmware from a file into the FX2's EEPROM.
#
# @warning This function will make permanent changes to your hardware. Remember to make a
# backup copy of the existing EEPROM firmware with \c flSaveFirmware() before calling it.
#
# Overwrite the FX2's EEPROM with a custom firmware from a <code>.hex</code> or
# <code>.iic</code> file.
#
# @param curVidPid The current Vendor/Product (i.e VVVV:PPPP) of the FX2 device.
# @param fwFile A <code>.hex</code> or <code>.iic</code> file containing new FX2 firmware to be
#            loaded into the FX2's EEPROM.
# @throw FLException
#     - If there was a memory allocation failure.
#     - If there was a problem talking to the FX2.
#     - If the firmware file could not be loaded.
#
def flFlashCustomFirmware(curVidPid, fwFile):
    error = ErrorString()
    status = fpgalink.flFlashCustomFirmware(curVidPid.encode('ascii'), fwFile.encode('ascii'), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)

# @}

##
# @name Utility Functions
# @{

##
# @brief Sleep for the specified number of milliseconds.
#
# @param ms The number of milliseconds to sleep.
#
def flSleep(ms):
    fpgalink.flSleep(ms)

##
# @brief Configure a single port bit on the microcontroller.
#
# With this function you can set a single microcontroller port bit to either \c PIN_INPUT,
# \c PIN_HIGH or \c PIN_LOW, and read back the current state of the bit.
#
# @param handle The handle returned by \c flOpen().
# @param portNumber Which port to configure (i.e 0=PortA, 1=PortB, 2=PortC, etc).
# @param bitNumber The bit within the chosen port to use.
# @param pinConfig Either \c PinConfig.INPUT, \c PinConfig.HIGH or \c PinConfig.LOW.
# @returns True if the pin is currently high, else False.
# @throw FLException if the micro failed to respond to the port access command.
#
def flSingleBitPortAccess(handle, portNumber, bitNumber, pinConfig):
    error = ErrorString()
    bitRead = uint8()
    status = fpgalink.flSingleBitPortAccess(handle, portNumber, bitNumber, pinConfig, byref(bitRead), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    return False if bitRead.value == 0 else True

##
# @brief Configure multiple port bits on the microcontroller.
#
# With this function you can set multiple microcontroller port bits to either \c PinConfig.INPUT,
# \c PinConfig.HIGH or \c PinConfig.LOW, and read back the current state of each bit. This is
# achieved by sending a comma-separated list of port configurations, e.g "A12-,B2+,C7?". A "+"
# or a "-" suffix sets the port as an output, driven high or low respectively, and a "?" suffix
# sets the port as an input. The current state of up to 32 bits are returned in \c readState,
# LSB first.
#
# @param handle The handle returned by \c flOpen().
# @param portConfig A comma-separated sequence of port configurations.
# @returns The ports, read back in order, LSB first.
# @throw FLException
#     - If the port access command completed successfully.
#     - If \c portConfig is malformed.
#     - If the micro failed to respond to the port access command.
#
def flMultiBitPortAccess(handle, portConfig):
    error = ErrorString()
    readState = uint32()
    status = fpgalink.flMultiBitPortAccess(handle, portConfig.encode('ascii'), byref(readState), byref(error))
    if ( status != FL_SUCCESS ):
        s = str(error.value)
        fpgalink.flFreeError(error)
        raise FLException(s)
    return readState.value
# @}

flInitialise(0)
