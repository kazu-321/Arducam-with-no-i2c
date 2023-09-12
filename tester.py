import board
import busio
import bitbangio
import time as utime
import digitalio
from OV2640_reg import *
from OV5642_reg import *

OV2640=0
OV5642=1

MAX_FIFO_SIZE=0x7FFFFF
ARDUCHIP_FRAMES=0x01
ARDUCHIP_TIM=0x03
VSYNC_LEVEL_MASK=0x02
ARDUCHIP_TRIG=0x41
CAP_DONE_MASK=0x08

OV5642_CHIPID_HIGH=0x300a
OV5642_CHIPID_LOW=0x300b

OV2640_160x120  =0
OV2640_176x144  =1
OV2640_320x240  =2
OV2640_352x288  =3
OV2640_640x480  =4
OV2640_800x600  =5
OV2640_1024x768 =6
OV2640_1280x1024=7
OV2640_1600x1200=8

OV5642_320x240  =0
OV5642_640x480  =1
OV5642_1024x768 =2
OV5642_1280x960 =3
OV5642_1600x1200=4
OV5642_2048x1536=5
OV5642_2592x1944=6
OV5642_1920x1080=7

Advanced_AWB =0
Simple_AWB   =1
Manual_day   =2
Manual_A     =3
Manual_cwf   =4
Manual_cloudy=5


degree_180=0
degree_150=1
degree_120=2
degree_90 =3
degree_60 =4
degree_30 =5
degree_0  =6
degree30  =7
degree60  =8
degree90  =9
degree120 =10
degree150 =11

Auto   =0
Sunny  =1
Cloudy =2
Office =3
Home   =4

Antique     =0
Bluish      =1
Greenish    =2
Reddish     =3
BW          =4
Negative    =5
BWnegative  =6
Normal      =7
Sepia       =8
Overexposure=9
Solarize    =10
Blueish     =11
Yellowish   =12

Exposure_17_EV  =0
Exposure_13_EV  =1
Exposure_10_EV  =2
Exposure_07_EV  =3
Exposure_03_EV  =4
Exposure_default=5
Exposure03_EV   =6
Exposure07_EV   =7
Exposure10_EV   =8
Exposure13_EV   =9
Exposure17_EV   =10

Auto_Sharpness_default=0
Auto_Sharpness1       =1
Auto_Sharpness2       =2
Manual_Sharpnessoff   =3
Manual_Sharpness1     =4
Manual_Sharpness2     =5
Manual_Sharpness3     =6
Manual_Sharpness4     =7
Manual_Sharpness5     =8

MIRROR     =0
FLIP       =1
MIRROR_FLIP=2

Saturation4 =0
Saturation3 =1
Saturation2 =2
Saturation1 =3
Saturation0 =4
Saturation_1=5
Saturation_2=6
Saturation_3=7
Saturation_4=8

Brightness4 =0
Brightness3 =1
Brightness2 =2
Brightness1 =3
Brightness0 =4
Brightness_1=5
Brightness_2=6
Brightness_3=7
Brightness_4=8

Contrast4 =0
Contrast3 =1
Contrast2 =2
Contrast1 =3
Contrast0 =4
Contrast_1=5
Contrast_2=6
Contrast_3=7
Contrast_4=8

Antique      = 0
Bluish       = 1
Greenish     = 2
Reddish      = 3
BW           = 4
Negative     = 5
BWnegative   = 6
Normal       = 7
Sepia        = 8
Overexposure = 9
Solarize     = 10
Blueish      = 11
Yellowish    = 12

high_quality   =0
default_quality=1
low_quality    =2

Color_bar   =0
Color_square=1
BW_square   =2
DLI         =3

BMP =0
JPEG=1
RAW =2

