#include "PMS.h"
#include <HardwareSerial.h>
#include <AWS_IOT.h>
#include <WiFi.h>

HardwareSerial pmsSerial(0);
PMS pms(pmsSerial);
PMS::DATA data;

AWS_IOT hornbill;   // AWS_IOT instance
char WIFI_SSID[] = "YOUR_WIFI_SSID";
char WIFI_PASSWORD[] = "YOUR_WIFI_PASSWORD";
char HOST_ADDRESS[] = "YOUR_AWS_IoT_HOST_ADDRESS";
char CLIENT_ID[] = "RAMA3";
char TOPIC_LOCATION[] = "DustSensor/RAMA3";

int status = WL_IDLE_STATUS;
char payload[512];
uint16_t pm_1_0, pm_2_5, pm_10_0;

void connectWIFI() {
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(WIFI_SSID);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    // wait 5 seconds for connection:
    delay(5000);
  }
  Serial.println("Connected to wifi");
}

void connectAWS() {
  if(hornbill.connect(HOST_ADDRESS, CLIENT_ID) == 0) { // Connect to AWS using Host Address and Cliend ID
    Serial.println("Connected to AWS");
    delay(1000);
  } else {
    Serial.println("AWS connection failed, Check the HOST Address");
    while(1);
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  connectWIFI();

  connectAWS();

  delay(2000);  
  pmsSerial.begin(9600);
  Serial.println("Begin reading dust sensor");
}

void loop() {
  if (pms.read(data)) {
    pm_1_0 = data.PM_AE_UG_1_0;
    Serial.print("PM 1.0 (ug/m3): ");
    Serial.println(pm_1_0);

    pm_2_5 = data.PM_AE_UG_2_5;
    Serial.print("PM 2.5 (ug/m3): ");
    Serial.println(pm_2_5);

    pm_10_0 = data.PM_AE_UG_10_0;
    Serial.print("PM 10.0 (ug/m3): ");
    Serial.println(pm_10_0);

    if (isnan(pm_1_0) || isnan(pm_2_5) || isnan(pm_10_0)) {
      Serial.println("Some value is missing from dust sensor!");
    } else {
      char DustSenSorID[] = "DustSensor003";
      sprintf(payload, "{\"DustSensorID\": \"%s\", \"PM1.0\": \"%d\", \"PM2.5\": \"%d\", \"PM10.0\": \"%d\"}", DustSenSorID, pm_1_0, pm_2_5, pm_10_0);
          
      if(hornbill.publish(TOPIC_LOCATION, payload) == 0) {        
        Serial.print("Publish Message:");   
        Serial.println(payload);
      }
      else {
        Serial.println("Publish failed");
      }
      Serial.println();  
    }
  } else {
    Serial.println("Failed to read from dust sensor!");
  }
 
  // publish the temp and humidity every 10 seconds.
  vTaskDelay(10000 / portTICK_RATE_MS);
}
