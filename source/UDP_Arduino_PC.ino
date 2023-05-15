#include <WebServer.h>
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
WiFiServer server(80);
boolean connected = false;


// void sendPackets(){
//    char buffer[CHUNK_LENGTH];
//     size_t blen = sizeof(buffer);
//     size_t rest = buffLen % blen;
//     uint8_t i = 0;
//     for (i=0; i <  buffLen/blen; ++i) {
//         file.seek(i*blen);
//         int rec = file.readBytes(buffer, CHUNK_LENGTH);
//         Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
//         Udp.write((uint8_t *)buffer, CHUNK_LENGTH);
//         Udp.endPacket();
//         delay(100);
//       }

//       if (rest) {
//         file.seek(i*blen);
//         int rec = file.readBytes(buffer, rest);
//         Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
//         Udp.write((uint8_t *)buffer, rest);
//         Udp.endPacket();
//       }
// }

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
              //  ------------------ start of else-statement ------------------
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
                if (file_extension == "txt"){
                    char buffer[buffLen];
                    int rec = file.readBytes(buffer, sizeof(buffer));
                    Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
                    Udp.write((uint8_t *)buffer, buffLen);
                    Udp.endPacket();
                  }
                  
                if (file_extension == "jpg"){
                    char buffer[CHUNK_LENGTH];
                    size_t blen = sizeof(buffer);
                    size_t rest = buffLen % blen;
                    uint8_t i = 0;
                    for (i=0; i <  buffLen/blen; ++i) {
                        file.seek(i*blen);
                        int rec = file.readBytes(buffer, CHUNK_LENGTH);
                        Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
                        Udp.write((uint8_t *)buffer, CHUNK_LENGTH);
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
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(local_ip, gateway, subnet);

  server.begin();

  if(!SD_MMC.begin()){
      Serial.print("Card Mount Failed");
  }
  
  // send only when client requests data
  // int packet = Udp.parsePacket();
  // while (packet == 0) {
  //       Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
  //       Udp.print("Hello");
  //       Udp.endPacket();
  //       Serial.println(".");
  //       packet = Udp.parsePacket();
  //       delay(1000);
  // }
  // Serial.println("Handshake Done");
  // listDir(SD_MMC, "/data", 0);
  // delay(1000);
  // Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
  // Udp.print("Done Sending");
  // Udp.endPacket();
  // Serial.print("Done Sending");
}

  void loop(){

        char incoming[CHUNK_LENGTH];
        // send only when client requests data
        int packet = Udp.parsePacket();
        int counter = 0;
        while(packet){
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

        int rc = Udp.read(incoming, Udp.available());
        String myString = String(incoming);
        Serial.println(myString);
        // if(counter < 10000 && counter>1){
        //     Serial.println("Handshake Done");
        //     listDir(SD_MMC, "/data", 0);
        //     delay(1000);
        //     Udp.beginPacket(CONSOLE_IP, CONSOLE_PORT);
        //     Udp.print("Done Sending");
        //     Udp.endPacket();
        //     Serial.print("Done Sending");
        //   }
        packet =0;
}




