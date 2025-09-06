# Smart Insole Analytics Web Application v2

A professional real-time gait analysis and pressure monitoring system for smart insoles with advanced visualization capabilities.

## 🌟 Features

### 📱 Real Device Support
- **Bluetooth Connectivity**: Scan and connect to real Smart Insole devices via Bluetooth
- **Serial Communication**: Detect and connect to devices via USB/Serial ports
- **Auto-Detection**: Intelligent device scanning with proper error handling
- **Live Data Streaming**: Real-time sensor data from connected hardware

### 🎮 Simulation Mode
- **Demo Mode**: Full simulation when no hardware is available
- **Realistic Patterns**: Walking, standing, and running gait simulations
- **Individual Sensor Testing**: Test specific sensors in isolation
- **Smart UI**: Simulation controls automatically hide when real device is connected

### 📊 Professional Visualization
- **Real-time Plotting**: 8-channel sensor data with Plotly.js
- **Pressure Heatmap**: Visual foot pressure overlay on anatomical foot image
- **Gait Analysis**: Automatic gait phase detection (Heel Strike, Stance, Toe Off, Swing)
- **Force Calculations**: Real-time force and pressure calculations

### 🌙 Modern Dark Theme
- **Professional Design**: Beautiful dark gradient interface
- **High Contrast**: Optimized for long-term use
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Glassmorphism**: Modern UI with backdrop blur effects

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/mrayhankhan/insole_webapp_v2.git
cd insole_webapp_v2
```

2. **Install dependencies:**
```bash
pip install fastapi uvicorn websockets numpy pyserial pybluez
```

3. **Run the server:**
```bash
python professional_server.py
```

4. **Open your browser:**
Navigate to `http://localhost:8000`

## 🔧 Hardware Requirements

### For Real Device Connection:
- **Smart Insole Device** with 8 capacitive sensors
- **Bluetooth**: ESP32 or similar with Bluetooth capability
- **Serial**: Arduino/ESP32 with USB connection
- **Data Format**: Comma-separated values (sensor1,sensor2,...,sensor8)

### Device Communication Protocol:
```
# Serial/Bluetooth Output Format:
12.5,14.2,11.8,13.1,12.9,15.3,16.0,14.8
```

## 📁 Project Structure

```
insole_webapp_v2/
├── professional_server.py      # FastAPI backend server
├── professional_dashboard.html # Frontend interface
├── foot-outline.png            # Foot anatomy image
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── docs/                       # Documentation
    ├── API.md                  # API documentation
    ├── HARDWARE.md             # Hardware setup guide
    └── DEPLOYMENT.md           # Deployment instructions
```

## 🔌 API Endpoints

### WebSocket
- `ws://localhost:8000/ws` - Real-time sensor data streaming

### REST API
- `POST /api/connect/bluetooth` - Connect to Bluetooth device
- `POST /api/connect/serial` - Connect to Serial device
- `GET /api/scan/serial` - Scan available serial ports
- `POST /api/disconnect` - Disconnect from device
- `GET /api/data/current` - Get current sensor readings and analysis

## 🎯 Use Cases

### 🏥 Medical Applications
- **Gait Analysis**: Clinical gait assessment and rehabilitation
- **Balance Assessment**: Center of pressure analysis
- **Injury Prevention**: Early detection of abnormal gait patterns
- **Recovery Monitoring**: Track rehabilitation progress

### 🏃 Sports & Fitness
- **Performance Analysis**: Optimize running technique
- **Training Monitoring**: Track training load and intensity
- **Injury Prevention**: Identify risk factors in movement patterns
- **Equipment Testing**: Analyze shoe and insole performance

### 🔬 Research Applications
- **Biomechanics Research**: Collect detailed gait data
- **Device Development**: Test and validate new sensor technologies
- **Data Collection**: Large-scale gait pattern studies
- **Algorithm Development**: Train machine learning models

## 🛠️ Configuration

### Sensor Mapping
The system expects 8 sensors positioned as follows:
1. **Sensor 1-3**: Toe area (hallux, second toe, lateral toes)
2. **Sensor 4-6**: Midfoot area (medial, central, lateral)
3. **Sensor 7-8**: Heel area (medial heel, lateral heel)

### Calibration
- **Baseline Values**: Automatically calibrated on startup
- **Force Conversion**: Configurable capacitance-to-force mapping
- **Noise Reduction**: Built-in filtering algorithms

## 🚀 Deployment

### Local Development
```bash
python professional_server.py
```

### Production Deployment
```bash
# Using Docker
docker build -t insole-webapp .
docker run -p 8000:8000 insole-webapp

# Using systemd service
sudo systemctl enable insole-webapp
sudo systemctl start insole-webapp
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **M. Rayhan Khan** - *Initial work* - [@mrayhankhan](https://github.com/mrayhankhan)

## 🙏 Acknowledgments

- Thanks to the open-source community for the amazing libraries
- Plotly.js for excellent real-time plotting capabilities
- FastAPI for the robust backend framework
- The biomechanics research community for inspiration

## 📞 Support

For support, email rayhan@example.com or open an issue on GitHub.

---

**Made with ❤️ for the biomechanics and sports science community**
