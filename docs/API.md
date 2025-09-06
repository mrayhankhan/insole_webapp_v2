# API Documentation

## WebSocket API

### Connection
```
ws://localhost:8000/ws
```

### Incoming Messages (Client to Server)

#### Pattern Control (Simulation Mode Only)
```json
{
  "action": "pattern",
  "pattern": "walking|standing|running|clear"
}
```

#### Simulation Control
```json
{
  "action": "play|pause|stop|clear"
}
```

#### Sensor Testing (Simulation Mode Only)
```json
{
  "action": "test_sensor",
  "sensor": 0-7
}
```

### Outgoing Messages (Server to Client)

#### Sensor Data
```json
{
  "sensors": [12.5, 14.2, 11.8, 13.1, 12.9, 15.3, 16.0, 14.8],
  "timestamp": 1757190700.256,
  "pattern": "walking",
  "connection": "bluetooth|serial|null",
  "simulation_mode": true,
  "test_mode": false,
  "test_sensor": -1
}
```

#### Connection Status
```json
{
  "action": "connection_status",
  "simulation_mode": true,
  "connection_type": "bluetooth|serial|null",
  "device_name": "Smart Insole BLE"
}
```

## REST API

### Device Connection

#### Connect Bluetooth
```http
POST /api/connect/bluetooth
```

**Response:**
```json
{
  "status": "connected|error",
  "device": "Smart Insole BLE",
  "address": "XX:XX:XX:XX:XX:XX",
  "type": "bluetooth",
  "message": "Error message if failed"
}
```

#### Connect Serial
```http
POST /api/connect/serial
Content-Type: application/json

{
  "port": "/dev/ttyUSB0"  // Optional
}
```

**Response:**
```json
{
  "status": "connected|error",
  "device": "/dev/ttyUSB0",
  "response": "Device response",
  "type": "serial",
  "message": "Error message if failed"
}
```

#### Scan Serial Ports
```http
GET /api/scan/serial
```

**Response:**
```json
{
  "ports": [
    {
      "device": "/dev/ttyUSB0",
      "description": "Arduino Uno",
      "manufacturer": "Arduino LLC"
    }
  ]
}
```

#### Disconnect
```http
POST /api/disconnect
```

**Response:**
```json
{
  "status": "disconnected|error",
  "message": "Error message if failed"
}
```

### Data Access

#### Get Current Data
```http
GET /api/data/current
```

**Response:**
```json
{
  "sensors": {
    "sensor0": {
      "capacitance": 12.5,
      "filtered": 12.5,
      "force": 26.25
    }
  },
  "analysis": {
    "total_force": 210.0,
    "max_force": 35.0,
    "avg_force": 26.25,
    "gait_phase": "Heel Strike",
    "center_of_pressure": [95.2, 145.8]
  },
  "connection": {
    "type": "bluetooth",
    "device": "Smart Insole BLE",
    "simulation_mode": false
  }
}
```

## Error Codes

- **200**: Success
- **404**: Resource not found
- **500**: Internal server error

## Rate Limits

- WebSocket: No limits
- REST API: 100 requests per minute per IP
