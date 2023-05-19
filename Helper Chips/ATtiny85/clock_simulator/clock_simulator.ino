//**************************************************************//
//  Shift Register Test
//****************************************************************

// Pin connected to ST_CP of 74HC595
int latchPin = 1;

// Pin connected to SH_CP of 74HC595
int clockPin = 0;

// Pin connected to DS of 74HC595
int dataPin = 2;

// To shift 1 single byte
void shift_out_byte(byte data) {
  // Disable outputs
  digitalWrite(latchPin, LOW);
  // Shift out the data
  shiftOut(dataPin, clockPin, MSBFIRST, data);
  // Enable outputs
  digitalWrite(latchPin, HIGH);
}


void setup() {
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
}

void loop() {
  // count from 0 to 255 and display the number
  // on the LEDs
  for (int numberToDisplay = 0; numberToDisplay < 256; numberToDisplay++) {
    shift_out_byte(numberToDisplay);
    delay(500);
  }
}