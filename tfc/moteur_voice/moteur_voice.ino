// auteur : BOSOLINDO EDHIENGENE Roger
// email : rogerbosolinndo34@gmail.com
// Code optimisé par IA
// Classification à 6 classes (Arduino Nano 33 BLE Sense)

#include <PDM.h>
#include <arm_math.h>
#include <MicroTFLite.h>
#include "model.h"
#include "mel_filterbank.h"

// paramètres audio
#define SAMPLE_RATE 16000  // fréquence d'échantillonnage
#define CLIP_SAMPLES 16000 // le nombre d'échantillons par enregistrement
#define WIN_LENGTH 480    // nombre d'échantillons par fenêtre (de 30ms)
#define HOP_LENGTH 320    // on avance de 20ms à chaque fois, soit 320 échantillons
#define N_FFT 512         //
#define NUM_FRAMES 49     // nombre de trames
#define N_MELS MEL_NUM_FILTERS  // nombre de caractéristique mels par trame

// buffer du micro (rempli petit a petit par l'interruption PDM)
short pdmBuffer[512];

// DOUBLE BUFFER : pendant qu'on analyse un buffer, le micro remplit l'autre
int16_t bufferA[CLIP_SAMPLES];
int16_t bufferB[CLIP_SAMPLES];

int writeIndex = 0;
bool remplitA = true;   // true on remplit A, false on remplit B
bool bufferAPret = false;
bool bufferBPret = false;

// buffers de calcul
float32_t hammingWindow[WIN_LENGTH];
float32_t fftInput[N_FFT];
float32_t fftOutput[N_FFT];
float32_t powerSpectrum[N_FFT / 2 + 1];
float32_t features[NUM_FRAMES][N_MELS];

arm_rfft_fast_instance_f32 fftInstance;

// modele
#define TENSOR_ARENA_SIZE (50 * 1024)
alignas(16) byte tensorArena[TENSOR_ARENA_SIZE];

// mots clés
const char* labels[] = {
                            "down",
                            "go",
                            "inconnu",
                            "left",
                            "stop",
                            "up"
                        };
#define NUM_CLASSES 6
#define IDX_DOWN 0
#define IDX_GO 1
#define IDX_INCONNU 2
#define IDX_LEFT 3
#define IDX_STOP 4
#define IDX_UP 5

float scoreMin = 0.90;
unsigned long cooldownMs = 2000; // on attend 2s avant de reprendre le même mot

int dernierMot = -1;
unsigned long dernierTemps = 0;

// moteur
int pinMoteurA = 2;
int pinMoteurB = 10;

int incrementVitesse = 40;
int vitesseMax = 200;

int MOTEUR_ARRET = 0;
int MOTEUR_AVANT = 1;
int MOTEUR_ARRIERE = 2;

int directionActuelle = MOTEUR_ARRET;
int vitesseActuelle = 0;

int ancienneDirection = MOTEUR_ARRET;
int ancienneVitesse = 0;

void commanderMoteur() {
  if (directionActuelle == MOTEUR_AVANT) {
    analogWrite(pinMoteurA, vitesseActuelle);
    analogWrite(pinMoteurB, 0);
  }
  else if (directionActuelle == MOTEUR_ARRIERE) {
    analogWrite(pinMoteurA, 0);
    analogWrite(pinMoteurB, vitesseActuelle);
  }
  else {
    analogWrite(pinMoteurA, 0);
    analogWrite(pinMoteurB, 0); // on coupe tout
  }

  Serial.print("Direction=");
  if (directionActuelle == MOTEUR_AVANT) Serial.print("AVANT");
  else if (directionActuelle == MOTEUR_ARRIERE) Serial.print("ARRIERE");
  else Serial.print("STOP");
  Serial.print(" Vitesse=");
  Serial.println(vitesseActuelle);
}

