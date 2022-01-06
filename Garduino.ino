/****************************************************
 * File         : Gardino.ino
 * Description  : Simple program for reading moisture, temp & light and writing to LCD
 * Author       : Rowland Marshall
 * 
 * Versions     :
 *    1.01 | 
 *    1.00 | 2020-08-08 16:39:46 |  Promoted v0.06 to v1.00!
 *                                  Moisture level is unverified but works and is conservative
 *    0.06 | 2020-08-08 09:43:36 |  Added pumping and waiting conditions
 *                                  Added pumping icon/animation
 *    0.05 | 2020-08-02 16:57:56 |  Changed serial messages to csv format
 *                                  Changed wait time to 30 seconds
 *    0.04 | 2020-07-27 17:37:09 |  Added serial message for Watering on/off
 *    0.03 | 2020-07-27 17:19:05 |  Pump is functional and triggered by the moisture voltage
 *    0.02 | 2020-07-27 14:08:02 |  Convert temp voltage to real temp
 *                                  Publish figures to serial
 *                                  Moved global variables to loop local
 *    0.01 | 2020-07-27 13:51:58 |  initial building testing showing only voltages
 ****************************************************/

// Load the LiquidCrystal library, which will give us commands to interface to the LCD:
#include <LiquidCrystal.h>

// Initialize the library with the pins we're using. See http://arduino.cc/en/Reference/LiquidCrystal
LiquidCrystal lcd(12,11,5,4,3,2);

// Setup pins
const int MoisturePin = 0;  // moisture sensor A0
const int TempPin = 1;      // temperature sensor A1
const int LightPin = 2;     // light sensor A2
const int RelayPin = 7;	    // use this pin to drive the relay that turns on the pump D7
const float Waterlevel = 2.15; // this will be used as the toggle point vs moisture for the relay
const int PumpIntervalOn = 30; // 1 seconds current time spent pumping water
const int PumpIntervalWait = 300; // 1 seconds current time spent pumping water
const int CycleWaitDelay = 1000; // 1/1000 seconds current time spent pumping water
// Make custom characters:

byte Heart[] = { // Byte 0
  B00000,
  B01010,
  B11111,
  B11111,
  B01110,
  B00100,
  B00000,
  B00000
};

byte EmptyHeart[] = { // Byte 1
  B00000,
  B01010,
  B10101,
  B10001,
  B01010,
  B00100,
  B00000,
  B00000
};

byte PumpingA[] = { // Byte 2
  B00100,
  B00100,
  B01010,
  B01010,
  B10001,
  B10001,
  B11111,
  B01110
};

byte PumpingB[] = { // Byte 3
  B00100,
  B00100,
  B01010,
  B01010,
  B10001,
  B11111,
  B11111,
  B01110
};

  // Initialise pump timing variables
  int timePumping = PumpIntervalOn; // seconds interval pumping
  int waitPumping = PumpIntervalWait; // time to wait between pumping intervals to see the sensor recover
  int pumpIcon = 2; // purely asthetic pumping icon

void setup()
{  
  pinMode(RelayPin, OUTPUT);  // set pin as an output
  digitalWrite(RelayPin, HIGH);  // turn the relay off to start

  // init LCD to 2 lines of 16 char and clear
  lcd.begin(16, 2);
  lcd.clear();

  lcd.print("Garduino v1.00");

  Serial.begin(9600);

   // Create a new characters:
  lcd.createChar(0, Heart);
  lcd.createChar(1, EmptyHeart);
  lcd.createChar(2, PumpingA);
  lcd.createChar(3, PumpingB);
}

