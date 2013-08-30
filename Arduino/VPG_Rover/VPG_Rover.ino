/***********************************************************************
VPG_Rover

Created 22 Aug 2013 by Mike Hord @ SparkFun Electronics.

This code is beerware- feel free to make use of it, with or without
attribution, in your own projects. If you find it helpful, buy me a beer
the next time you see me at the local- or better yet, shop SparkFun!

This sketch uses the RedBot hardware to implement a remote controlled
rover that takes its marching orders from the VPG central processor.

See github.com/mhord/vpg for more information; I'm going to assume you
are familiar with the basic structure of the VPG throughout this code.
***********************************************************************/
// Include the libraries. We make a provision for using the Xbee header
//  via software serial to report values, but that's not really used in
//  the code anywhere.
#include <RedBot.h>
#include <SoftwareSerial.h>

// Instantiate the encoder. This includes motor control, as well. The 
//  first parameter is the pin that the left wheel encoder is
//  connected to, the second, the right wheel.
RedBotEncoder motor = RedBotEncoder(10, 11);

// Instantiate the sensors. Sensors can only be created for analog input
//  pins; the Xbee software serial uses pins A0 and A1.
RedBotSensor lSen = RedBotSensor(A3);
RedBotSensor cSen = RedBotSensor(A6);
RedBotSensor rSen = RedBotSensor(A7);

// Create a software serial connection. See the Arduino documentation
//  for more information about this. The pins used here are the hard
//  wired pins the Xbee header connects to.
SoftwareSerial xbee(15, 14);

// Setup is a barebones thing for this sketch- activate the serial stuff and greet
//  the morning sun for sanity checking sake.
void setup()
{
  Serial.begin(57600);
  xbee.begin(9600);
  Serial.println("Hello world!");
}

#define MOVE_SPEED 255   // Just in case I decide to change the speed of motions
                         //  later. This is the speed of *all* move commands.

// Loop buffers up to 7 commands (the VPG's camera can only hold up to 6 command
//  tiles in the FOV at once, and that only when you arrange the train diagonally),
//  and when it receives an 'x' from the control unit, it triggers the rover to
//  carry out the commands.
void loop()
{
  // static variables because we want them to persist between iterations of loop
  static char commandBuffer[8];  // This is (obvi) the buffer for incoming data.
  static char bufferTop=0;       // This is the pointer to the top of the data
                                 //  buffer. This is where the next character should
                                 //  go, or, alternatively, how many characters we've
                                 //  received.
                                 
  while(xbee.available() == 0);  // Wait for data on the xbee serial port.
  commandBuffer[bufferTop] = xbee.read(); // Read the incoming data into the buffer.
  
  // If we've received our "end of commands" character ('x'), we should go ahead and
  //  act on those commands. More on how we do that in the executeCommandStack()
  //  function comments.
  if (commandBuffer[bufferTop++] == 'x')
  {
    executeCommandStack(commandBuffer, bufferTop);
    bufferTop = 0;
  }
} 

// executeCommandStack() unpacks the commands received from the controller and
//  performs the appropriate actions.
void executeCommandStack(char* stack, char numCommands)
{
  // Iterate over the incoming buffer.
  for (char i = 0; i < numCommands; i++)
  {
    Serial.println(stack[i]);  // For debugging.
    // This switch statement handles the movement.
    switch(stack[i])
    {
      case '0':      // Move forward one "unit", one full revolution of a wheel.
        // We use this for-loop structure because we need to be checking for an edge
        //  to the table. We *could* just move 16 ticks, but we can't interrupt when
        //  we hit the edge of the table.
        for (byte j = 0; j < 16; j++)
        {
          motor.moveTicks(1, MOVE_SPEED, false);  // Move one tick, at MOVE_SPEED,
                                                  //  then don't brake.
          if ( (rSen.read() > 350) ||  // Check each sensor to see if it's crossed a
               (lSen.read() > 350) ||  //  dark border (presumably the edge of the
               (cSen.read() > 350) )   //  table or region of safety.
          {
            motor.brake();  // If we trigger, we want to stop motion and not
            break;          //  move any more.
          }
        }
        motor.brake();  // Assuming we don't run into any issues, we'll stop motion
                        //  here, then break from the switch statement.
        break;
      // All of the motions take the same form as the first one. Not all are valid
      //  to receive from the controller; particularly the 135 degree turns and the
      //  reverse motions are excluded by not having tiles for those commands.
      case '1':      // Turn right 45 degrees.
        for (byte j = 0; j < 4; j++)
        {
          motor.pivot(1, -1*MOVE_SPEED, false);
          if ( (rSen.read() > 350) ||
               (lSen.read() > 350) ||
               (cSen.read() > 350) )
          {
            motor.brake();
            break;
          }
        }
        motor.brake();
        break;
      case '2':      // Turn right 90 degrees.
        for (byte j = 0; j < 8; j++)
        {
          motor.pivot(1, -1*MOVE_SPEED, false);
          if ( (rSen.read() > 350) ||
               (lSen.read() > 350) ||
               (cSen.read() > 350) )
          {
            motor.brake();
            break;
          }
        }
        motor.brake();
        break;
      case '3':      // Turn right 135 degrees.
        for (byte j = 0; j < 12; j++)
        {
          motor.pivot(1, -1*MOVE_SPEED, false);
          if ( (rSen.read() > 350) ||
               (lSen.read() > 350) ||
               (cSen.read() > 350) )
          {
            motor.brake();
            break;
          }
        }
        motor.brake();
        break;
      case '4':      // Reverse one "unit".
        for (byte j = 0; j < 16; j++)
        {
          motor.moveTicks(1, -1*MOVE_SPEED, false);
          if ( (rSen.read() > 350) ||
               (lSen.read() > 350) ||
               (cSen.read() > 350) )
          {
            motor.brake();
            break;
          }
        }
        motor.brake();
        break;
      case '5':      // Turn 135 degrees left
        for (byte j = 0; j < 12; j++)
        {
          motor.pivot(1, MOVE_SPEED, false);
          if ( (rSen.read() > 350) ||
               (lSen.read() > 350) ||
               (cSen.read() > 350) )
          {
            motor.brake();
            break;
          }
        }
        motor.brake();
        break;
      case '6':      // Turn 90 degrees left
        for (byte j = 0; j < 8; j++)
        {
          motor.pivot(1, MOVE_SPEED, false);
          if ( (rSen.read() > 350) ||
               (lSen.read() > 350) ||
               (cSen.read() > 350) )
          {
            motor.brake();
            break;
          }
        }
        motor.brake();
        break;
      case '7':      // Turn 45 degrees left.
        for (byte j = 0; j < 4; j++)
        {
          motor.pivot(1, MOVE_SPEED, false);
          if ( (rSen.read() > 350) ||
               (lSen.read() > 350) ||
               (cSen.read() > 350) )
          {
            motor.brake();
            break;
          }
        }
        motor.brake();
        break;
      default:       // Something else...
        commandError();
        break;
    }
    delay(500);
  }
}

// Someday, maybe, I'll add some error handling here. Today is not that day.
void commandError()
{
}
