#include "Tlc5940.h"

int channelIntensity[20];

void setup()
{
  Serial.begin(57600);
  Serial.setTimeout(100);
  Tlc.init();
  for (byte i = 0; i < 20; i++)
  { 
    Tlc.set(i, 1600);
    Tlc.update();
    delay(10);
    channelIntensity[i] = 1600;
  }
}

void loop()
{
  int channel = -1;
  int intensity = -1;
  Serial.println("Enter command:");
  while (Serial.available() == 0);
  if (Serial.peek() > '9') 
  {
    char command = Serial.read();
    switch (command)
    {
      case 'p':
        for (byte i = 0; i < 20; i++)
        {
          Serial.print(i);
          Serial.print(": ");
          Serial.println(channelIntensity[i]);
        }
        return;
      case 'z':
        for (byte i = 0; i < 20; i++)
        {
          Tlc.set(i, 0);
          Tlc.update();
          delay(10);
          channelIntensity[i] = 0;
        }
        Serial.println("All channels cleared.");
        return;
      case 'm':
        for (byte i = 0; i < 20; i++)
        { 
          Tlc.set(i, 4095);
          Tlc.update();
          delay(10);
          channelIntensity[i] = 4095;
        }
        Serial.println("All channels maxed.");
        return;
      case 'a':
        Serial.println("Enter new value for all channels:");
        while (Serial.available() == 0);
        intensity = Serial.parseInt();
        if ((intensity > 4095) || (intensity < 0)) 
        {
          Serial.println("Value not in range!");
          return;
        }
        for (byte i = 0; i < 20; i++)
        {
          Tlc.set(i, intensity);
          Tlc.update();
          delay(10);
          channelIntensity[i] = intensity;
        }
        Serial.print("All channels set to: ");
        Serial.println(intensity);
        return;
      default:
        return;      
    }
  }
  else
  {
    channel = Serial.parseInt();
  }
  if ((channel > 19) || (channel < 0))
  {
    Serial.println("Channel not in range!");
    return;
  }
  
  Serial.println("Enter new value:");
  while (Serial.available() == 0);
  intensity = Serial.parseInt();
  if ((intensity > 4095) || (intensity < 0)) 
  {
    Serial.println("Value not in range!");
    return;
  }
  channelIntensity[channel] = intensity;
  
  Tlc.set(channel, intensity);
  Tlc.update();
}
