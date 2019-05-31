/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>
#include <string.h>

Servo myservo_y;
Servo myservo_x;

bool moving = false;

String temp;

int x_curr = 90;
int y_curr = 60;

int x_goto = 90;
int y_goto = 60;

int rate = 15;

void setup() {
  Serial.begin(9600);
  myservo_x.attach(10);
  myservo_y.attach(9);
  myservo_x.write(x_curr);
  myservo_y.write(y_curr);
}

void loop() {
  if (Serial.available() > 0) {
    x_goto = Serial.parseInt();
    y_goto = Serial.parseInt();
    rate = Serial.parseInt();

    if (x_curr != x_goto || y_curr != y_goto) {
      moving = true;
    }

    while (moving) {
      if (x_curr < x_goto) {
        x_curr += 1;
        myservo_x.write(x_curr);
        delay(rate);
      }
      else if (x_curr > x_goto) {
        x_curr -= 1;
        myservo_x.write(x_curr);
        delay(rate);
      }
      if (y_curr < y_goto) {
        y_curr += 1;
        myservo_y.write(y_curr);
        delay(rate);
      }
      else if (y_curr > y_goto) {
        y_curr -= 1;
        myservo_y.write(y_curr);
        delay(rate);
      }
      if (x_curr == x_goto && y_curr == y_goto) {
        moving = false;
      }
    }
  }
}
    
    
//    if (x_curr > x_prev) {
//      for (x_prev; x_prev <= x_curr; x_prev += 1) {
//         myservo_x.write(x_prev);
//         delay(15);
//      }
//    }
//    else {
//      for (x_prev; x_prev >= x_curr; x_prev -= 1) {
//         myservo_x.write(x_prev);
//         delay(15);
//      }
//    }
//    if (y_curr > y_prev) {
//      for (y_prev; y_prev <= y_curr; y_prev += 1) {
//         myservo_y.write(y_prev);
//         delay(15);
//      }
//    }
//    else {
//      for (y_prev; y_prev >= y_curr; y_prev -= 1) {
//         myservo_y.write(y_prev);
//         delay(15);
//      }
//    }


  
//  for (pos = 0; pos <= 180; pos += 1) { // goes from 180 degrees to 0 degrees
//    myservo_x.write(pos);
//    delay(15);                       // waits 15ms for the servo to reach the position
//  }
//  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
//    myservo_x.write(pos);
//    delay(15);                       // waits 15ms for the servo to reach the position
//  }
