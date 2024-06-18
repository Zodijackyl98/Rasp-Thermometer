import RPi.GPIO as GPIO
import math
from ADCDevice import *

import pandas as pd
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from datetime import datetime
import time

GPIO.setmode(GPIO.BOARD)

channel_list = [37,40,38,7] #RGBY 
GPIO.setup(channel_list, GPIO.OUT)

adc = ADCDevice() # Define an ADCDevice class object

def setup():
    global adc
    if(adc.detectI2C(0x48)): # Detect the pcf8591.
        adc = PCF8591()
    elif(adc.detectI2C(0x4b)): # Detect the ads7830
        adc = ADS7830()
    else:
        print("No correct I2C address found, \n"
        "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
        "Program Exit. \n");
        exit(-1)
        
def loop():
    time_format = "%Y-%m-%dT%H:%M:%S.%f"
    start_time = datetime.strptime(datetime.now().isoformat(), time_format)
    temp_list = []
    initial_temp = 25
    temp_list.append(initial_temp)
    time_list = []
    cpu_temp_list = []
    adc_list = []
    voltage_list = []
    voltage_list_ = []
    rt_list = []

    i = 0 #Initial Value

    mcp.output(3,1)     # turn on LCD backlight
    lcd.begin(16,2)     # set number of LCD lines and columns
    while True:
        value = adc.analogRead(0)        # read ADC value A0 pin
        value_ = adc.analogRead(1)       # read ADC value A1 pin
        voltage = value / 255.0 * 3.3        # calculate voltage
        voltage_ = round(value_ / 255.0 * 3.3, 3)      # calculate voltage
        Rt = 10 * voltage / (3.3 - voltage)    # calculate resistance value of thermistor
        tempK = 1/(1/(273.15 + 25) + math.log(Rt/10)/3950.0) # calculate temperature (Kelvin)
        tempC = round(tempK -273.15, 3)        # calculate temperature (Celsius)
        
        temp_list.append(tempC)
        time_list.append(datetime.now().isoformat())
        adc_list.append(round(value, 3))
        rt_list.append(Rt)
        voltage_list.append(voltage)
        voltage_list_.append(voltage_)
        cpu_temp_list.append(get_cpu_temp()[:-2])

        end_time = datetime.strptime(datetime.now().isoformat(), time_format)
        time_gap = str(end_time - start_time).split(':')[0] + ':' + \
		   str(end_time - start_time).split(':')[1] + ':' + \
		   str(end_time - start_time).split(':')[2].split('.')[0] 

        # print(temp_list, "i = ", i)

        # if len(temp_list) >= 2:
        fark = temp_list[i] - temp_list[i-1]
        # print ('ADC Value : %d, Voltage : %.2f, Temperature : %.2f Temp_list[i] : %.2f'%(value,voltage,tempC, temp_list[-1]))
            
        lcd.setCursor(col = 0,row = 0)  # set cursor position
        lcd.message(str(str(tempC)+  '&' + get_cpu_temp()[:-2]).center(16, ' ')) # get_cpu_temp()[:-2], 'A1:' + str(voltage_)
            
        lcd.setCursor(col = 0, row = 1)
        lcd.message(str('UT :' + time_gap).center(16, ' '))

        time.sleep(1)

        i += 1

        # if fark > 0.0:
        #     GPIO.output(channel_list[0], GPIO.HIGH)
        #     # print('RED')
        # if fark == 0.0:
        #     GPIO.output(channel_list[2], GPIO.HIGH)
        #     # print('BLUE')
           
        # if fark < 0.0:
        #     GPIO.output(channel_list[1], GPIO.HIGH)
        #     # print('GREEN')
           

        # lcd.setCursor(col = 0, row = 1)
        # lcd.leftToRight()
        # lcd.scrollDisplayRight()
        # lcd.setCursor(col = 0, row = 0)

        if len(time_list) == 10000:
            GPIO.output(channel_list, GPIO.LOW)
            return [time_list, temp_list, cpu_temp_list, adc_list, voltage_list, rt_list, time_gap]
        

def get_cpu_temp():     # get CPU temperature from file "/sys/class/thermal/thermal_zone0/temp"
    tmp = open('/sys/class/thermal/thermal_zone0/temp')
    cpu = tmp.read()
    tmp.close()
    return '{:.2f}'.format( float(cpu)/1000 ) + ' C'
 
def get_time_now():     # get system time
    return datetime.now().strftime('    %H:%M:%S')

def destroy():
    adc.close()
    GPIO.cleanup()
    lcd.clear()
    
def log(Time, temp, cpu_temp, ADC_Value, Voltage, Rt, up_time):
    df = pd.DataFrame(columns = ['Time','Room Temp','CPU Temp', 'ADC Value', 'Voltage', 'Rt'])
    time_format = "%Y-%m-%dT%H:%M:%S.%f"
    log_std_dir = "./"
    log_std_text = "Temp_log_"
    log_time_format = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day) + '_' +str(datetime.now().hour)+ '-' + str(datetime.now().minute)
    df['Time'] = [datetime.strptime(i, time_format) for i in Time]
    df['Room Temp'] = temp[1:] #exclude Initial Value
    df['CPU Temp'] = cpu_temp
    df['ADC Value'] = ADC_Value
    df['Voltage'] = Voltage
    df['Rt'] = Rt
    GPIO.output(7, GPIO.HIGH)
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.message(log_time_format.center(16, ' '))
    lcd.setCursor(0, 1)
    lcd.message(up_time.center(16, ' '))
    df.to_csv(log_std_dir + log_std_text + log_time_format + ".txt", header = True, sep = '\t', index = False)
    time.sleep(10)
    GPIO.output(7, GPIO.LOW)
    GPIO.cleanup()
    lcd.clear()

PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.

try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Address Error !')
        exit(1)

lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

if __name__ == '__main__':  # Program entrance
    print ('Program is starting ... ')
    setup()
    try:
        s = loop()

        log(Time = s[0], 
            temp = s[1], 
            cpu_temp = s[2],
            ADC_Value = s[3],
            Voltage = s[4], 
            Rt = s[5],
            up_time = s[6]
            ) 

    except KeyboardInterrupt: # Press ctrl-c to end the program  
        destroy()
        
    
