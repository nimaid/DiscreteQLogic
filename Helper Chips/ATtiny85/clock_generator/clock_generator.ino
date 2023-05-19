/*
  ATTiny85 1 Second Clock Genereator with adjust
           ______
      NC -|      |- VCC
     ADJ -|      |- NC
  EN_ADJ -|      |- Out'
     GND -|______|- Out

  By default the outputs have a clock signal of 1 Hz preprogrammed.
  If EN_ADJ is tied to ground, then the voltage on ADJ will modify the frequency of the signal:
    At 0v, 0.1s will be added to the period for a total of 1.1 Hz
    At 5v, 0.1s will be subtracted from the period for a total of 0.9 Hz
*/


// Pin definitions
const int OUT = 0;
const int OUTI = 1;
const int ADJ = A3;
const int NO_A = 4;

// Time definitions
const int period_base = 1000;  // ms
const int period_adjust = 100; // ms


// Toggle clock
bool clock_state = LOW;
void toggle_clock() {
  digitalWrite(OUTI, clock_state);
  clock_state = !clock_state;
  digitalWrite(OUT, clock_state);
}


// Get delay time
int delay_time(){
  if (digitalRead(NO_A)) {
    return (period_base/2);
  }
  else {
    return (period_base/2) + map(analogRead(ADJ), 0, 1023, (period_adjust/2), -(period_adjust/2));
  }
}


// Run a clock cycle
void run_clock(){
  delay(delay_time());
  toggle_clock();
}


void setup() {
  pinMode(OUT, OUTPUT);
  pinMode(OUTI, OUTPUT);
  pinMode(NO_A, INPUT_PULLUP);
  digitalWrite(OUT, clock_state);
  digitalWrite(OUTI, !clock_state);
}

void loop() {
  run_clock();
}
