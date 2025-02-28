#include <Arduino.h>

// Relay pins declaration
const int relay1 = 2; //IN1
const int relay2 = 3; //IN2
const int relay3 = 4; //IN3
const int relay4 = 5; //IN4
const int relay5 = 6; //IN5
const int relay6 = 7; //IN6
const int relay7 = 8; //IN7
const int relay8 = 9; //IN8
const int relay9 = 10; 
const int relay10 = 11;
const int relay11 = 12;
const int LED = 13; 

// Command enumeration
enum Command {
  CMD_PUSH_ACTUATOR,    // Push sequence
  CMD_EXTEND_BOTH,      // Extend both actuators
  CMD_STOP,             // Stop operation
  CMD_PUMP_SEQUENCE,    // Run pump sequence
  CMD_RETRACT_BOTH,     // Retract both actuators
  CMD_PUMP_ON,          // Turn pump on
  CMD_PUMP_OFF,         // Turn pump off
  CMD_FULL_SEQUENCE,    // Run full sequence
  CMD_LED_ON,           // Turn LED on
  CMD_AIR_CLOSE,        // Close air valve
  CMD_AIR_OPEN,         // Open air valve
  CMD_LOCKED_SEQUENCE,    // Run full sequence for LOCKED state
  CMD_UNLOCKED_SEQUENCE,  // Run full sequence for UNLOCKED state
  CMD_STATUS_UPDATE,      // Request a status update
  CMD_INVALID
};

// Command string mapping
const char* const COMMAND_STRINGS[] = {
  "PUSH",
  "EXTEND_BOTH",
  "STOP",
  "PUMP_SEQ",
  "RETRACT_BOTH",
  "PUMP_ON",
  "PUMP_OFF",
  "FULL_SEQ",
  "LED_ON",
  "AIR_CLOSE",
  "AIR_OPEN",
  "LOCKED_SEQUENCE",
  "UNLOCKED_SEQUENCE",
  "STATUS_UPDATE"
};

// Function to convert string to command enum
Command getCommandFromString(String cmdString) {
  cmdString.trim();  // Remove any whitespace
  
  for (int i = 0; i < CMD_INVALID; i++) {
    if (cmdString.equals(COMMAND_STRINGS[i])) {
      return static_cast<Command>(i);
    }
  }
  return CMD_INVALID;
}

