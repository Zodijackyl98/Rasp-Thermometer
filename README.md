# Rasp-Thermometer
Converts analog signal coming from simple thermistor into digital signal by using 8bit ADS7830 ADC.

Whole process can be seen via LCD screen that refreshes in given sample rate. Temperature values from the sensor,CPU temperature and up time parameters can be seen on the screen according to default settings. 
Creates csv file after reaching given sample count.

Optionally, you can uncomment the rows that are used to control 4 LEDs. 3 of them are used to give user the information about temperature change, is it rising, decreasing or remaining still. The last one just tells the user that csv file has succesfully been written. GPIO pin numbers can be found in channel list variable. 
