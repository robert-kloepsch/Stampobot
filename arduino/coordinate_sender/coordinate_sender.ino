
String rec;

void setup() { 
  Serial.begin(115200);
}

void loop() { 

  //Read serial input and extract the available data
  if (Serial.available() > 0) {
    rec = Serial.readStringUntil('\n');
    int commaIndex = rec.indexOf(',');
    int x_coord = rec.substring(0, commaIndex).toInt();
    int y_coord = rec.substring(commaIndex + 1).toInt();
    
    // After robot picking stamp, it sends the command to pc
    Serial.println("detect");    
  }   
  
}
