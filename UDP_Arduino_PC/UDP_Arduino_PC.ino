#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_sleep.h"
#include "FS.h"
#include "SD_MMC.h"


// the IP of the machine to which you send msgs - this should be the correct IP in most cases (see note in python code)
#define CONSOLE_IP "192.168.1.2"
#define CONSOLE_PORT 4210
const char* ssid = "ESP32 Dev Board";  // ESP Wifi Host
const char* password = "12345@678";

#define GPIO_DEEP_SLEEP_DURATION 2     // sleep x seconds and then wake up
#define CHUNK_LENGTH 1048

// Wifi Connection
WiFiUDP Udp;
IPAddress local_ip(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
size_t bitToggleNow = 0;
size_t bitToggleStats = 0;
size_t count = 0;
boolean connected = false;

void readDataNow(){
  for (uint8_t i=0; i<10; i++){
      Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
      Udp.printf(" Weight: ");
      Udp.printf("%d", count);
      Udp.printf(" Size: ");
      Udp.printf("%d", count*2);
      Udp.endPacket();
      count++;
      delay(500);
    }
}

void readStatsNow(){
  for (uint8_t i=0; i<10; i++){
      Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
      Udp.printf(" Battery: ");
      Udp.printf("%d%", count);
      Udp.printf(" Humidity: ");
      Udp.printf("%d", count*2);
      Udp.endPacket();
      count++;
      delay(500);
    }
}


void sendPackets(File file , size_t buffLen, size_t chunk){
   char buffer[chunk];
    size_t blen = sizeof(buffer);
    size_t rest = buffLen % blen;
    uint8_t i = 0;
    for (i=0; i <  buffLen/blen; ++i) {
        file.seek(i*blen);
        int rec = file.readBytes(buffer, chunk);
        Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
        Udp.write((uint8_t *)buffer, chunk);
        Udp.endPacket();
        delay(100);
      }

      if (rest) {
        file.seek(i*blen);
        int rec = file.readBytes(buffer, rest);
        Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
        Udp.write((uint8_t *)buffer, rest);
        Udp.endPacket();
      }
}

void listDir(fs::FS &fs, const char * dirname, uint8_t levels){
    Serial.printf("Listing directory: %s\n", dirname);
    
    File root = fs.open(dirname);  
    if(!root){
        Serial.println("Failed to open directory");
        return;
    }
    if(!root.isDirectory()){
        Serial.println("Not a directory");
        return;
    }

    File file = root.openNextFile();
    while(file){
        if(file.isDirectory()){
            if(levels){
                listDir(fs, file.path(), levels -1);
            }
        } else {
              //  ------------------------------------
              size_t buffLen = file.available();
              String name =  String(file.name());
              String file_extension = name.substring(name.lastIndexOf(".")+1);
              
              Serial.println(name);
              // details about file before sending file bytes
              Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
              Udp.printf(" FILE: ");
              Udp.printf(file.name());
              Udp.printf(" SIZE: ");
              Udp.printf("%d", buffLen);
              Udp.printf(" Ext: ");
              Udp.printf("%s",file_extension);
              Udp.endPacket();
              // sending data 
              sendPackets(file, buffLen, CHUNK_LENGTH);
              // end tag
              delay(1000);
              Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
              Udp.print("<NEXT>");
              Udp.endPacket();

        }
        file = root.openNextFile();
    }
}

void setup()
{
  Serial.begin(115200);
  WiFi.disconnect(true);
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(local_ip, gateway, subnet);

  if(!SD_MMC.begin()){
      Serial.print("Card Mount Failed");
  }
  Serial.println("Start Program");
}
  

  void loop(){

         char rcv[CHUNK_LENGTH];
        // send only when client requests data
          int packet = Udp.parsePacket();
          int counter = 0;
          while(Udp.parsePacket()==0){
                Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
                Udp.printf("Hello");
                Udp.endPacket();
                Serial.println(".");
                counter++;
                if (counter > 1000000){
                  break;
                }
                delay(1000);
          }

          size_t pk = Udp.available();
          int err = Udp.read(rcv, pk);
          String name =  String(rcv);

          if(name.startsWith("Send")){
              Serial.println("Sending");
              listDir(SD_MMC, "/data", 0);
              delay(1000);
              Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
              Udp.printf("Done Sending");
              Udp.endPacket();
              Serial.print("Done Sending");
            }

          if(name.startsWith("Read")){
              Serial.println("Sending");
              readDataNow();
              delay(1000);
              Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
              Udp.printf("Done");
              Udp.endPacket();
              Serial.print("Done Sending");
            }
          
          if(name.startsWith("Stats")){
              Serial.println("Sending");
              readStatsNow();
              delay(1000);
              Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
              Udp.printf("Done");
              Udp.endPacket();
              Serial.print("Done Sending");
            }
          packet =0;
}




