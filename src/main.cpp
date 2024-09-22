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
// const int relay12 = 13; 

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
  digitalWrite(relay11, HIGH);
  // digitalWrite(relay12, HIGH);
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

// void midCloseAir(){
//   digitalWrite(relay12, HIGH);
// }

// void midOpenAir(){
//   digitalWrite(relay12, LOW);
// }
//
void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    switch (command) {
      case 'E':  //For pushing actuator 1
        extendActuator4();
        delay(1100);
        stopActuator();
        retractActuator4();
        delay(1100);
        stopActuator();
        break;

      case 'R':
        extendActuator2();
        extendActuator3();
        delay(1150);
        stopActuator2();
        stopActuator3();
        break;

      case 'S':
        stopActuator();
        break;

      case 'A': //For pushing actuator 2
        extendActuator2();
        extendActuator3();
        delay(1150);
        stopActuator2();
        stopActuator3();
        pumpON();
        for (int i = 0; i < 40; i++)
        {
          Serial.println("L");
          delay(100);
        }
        break;

      case 'K':
        retractActuator2();
        retractActuator3();
        break;

      case 'B':
        pumpON();
        break;

      case 'C':
        pumpOFF();
        break;

      case 'D':
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

      case 'J': // as 'E' has been used
        // midCloseAir();
        break;

      case 'F':
        // midOpenAir();
        break;

      case 'G':
        extendActuator4();
        break;

      case 'H':
        closeAir();
        break;

      case 'I':
        openAir();
        break;

      default:
        // Optional: handle unexpected commands
        break;
    }
  }

}


