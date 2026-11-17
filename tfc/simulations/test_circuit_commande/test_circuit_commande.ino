const int pin1 = 2;
const int pin2 = 10;
int PWM = 255; // vitesse maximale

void setup() {
  Serial.begin(9600);
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
}

void loop() {
  if (PWM < 20){
    Serial.println("Vitesse maximale!!");
    PWM = 255;
  }

  analogWrite(pin1, PWM);
  analogWrite(pin2, 0);
  delay(5000);

  analogWrite(pin1, 0);
  analogWrite(pin2, PWM); // inversion de sens de rotation
  delay(5000);

  analogWrite(pin1, 0);
  analogWrite(pin2, 0);
  delay(5000);

  PWM = PWM - 65; // reduction de vitesse
  Serial.print("[Vitesse] : "); Serial.print(PWM); Serial.println("/255");
}