// fonction appelée automatiquement dès que le micro a de nouvelles données
void onPDMdata() {
  int bytesAvailable = PDM.available();
  PDM.read(pdmBuffer, bytesAvailable);
  int nbEchantillons = bytesAvailable / 2;

  for (int i = 0; i < nbEchantillons; i++) {

    // on ecrit dans le buffer qui est actif en ce moment
    if (remplitA) {
      bufferA[writeIndex] = pdmBuffer[i];
    } else {
      bufferB[writeIndex] = pdmBuffer[i];
    }

    writeIndex += 1;

    // le buffer est plein (1 seconde de son)
    if (writeIndex >= CLIP_SAMPLES) {

      if (remplitA) {
        // on veut basculer sur B, mais si B contient encore des données
        // pas encore lues par loop(), on ne doit PAS ecrire dessus
        if (bufferBPret) {
          writeIndex = 0; // on perd ce morceau de son
        } else {
          bufferAPret = true;
          remplitA = false;
          writeIndex = 0;
        }
      } else {
        if (bufferAPret) {
          writeIndex = 0;
        } else {
          bufferBPret = true;
          remplitA = true;
          writeIndex = 0;
        }
      }
    }
  }
}

// calcule la fenêtre de hamming (pour lisser les bords du son)
void calculerHamming() {
  for (int n = 0; n < WIN_LENGTH; n++) {
    hammingWindow[n] = 0.54 - 0.46 * cos(2.0 * PI * n / WIN_LENGTH);
  }
}

// transforme un petit bout de son en "features" comprehensibles par le modèle
void calculerFeatures(int16_t* debutFrame, float32_t* sortieMel) {

  // 1) on applique la fenêtre de hamming
  for (int n = 0; n < WIN_LENGTH; n++) {
    fftInput[n] = (debutFrame[n] / 32768.0) * hammingWindow[n];
  }
  for (int n = WIN_LENGTH; n < N_FFT; n++) {
    fftInput[n] = 0.0;
  }

  // 2) FFT (on passe dans le domaine des fréquences)
  arm_rfft_fast_f32(&fftInstance, fftInput, fftOutput, 0);

  // 3) puissance de chaque fréquence
  powerSpectrum[0] = fftOutput[0] * fftOutput[0];
  powerSpectrum[N_FFT / 2] = fftOutput[1] * fftOutput[1];
  for (int k = 1; k < N_FFT / 2; k++) {
    float32_t re = fftOutput[2 * k];
    float32_t im = fftOutput[2 * k + 1];
    powerSpectrum[k] = re * re + im * im;
  }

  // 4) filtres mel
  float32_t melEnergy[N_MELS];
  for (int m = 0; m < N_MELS; m++) {
    MelFilter f = mel_filterbank[m];
    float32_t somme = 0.0;
    for (int b = 0; b < f.num_bins; b++) {
      somme += powerSpectrum[f.start_bin + b] * f.weights[b];
    }
    melEnergy[m] = somme;
  }

  // 5) log (pour compresser les sons très forts)
  float32_t logMel[N_MELS];
  for (int m = 0; m < N_MELS; m++) {
    logMel[m] = log(melEnergy[m] + 0.000001);
  }

  // 6) normalisation (moyenne / ecart type)
  float32_t moyenne = 0.0;
  for (int m = 0; m < N_MELS; m++) moyenne += logMel[m];
  moyenne = moyenne / N_MELS;

  float32_t variance = 0.0;
  for (int m = 0; m < N_MELS; m++) {
    float32_t d = logMel[m] - moyenne;
    variance += d * d;
  }
  variance = variance / N_MELS;
  float32_t ecartType = sqrt(variance) + 0.00000001;

  for (int m = 0; m < N_MELS; m++) {
    sortieMel[m] = (logMel[m] - moyenne) / ecartType;
  }
}

// calcule les features pour tout le clip audio (49 frames)
void extraireFeatures(int16_t* clip) {
  for (int frame = 0; frame < NUM_FRAMES; frame++) {
    int start = frame * HOP_LENGTH;
    calculerFeatures(&clip[start], features[frame]);
  }
}

void lancerInference() {
  int idx = 0;
  for (int frame = 0; frame < NUM_FRAMES; frame++) {
    for (int m = 0; m < N_MELS; m++) {
      ModelSetInput(features[frame][m], idx);
      idx += 1;
    }
  }

  if (!ModelRunInference()) {
    Serial.println("Oups, échec inference !");
    return;
  }

  // on cherche le mot avec le plus gros score
  int meilleurIdx = 0;
  float meilleurScore = ModelGetOutput(0);
  for (int i = 1; i < NUM_CLASSES; i++) {
    float score = ModelGetOutput(i);
    if (score > meilleurScore) {
      meilleurScore = score;
      meilleurIdx = i;
    }
  }

  // si le score est trop faible on ignore
  if (meilleurScore < scoreMin) {
    return;
  }

  // si on repete le même mot trop vite on ignore aussi
  unsigned long maintenant = millis();
  bool memeMot = (meilleurIdx == dernierMot);
  bool coolDownFini = (maintenant - dernierTemps) >= cooldownMs;

  if (memeMot && !coolDownFini) {
    Serial.print("Deja compris : ");
    Serial.println(labels[meilleurIdx]);
    return;
  }

  dernierMot = meilleurIdx;
  dernierTemps = maintenant;

  Serial.print("[Commande validée] : ");
  Serial.print(labels[meilleurIdx]);
  Serial.print(" score=");
  Serial.println(meilleurScore, 3);

  executerCommande(meilleurIdx);
}

