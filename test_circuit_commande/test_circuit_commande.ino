const int pin1 = 3;
const int pin2 = 5;
int PWM = 255; // vitesse maximale
float d = 1; // rapport cyclique

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (PWM < 0){
    Serial.println("!!Vitesse maximale!!");
    PWM = 255;
    d = 1.0;
  }
  Serial.print("Rapport cyclique : ");
  Serial.println(d);
  Serial.print("Tension de commande moyenne : ");
  Serial.println(d*3.3);
  analogWrite(pin1, PWM); // Sens initial
  delay(5000);
  analogWrite(pin1, LOW);
  Serial.println("Inversion de sens de rotation...");
  analogWrite(pin2, PWM); // inversion de sens de rotation
  delay(5000);
  analogWrite(pin2, LOW);
  PWM = PWM - 45; // reduction de vitesse
  Serial.println("================================");
  d = (PWM-1.0)/255.0;
}
