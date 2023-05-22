/*
  ATTiny85 1 Second Clock Generator
           ______
      NC -|      |- VCC
    Out' -|      |- Out
     Out -|      |- Out'
     GND -|______|- Out

  By default the outputs have a clock signal of 1 Hz preprogrammed.
*/

// Pin definitions
const int OUT = 0;
const int OUTI = 1;
const int OUT2 = 2;
const int OUT2I = 3;
const int OUT3 = 4;

// Time definitions
const int period_base = 1000;  // ms


bool clock_state = LOW;
// Set clock
void set_clock() {
  digitalWrite(OUT, clock_state);
  digitalWrite(OUTI, !clock_state);
  digitalWrite(OUT2, clock_state);
  digitalWrite(OUT2I, !clock_state);
  digitalWrite(OUT3, clock_state);
}
// Toggle clock
void toggle_clock() {
  clock_state = !clock_state;
  set_clock();
}

// Run a clock cycle
void run_clock(){
  delay(period_base/2);
  toggle_clock();
}


void setup() {
  pinMode(OUT, OUTPUT);
  pinMode(OUTI, OUTPUT);
  pinMode(OUT2, OUTPUT);
  pinMode(OUT2I, OUTPUT);
  pinMode(OUT3, OUTPUT);
  set_clock();
}

void loop() {
  run_clock();
}