void loop()
{
  // Initialize variables
  float mVoltage; // Moisture voltage
  float tVoltage, degreesC, degreesCRound; // Temperature voltage & degrees
  float lVoltage; // Light sensor voltage

  // Read voltages (convert 1024 point analog to 0-5V range)
  mVoltage = getVoltage(MoisturePin);
  tVoltage = getVoltage(TempPin);
  lVoltage = getVoltage(LightPin);

  // Convert tVoltage to Temperature
  degreesC = (tVoltage - 0.5) * 100.0;
  degreesCRound = round(degreesC * 10) / 10.0; // round to 1 decimal place for temp

  // Print to serial   
  Serial.print("M;" + String(mVoltage) + ";T;" + String(tVoltage) + ";L;" + String(lVoltage) + ";TempC;" + String(degreesC));

  // Serial.print("M: ");  // these ones kept for debug
  // Serial.print(mVoltage);
  // Serial.print("v | T: ");
  // Serial.print(tVoltage);
  // Serial.print("v | L: ");
  // Serial.print(lVoltage);
  // Serial.print("v"); 
  // Serial.print('\n');
  // Serial.print("Temp (C): ");
  // Serial.print(degreesC);
  // Serial.print(" | Temp (C) Round: ");
  // Serial.print(degreesCRound);
  // Serial.print('\n');
  
  // Clear lower part of screen  
  lcd.setCursor(0,1);   // Set the cursor to the position
  lcd.print("               "); // Erase the largest possible number
  
  // set cursor location & print result
  lcd.setCursor(0,1);
  lcd.print("M");
  lcd.print(mVoltage,1);
  lcd.print(" T"); 
  lcd.print(degreesCRound,1);
  lcd.print("c L");
  lcd.print(lVoltage,1);

  //debug
  // Serial.println(timePumping);
  // Serial.println(waitPumping);

  // check moisture level and turn on pump. Voltage is higher when dryer (~3V for open air; ~1.5V for full water immersion).  So we will test if the mVoltage is dryer than the desired level
  if (mVoltage > Waterlevel)
  {
    // This says that we don't have the right moisture.  But if we just turn the pump on and wait for this sensor, then we will flood the system!  So we need to pump for a bit and see if the sensor catches up. We do this by pumping for some time (like 30 seconds) and then waiting for some time (like 5 mins).  We use some countdown timers to track these, and we reset them when the moisture level reaches the desired level.  I also didn't forget that we need to turn the pump off if moisture suddenly passes the desired level!
    
    // First we check if we are currently in the pumping phase
    if (timePumping >= 0) // Check if we pumped recently based on the wait flag
    {
      lcd.setCursor(15,0);
      lcd.write(byte(pumpIcon)); // print start pumping (water droplet icon)
      pumpIcon = 3 - pumpIcon / 3; // flip between 2 and 3
      digitalWrite(RelayPin, LOW);  // turn the relay on
      Serial.print(";Watering(1 = YES); 1\n");
      timePumping -= (CycleWaitDelay/1000); // reduce the pumping count time by 1 wait cycle
    } 
    // Then we check if we are in a wait cycle (timePumping is 0 or lower but waitPumping has time left)
    else if (waitPumping >= 0) // the level is low but we are in a wait cycle
    {
      lcd.setCursor(15,0);
      lcd.write(byte(1)); // print low water icon (but we are waiting)
      digitalWrite(RelayPin, HIGH);  // turn the pump relay off
      Serial.print(";Watering(1 = YES); 0\n");
      waitPumping -= (CycleWaitDelay/1000); // reduce the waiting count time by 1 wait cycle
    }
    // Otherwise waiting and pumping must have ended so reset the pump/wait variables
    else 
    {
      timePumping = PumpIntervalOn; // seconds interval pumping
      waitPumping = PumpIntervalWait; // time to wait between pumping intervals to see the sensor recover
    }
  } 
  else
  {
    // digitalWrite(RelayPin, HIGH);  // turn the relay off
    lcd.setCursor(15,0);
    lcd.write(byte(0)); // print full heart as we are ok
    Serial.print(";Watering(1 = YES); 0\n");
    digitalWrite(RelayPin, HIGH);  // turn the pump relay off

    // reset the counter variables and the pump
    timePumping = PumpIntervalOn; // seconds interval pumping
    waitPumping = PumpIntervalWait; // time to wait between pumping intervals to see the sensor recover
  }
  

  // delay 1000ms = 1sec 
  delay(CycleWaitDelay);
}
float getVoltage(int pin)
{
  // This equation converts the 0 to 1023 value that analogRead()
  // returns, into a 0.0 to 5.0 value that is the true voltage
  // being read at that pin.
  return (analogRead(pin) * 0.004882814); // 0.004882814 = (double)5 / (double)1024;
}