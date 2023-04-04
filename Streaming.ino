#include <Wire.h>

#include "SparkFun_BNO080_Arduino_Library.h" // Click here to get the library: http://librarymanager/All#SparkFun_BNO080
BNO080 myIMU;


void setup()
{
  Serial.begin(115200);

  Wire.begin(); 

  myIMU.begin();

  Wire.setClock(400000); //Increase I2C data rate to 400kHz

  myIMU.enableAccelerometer(100); //Send data update every 100ms
}

void loop()
{
  //Look for reports from the IMU
  if (myIMU.dataAvailable() == true)
  {
    float x = myIMU.getAccelX();
    
  float resultant = abs(x*x); //squaring x to amplify true steps (big peaks) while keeping noise small (small peaks)


    Serial.print(resultant, 4); //export/print resultant to 4 decimal places to serial (usb port)
    Serial.println(); //do the print 
  }

}
