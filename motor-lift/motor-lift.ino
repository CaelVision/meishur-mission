#include <DShot.h>
#include <HX711.h>

enum Direction {
  RAMP_UP,
  RAMP_DOWN,
  AT_TARGET,
} direction;

DShot esc(DShot::Mode::DSHOT150);

uint8_t dataPin = 6;
uint8_t clockPin = 7;
HX711 loadcell;

void emptySerialBuffer() {
  while(Serial.available()) {
    Serial.read();
  }
}

void setup() {

  Serial.begin(115200);

  loadcell.begin(dataPin, clockPin);
  loadcell.set_scale(402.16);

  esc.attach(5);
  esc.setThrottle(0);

  while(!Serial);
  Serial.println("ready to start!");

  // START testing when the user sends anything
  while(!Serial.available());
  emptySerialBuffer();

  direction = RAMP_UP;
  loadcell.tare();
}

int throttle = 0;
const int step = 5;
const int max = 300;
const int min = 48;

bool reachedTarget = false;
int targetThrottleCtr = 0;
const int targetThrottleDur = 80;

bool terminate = false;

const int readLiftEvery = 5;
int readLiftCtr = 0;
float lift = 0;

void loop() {

  // STOP MOTOR if the user sends anything
  if (Serial.available()) {
    Serial.println("TERMINATING");
    emptySerialBuffer();
    terminate = true;
    esc.setThrottle(0);
  }
  if (terminate) {
    esc.setThrottle(0);
    return;
  }

  if (direction == RAMP_UP) {
    throttle += step;
  } else if (direction == RAMP_DOWN) {
    throttle -= step;
  }

  if (reachedTarget) {
    targetThrottleCtr++;

    if (targetThrottleCtr > targetThrottleDur) {
      targetThrottleCtr = 0;
      reachedTarget = false;
      direction = RAMP_DOWN;
    }
  }

  if (throttle > max) {
    throttle = max;
    reachedTarget = true;
    direction = AT_TARGET;

  } else if (throttle < min) {
    throttle = min;
    direction = RAMP_UP;
  }

  // Serial.print("throttle is ");
  // Serial.print(throttle);
  // Serial.print(" ");

  if (++readLiftCtr > readLiftEvery) {
    lift = loadcell.get_units(1);
    readLiftCtr = 0;
    Serial.print(throttle);
    Serial.print(" ");
    Serial.print(lift);
    Serial.println();
  }
  // Serial.print("loadcell reads ");
  // Serial.print(lift);

  // Serial.println();

  esc.setThrottle(throttle);

  delay(50);
}