class ArducamClass(object):
    def __init__(self,Type):
        self.CameraMode=JPEG
        self.CameraType=Type
        self.SPI_CS=digitalio.DigitalInOut(board.GP5)
        self.SPI_CS.direction = digitalio.Direction.OUTPUT
        self.I2cAddress=0x30
        self.spi = busio.SPI(clock=board.GP2, MOSI=board.GP3, MISO=board.GP4)
        while not self.spi.try_lock():
            pass
        self.spi.configure(baudrate=4000000,polarity=0,phase=0,bits=8)
        self.i2c = bitbangio.I2C(scl=board.GP9, sda=board.GP8,frequency=1000000)        
        while not self.i2c.try_lock():
            pass
        print(self.i2c.scan()) # -> []
        self.Spi_write(0x07,0x80)
        utime.sleep(0.1)
        self.Spi_write(0x07,0x00)
        utime.sleep(0.1)
        
            
    def Set_Camera_mode(self,mode):
        self.CameraMode=mode
    
    def Spi_Test(self):
        while True:
            self.Spi_write(0X00,0X56)
            value=self.Spi_read(0X00)
            if(value[0]==0X56):
                print('SPI interface OK')
                break
            else:
                print('SPI interface Error')
            utime.sleep(1)

        
    def Spi_write(self,address,value):
        maskbits = 0x80
        buffer=bytearray(2)
        buffer[0]=address | maskbits
        buffer[1]=value
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        self.SPI_CS_HIGH()
        
    def Spi_read(self,address):
        maskbits = 0x7f
        buffer=bytearray(1)
        buffer[0]=address & maskbits
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        self.spi_readinto(buffer)
        self.SPI_CS_HIGH()
        return buffer

    def spi_write(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.spi.write(buf, start=start, end=end)

    def spi_readinto(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.spi.readinto(buf, start=start, end=end)
        
    def get_bit(self,addr,bit,p=0):
        value=self.Spi_read(addr)[p]
        return value&bit
  
    def SPI_CS_LOW(self):
        self.SPI_CS.value=False
        
    def SPI_CS_HIGH(self):
        self.SPI_CS.value=True
        
    def set_fifo_burst(self):
        buffer=bytearray(1)
        buffer[0]=0x3c
        self.spi.write(buffer, start=0, end=1)
        
    def clear_fifo_flag(self):
        self.Spi_write(0x04,0x01)
        
    def flush_fifo(self):
        self.Spi_write(0x04,0x01)
        
    def start_capture(self):
        self.Spi_write(0x04,0x02)
        
    def read_fifo_length(self):
        len1=self.Spi_read(0x42)[0]
        len2=self.Spi_read(0x43)[0]
        len3=self.Spi_read(0x44)[0]
        len3=len3 & 0x7f
        lenght=((len3<<16)|(len2<<8)|(len1))& 0x07fffff
        return lenght
    
            
    def set_format(self,mode):
        if mode==BMP or mode==JPEG or mode==RAW:   
            self.CameraMode=mode
            
    def set_bit(self,addr,bit):
        temp=self.Spi_read(addr)[0]
        self.Spi_write(addr,temp&(~bit))
    


import usb_cdc

once_number=128
mode = 0
start_capture = 0
stop_flag=0
data_in=0
value_command=0
flag_command=0
buffer=bytearray(once_number)

mycam = ArducamClass(OV2640)
mycam.Spi_Test()
utime.sleep(1)
mycam.clear_fifo_flag()


def read_fifo_burst():
    count=0
    lenght=mycam.read_fifo_length()
    mycam.SPI_CS_LOW()
    mycam.set_fifo_burst()
    while True:
        mycam.spi.readinto(buffer,start=0,end=once_number)
        usb_cdc.data.write(buffer)
        utime.sleep(0.00015)
        count+=once_number
        if count+once_number>lenght:
            count=lenght-count
            mycam.spi.readinto(buffer,start=0,end=count)
            usb_cdc.data.write(buffer)
            mycam.SPI_CS_HIGH()
            mycam.clear_fifo_flag()
            break
    
while True:
    if usb_cdc.data.in_waiting > 0:
        value_command = usb_cdc.data.read()
        flag_command=1
    if flag_command==1:
        flag_command=0
        print(value_command)
        value=int.from_bytes(value_command,"big")
        if value==0x10:
            print("capture")
            mode=1
            start_capture=1
        elif value==0x11:
            mycam.set_format(JPEG)
            mycam.Camera_Init()
            mycam.set_bit(ARDUCHIP_TIM,VSYNC_LEVEL_MASK)
        elif value==0x20:
            mode=2
            start_capture=2
            stop_flag=0
        elif value==0x21:
            stop_flag=1
        elif value==0x30:
            mode=3
            start_capture=3

    if mode==1:
        if start_capture==1:
            mycam.flush_fifo();
            mycam.clear_fifo_flag();
            mycam.start_capture();
            start_capture=0
            print("start capture")
            print(mycam.get_bit(ARDUCHIP_TRIG,CAP_DONE_MASK))
        if mycam.get_bit(ARDUCHIP_TRIG,CAP_DONE_MASK)!=0:
            print("end capture")
            read_fifo_burst()
            mode=0       
    elif mode==2:
        if stop_flag==0:
            if start_capture==2:
                start_capture=0
                mycam.flush_fifo();
                mycam.clear_fifo_flag();
                mycam.start_capture();
            if mycam.get_bit(ARDUCHIP_TRIG,CAP_DONE_MASK)!=0:
                read_fifo_burst()
                start_capture=2
        else:
            mode=0
            start_capture=0