void setup() {
  //Baudrate of serial commnunication 
  Serial.begin(9600);
  //Set up output pin 
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  pinMode(relay3, OUTPUT);
  pinMode(relay4, OUTPUT);
  pinMode(relay5, OUTPUT);
  pinMode(relay6, OUTPUT);
  pinMode(relay7, OUTPUT);
  pinMode(relay8, OUTPUT);
  pinMode(relay9, OUTPUT);
  pinMode(relay10, OUTPUT);
  pinMode(relay11, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(relay11, HIGH);
  // digitalWrite(relay12, HIGH);
  digitalWrite(LED,LOW);
}
// Extend actuator functions //
void extendActuator(){
  digitalWrite(relay1,HIGH);
  digitalWrite(relay2,LOW);
}

void extendActuator2(){
  digitalWrite(relay3,HIGH);
  digitalWrite(relay4,LOW);
}

void extendActuator3(){
  digitalWrite(relay5,HIGH);
  digitalWrite(relay6,LOW);
}

void extendActuator4(){
  digitalWrite(relay7,HIGH);
  digitalWrite(relay8,LOW);
}
// Retract acutator functions //
void retractActuator(){
  digitalWrite(relay1,LOW);
  digitalWrite(relay2,HIGH);
}

void retractActuator2(){
  digitalWrite(relay3,LOW);
  digitalWrite(relay4,HIGH);
}

void retractActuator3(){
  digitalWrite(relay5,LOW);
  digitalWrite(relay6,HIGH);
}

void retractActuator4(){
  digitalWrite(relay7,LOW);
  digitalWrite(relay8,HIGH);
}

// Stop actuator functions //
void stopActuator(){ 
  digitalWrite(relay1,LOW);
  digitalWrite(relay2,LOW);
}

void stopActuator2(){ 
  digitalWrite(relay3,LOW);
  digitalWrite(relay4,LOW);
}

void stopActuator3(){ 
  digitalWrite(relay5,LOW);
  digitalWrite(relay6,LOW);
}

void stopActuator4(){ 
  digitalWrite(relay7,LOW);
  digitalWrite(relay8,LOW);
}
void pumpON(){
  digitalWrite(relay9, HIGH);
  digitalWrite(relay10, LOW);
}

void pumpOFF(){
  digitalWrite(relay9, LOW);
  digitalWrite(relay10, LOW);
}

void closeAir(){
  digitalWrite(relay11, HIGH);
}

void openAir(){
  digitalWrite(relay11, LOW);
}

void midCloseAir(){
  digitalWrite(relay12, HIGH);
}

void midOpenAir(){
  digitalWrite(relay12, LOW);
}

void runLockedSequence() {
  // Step 1: Press Reset button to enable Unlocked mode
  extendActuator();
  delay(1150);
  retractActuator();
  delay(1150);
  Serial.println("PRESSED_RESET");
  delay(3000);
  
  // Step 2: Retract actuator 2 and then press Reset
  retractActuator2();
  delay(1150);
  extendActuator(); // Press Reset
  delay(1150);
  retractActuator();
  delay(1150);
  Serial.println("ACCESS_CALIBRATION_MODE");
  delay(3000); // Wait a bit to display the text 
  retractActuator3(); 
  delay(1150);
  
  // Step 3: Press P button
  extendActuator3();
  delay(1150);
  retractActuator3();
  delay(1150);
  Serial.println("PRESSED_P");
  delay(3000);
  
  //Step 4: Open air
  openAir();
  Serial.println("OPEN_AIR");
  delay(5000); //Wait a bit for pressure to reach 500kPa

  //Step 5: Close Air
  closeAir();
  delay(1000);
  Serial.println("CLOSE_AIR");
  
  //Step 6: Open Mid Air
  midOpenAir();
  Serial.println("MID_AIR_OPEN");
  delay(1000);

  //Step 7: Close Mid Air
  midCloseAir();
  Serial.println("MID_AIR_CLOSE");
  delay(1000);
  // Final step
  Serial.println("SEQUENCE_COMPLETE");
}

// Implement unlocked sequence function
void runUnlockedSequence() {
  // Step 2: Retract actuator 2 and then press Reset
  retractActuator2();
  delay(1150);
  extendActuator(); // Press Reset
  delay(1150);
  retractActuator();
  delay(1150);
  Serial.println("ACCESS_CALIBRATION_MODE");
  delay(3000); // Wait a bit to display the text 
  retractActuator3(); 
  delay(1150);
  
  // Step 3: Press P button
  extendActuator3();
  delay(1150);
  retractActuator3();
  delay(1150);
  Serial.println("PRESSED_P");
  delay(3000);
  
  //Step 4: Open air
  openAir();
  Serial.println("OPEN_AIR");
  delay(5000); //Wait a bit for pressure to reach 500kPa

  //Step 5: Close Air
  closeAir();
  delay(1000);
  Serial.println("CLOSE_AIR");
  
  //Step 6: Open Mid Air
  midOpenAir();
  Serial.println("MID_AIR_OPEN");
  delay(1000);

  //Step 7: Close Mid Air
  midCloseAir();
  Serial.println("MID_AIR_CLOSE");
  delay(1000);
  // Final step  
  Serial.println("SEQUENCE_COMPLETE");
}

void loop() {
  if (Serial.available()) {
    String commandString = Serial.readStringUntil('\n');
    Command command = getCommandFromString(commandString);

    switch (command) {
      case CMD_PUSH_ACTUATOR: //Previously 'E'
        extendActuator4();
        delay(1100);
        stopActuator();
        retractActuator4();
        delay(1100);
        stopActuator();
        break;

      case CMD_EXTEND_BOTH: //Previously 'R'
        extendActuator2();
        extendActuator3();
        delay(1150);
        stopActuator2();
        stopActuator3();
        break;

      case CMD_STOP: //Previously 'S'
        stopActuator();
        break;

      case CMD_PUMP_SEQUENCE: // Previously 'A'
        extendActuator2();
        extendActuator3();
        delay(1150);
        stopActuator2();
        stopActuator3();
        extendActuator(); //Pressing Reset button 
        delay(1150);
        retractActuator();
        delay(1150);
        for (int i = 0; i < 40; i++) {
          Serial.println("L");
          delay(100);
        }
        break;

      case CMD_RETRACT_BOTH: // Previously 'K'
        retractActuator2();
        retractActuator3();
        break;

      case CMD_PUMP_ON: // Previously 'B'
        pumpON();
        break;

      case CMD_PUMP_OFF: // Previously 'C'
        pumpOFF();
        break;

      case CMD_FULL_SEQUENCE: // Previously 'D'
        extendActuator2();
        extendActuator4();
        delay(1150);
        stopActuator2();
        stopActuator4();
        delay(4000);
        retractActuator4();
        delay(5000);
        retractActuator2();
        delay(2000);
        extendActuator();
        delay(1100);
        stopActuator();
        delay(2000);
        retractActuator();
        delay(2000);
        break;

      case CMD_LED_ON: // Previously 'G'
        digitalWrite(LED, HIGH);
        break;

      case CMD_AIR_CLOSE: // Previously 'H'
        closeAir();
        break;

      case CMD_AIR_OPEN: // Previously 'I'
        openAir();
        break;

      case CMD_INVALID:
        // Handle invalid command
        Serial.println("Invalid command received");
        break;

      case CMD_LOCKED_SEQUENCE:
        runLockedSequence();
        break;
        
      case CMD_UNLOCKED_SEQUENCE:
        runUnlockedSequence();
        break;
    }
  }
}