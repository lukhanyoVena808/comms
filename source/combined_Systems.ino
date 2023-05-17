#include <Wire.h>
#include "DHT.h"
#include <Arduino.h>
#include "HX711.h"
#include "soc/rtc.h"
#include <WebServer.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_sleep.h"
#include <Adafruit_INA219.h>



#define DHTTYPE DHT11 // DHT 11

//DHT Sensor;
uint8_t DHTPin = 4;
DHT dht(DHTPin, DHTTYPE);
float Temperature;
float Humidity;
float Temp_Fahrenheit;

// Initialize the INA219 sensor object
Adafruit_INA219 ina219;

//readNow
// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 15;
const int LOADCELL_SCK_PIN = 2;
const byte numChars = 32;
char receivedChars[numChars];   // an array to store the received data
static byte ndx = 0;
boolean newData = false;
HX711 scale;

//--------------------------------
// the IP of the machine to which you send msgs - this should be the correct IP in most cases (see note in python code)
#define CONSOLE_IP "192.168.1.2"
#define CONSOLE_PORT 4210
const char* ssid = "ESP32 Dev Board 2";  // ESP Wifi Host
const char* password = "12345@678";
#define CHUNK_LENGTH 1048
// Wifi Connection
WiFiUDP Udp;
IPAddress local_ip(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
WiFiServer server(80);

void readStatsNow(){
  //read ten values
  for(int i=0; i<10; i++){
      Humidity = dht.readHumidity();
    // Read temperature as Celsius (the default)
    Temperature = dht.readTemperature();
    // Read temperature as Fahrenheit (isFahrenheit = true)
    Temp_Fahrenheit= dht.readTemperature(true);
    float batteryLevel = map(analogRead(33), 0.0f, 4095.0f, 0, 100);
    float batteryVoltage = (batteryLevel*4.2)/100;

      // Read the current and voltage values from the INA219 sensor
    float shuntVoltage = ina219.getShuntVoltage_mV();
    float busVoltage = ina219.getBusVoltage_V();
    float current_mA = ina219.getCurrent_mA();
    float power_mW =  busVoltage*current_mA;

    // Check if any reads failed and exit early (to try again).
    if (isnan(Humidity) || isnan(Temperature) || isnan(Temp_Fahrenheit)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      // return;
    }else{
        Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
        Udp.print(F("Humidity: "));
        Udp.print(Humidity);
        Udp.print(F("%  ,Temperature: "));
        Udp.print(Temperature);
        Udp.print(F("°C "));
        Udp.print(Temp_Fahrenheit);
        Udp.print(F("°F  ,"));
        Udp.print(F("Battery voltage: "));
        Udp.print(batteryVoltage);
        Udp.print(F("V  ,"));
        Udp.print(F("Battery level: "));
        Udp.print(batteryLevel);
        Udp.print(F("% "));

        ///----------
        Udp.print(" ,Shunt Voltage: ");
        Udp.print(shuntVoltage);
        Udp.print(" mV\t");
        Udp.print("Bus Voltage: ");
        Udp.print(busVoltage);
        Udp.print(" V");
        Udp.print(" ,Current: ");
        Udp.print(current_mA);
        Udp.print(" mA\t");
        Udp.print("Power: ");
        Udp.print(power_mW);
        Udp.println(" mW");
        //--------
        Udp.endPacket();
      }
      delay(1000);
  }
}

void readDataNow(){
    for (uint8_t i=0; i<10; i++){
        Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
        Udp.printf(" Weight: ");
        Udp.printf("%f",scale.get_units());
        Udp.endPacket();
        delay(1000);
    }
      
}

void setup() {
  Serial.begin(115200);
  WiFi.disconnect(true);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(local_ip, gateway, subnet);
  server.begin();
    // Initialize I2C communication
  Wire.begin();
  pinMode(DHTPin, INPUT);
  dht.begin();
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(761.0316456);
                   // this value is obtained by calibrating the scale with known weights; see the README for details
  scale.tare(); 

    // Initialize the INA219 sensor
  if (!ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) {
      delay(10);
    }
  }

   // Configure the INA219 settings
  ina219.setCalibration_16V_400mA();

}

void loop() {
        char incoming[CHUNK_LENGTH];
        // send only when client requests data
        int packet = Udp.parsePacket();
        int counter = 0;
        while(packet == 0){
              Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
              Udp.print("Hello");
              Udp.endPacket();
              Serial.println(".");
              Serial.println( WiFi.softAPIP() );  
              packet = Udp.parsePacket();
              counter++;
              if (counter > 10000){
                break;
              }
              delay(1000);
        }

        size_t rc = Udp.available();
        int rcv = Udp.read(incoming, rc);
        String line = String(incoming);
        
    if (line.startsWith("Stats")){
          Serial.println("Sending");
          readStatsNow();
          delay(1000);
          Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
          Udp.printf("Done");
          Udp.endPacket();
          Serial.print("Done Sending");
        }

  //If cient is requesting live data
  if(line.startsWith("Read")){
      Serial.println("Sending");
      readDataNow();
      delay(1000);
      Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
      Udp.printf("Done");
      Udp.endPacket();
      Serial.print("Done Sending");
    }
    packet=0;
    // showNewData();
    scale.power_down();             // put the ADC in sleep mode
    delay(1000);
    scale.power_up();
}