void executerCommande(int idx) {
  if (idx == IDX_UP) {
    // avance
    digitalWrite(LEDB, LOW);
    digitalWrite(LEDR, HIGH);
    digitalWrite(LEDG, HIGH);

    vitesseActuelle += incrementVitesse;
    if (vitesseActuelle > vitesseMax) vitesseActuelle = vitesseMax;
    commanderMoteur();
  }

  else if (idx == IDX_DOWN) {
    // recule
    digitalWrite(LEDB, HIGH);
    digitalWrite(LEDR, LOW);
    digitalWrite(LEDG, HIGH);

    vitesseActuelle -= incrementVitesse;
    if (vitesseActuelle < 50) vitesseActuelle = 50;
    commanderMoteur();
  }

  else if (idx == IDX_LEFT) {
    // change de sens (garde la vitesse)
    digitalWrite(LEDB, HIGH);
    digitalWrite(LEDR, HIGH);
    digitalWrite(LEDG, LOW);

    if (directionActuelle == MOTEUR_AVANT) {
      directionActuelle = MOTEUR_ARRIERE;
      commanderMoteur();
    } else if (directionActuelle == MOTEUR_ARRIERE) {
      directionActuelle = MOTEUR_AVANT;
      commanderMoteur();
    } else {
      Serial.println("A l'arret !!!");
    }
  }

  else if (idx == IDX_GO) {
    if (directionActuelle == MOTEUR_ARRET) {
      digitalWrite(LED_BUILTIN, HIGH);

      if (ancienneDirection != MOTEUR_ARRET) {
        directionActuelle = ancienneDirection;
        vitesseActuelle = ancienneVitesse;
        commanderMoteur();
      } else {
        Serial.println("Ignoré !!!");
      }
    } else {
      Serial.println("Déjà sur Go !");
    }
  }

  else if (idx == IDX_STOP) {
    // arrêt d'urgence
    digitalWrite(LED_BUILTIN, LOW);

    if (directionActuelle != MOTEUR_ARRET) {
      ancienneDirection = directionActuelle;
      ancienneVitesse = vitesseActuelle;
    }
    directionActuelle = MOTEUR_ARRET;
    vitesseActuelle = 0;
    commanderMoteur();
  }
  delay(1000);
  digitalWrite(LEDB, HIGH);
  digitalWrite(LEDR, HIGH);
  digitalWrite(LEDG, HIGH);
}

void setup() {
  Serial.begin(9600);
  while (!Serial);

  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(pinMoteurA, OUTPUT);
  pinMode(pinMoteurB, OUTPUT);
  commanderMoteur(); // tout eteint au demarrage

  calculerHamming();
  arm_rfft_fast_init_f32(&fftInstance, N_FFT);

  Serial.println("Initialisation...");
  if (!ModelInit(model, tensorArena, TENSOR_ARENA_SIZE)) {
    Serial.println("Erreur : le modèle n'a pas demarré !");
    while (true); // on bloque tout
  }
  Serial.println("Prêt !");

  ModelPrintTensorInfo();
  ModelPrintInputTensorDimensions();
  ModelPrintOutputTensorDimensions();
  ModelPrintTensorQuantizationParams();

  // à partir d'ici le micro tourne en continu, on ne l'arrête plus jamais
  PDM.onReceive(onPDMdata);
  if (!PDM.begin(1, SAMPLE_RATE)) {
    Serial.println("Erreur : le micro ne repond pas !");
    while (true);
  }
}

void loop() {
  if (bufferAPret) {
    extraireFeatures(bufferA);
    lancerInference();
    bufferAPret = false;
  }

  if (bufferBPret) {
    extraireFeatures(bufferB);
    lancerInference();
    bufferBPret = false;
  }
}
