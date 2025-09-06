# Hardware Guide

## Smart Insole Device

### Compatible Devices
- ESP32-based Bluetooth/WiFi modules
- Arduino with Bluetooth module (HC-05/HC-06)
- Serial connection devices

### Sensor Configuration
- 8 capacitive pressure sensors
- Positioned at key foot pressure points
- 16-bit ADC resolution recommended

### Communication Protocol

#### Serial Communication
- **Baud Rate**: 115200 (default)
- **Data Format**: JSON
- **Update Rate**: 50Hz (configurable)

#### Example Data Format
```json
{
  "sensors": [12.5, 14.2, 11.8, 13.1, 12.9, 15.3, 16.0, 14.8],
  "timestamp": 1234567890
}
```

#### Bluetooth LE Service
- **Service UUID**: 12345678-1234-1234-1234-123456789abc
- **Characteristic UUID**: 87654321-4321-4321-4321-cba987654321
- **Device Name**: "Smart Insole BLE"

### Sensor Placement

```
    [0]     [1]     <- Toe sensors
  [2] [3] [4] [5]    <- Metatarsal sensors
      [6]            <- Midfoot sensor
      [7]            <- Heel sensor
```

### Calibration Process
1. Stand on device for 5 seconds
2. Lift foot for baseline measurement
3. Apply known weight for scaling
4. Save calibration to device memory

### Power Management
- Battery life: 8-12 hours typical use
- Charging: USB-C connector
- Low battery warning at 15%
- Auto-sleep after 5 minutes inactivity

## Arduino Firmware

### Setup Requirements
```cpp
#include <WiFi.h>
#include <BluetoothSerial.h>
#include <ArduinoJson.h>

// Sensor pins
const int sensorPins[8] = {A0, A1, A2, A3, A4, A5, A6, A7};
```

### Basic Loop
```cpp
void loop() {
  JsonDocument doc;
  JsonArray sensors = doc["sensors"].to<JsonArray>();
  
  for(int i = 0; i < 8; i++) {
    float value = analogRead(sensorPins[i]) * 0.0322; // Convert to pressure
    sensors.add(value);
  }
  
  doc["timestamp"] = millis();
  
  String output;
  serializeJson(doc, output);
  Serial.println(output);
  
  delay(20); // 50Hz update rate
}
```

## Troubleshooting

### Connection Issues
1. Check device pairing status
2. Verify COM port permissions (Linux: add user to dialout group)
3. Test with different baud rates
4. Reset device to factory defaults

### Data Quality Issues
1. Check sensor connections
2. Verify power supply stability
3. Recalibrate sensors
4. Clean sensor surfaces

### Performance Issues
1. Reduce update rate if data drops
2. Check Bluetooth signal strength
3. Close other Bluetooth applications
4. Use serial connection for best performance
