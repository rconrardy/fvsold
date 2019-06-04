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
