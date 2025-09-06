#!/usr/bin/env python3
"""
Professional Smart Insole Analytics Server
Real Bluetooth/Serial Detection with Hidden Simulation Controls
"""

import asyncio
import json
import time
import math
import random
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import numpy as np

# Real device detection imports
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False

class SmartInsoleServer:
    def __init__(self):
        self.app = FastAPI(title="Professional Smart Insole Analytics Server")
        self.connected_clients: List[WebSocket] = []
        self.is_running = True
        self.current_pattern = 'walking'
        self.sensor_data = {'sensors': [0.0] * 8}
        self.data_history = []
        
        # Real device connection
        self.connection_type = None
        self.device_name = None
        self.serial_connection = None
        self.bluetooth_connection = None
        self.is_simulation_mode = True  # Start in simulation mode
        
        # Enhanced simulation parameters
        self.simulation_time = 0
        self.noise_level = 0.5
        self.baseline_values = [2.0, 2.2, 1.8, 2.1, 1.9, 2.3, 2.0, 1.8]
        self.sensor_ranges = [(10, 20), (12, 22), (8, 18), (10, 20), 
                             (9, 19), (11, 21), (15, 25), (14, 24)]
        
        # Individual sensor testing (only in simulation mode)
        self.test_mode = False
        self.test_sensor_index = -1
        self.test_duration = 0
        
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            try:
                with open("professional_dashboard.html", "r") as f:
                    return HTMLResponse(content=f.read())
            except FileNotFoundError:
                return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)
        
        @self.app.get("/foot-outline.png")
        async def serve_foot_image():
            """Serve the foot outline PNG image"""
            try:
                return FileResponse("foot-outline.png", media_type="image/png")
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail="Foot image not found")
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.connected_clients.append(websocket)
            print(f"🔌 Client connected. Total clients: {len(self.connected_clients)}")
            
            # Send initial connection status
            await websocket.send_text(json.dumps({
                'action': 'connection_status',
                'simulation_mode': self.is_simulation_mode,
                'connection_type': self.connection_type,
                'device_name': self.device_name
            }))
            
            try:
                while True:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                    await self.handle_websocket_message(data, websocket)
                    
            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)
                print(f"🔌 Client disconnected. Total clients: {len(self.connected_clients)}")
            except Exception as e:
                print(f"❌ WebSocket error: {e}")
                if websocket in self.connected_clients:
                    self.connected_clients.remove(websocket)
        
        @self.app.post("/api/connect/bluetooth")
        async def connect_bluetooth():
            """Real Bluetooth device detection and connection"""
            print("📱 Bluetooth connection requested")
            
            if not BLUETOOTH_AVAILABLE:
                return {
                    "status": "error", 
                    "message": "Bluetooth library not available. Install pybluez.",
                    "type": "bluetooth"
                }
            
            try:
                # Scan for nearby Bluetooth devices
                print("🔍 Scanning for Bluetooth devices...")
                nearby_devices = bluetooth.discover_devices(duration=5, lookup_names=True)
                
                # Look for Smart Insole devices
                insole_devices = []
                for addr, name in nearby_devices:
                    if name and any(keyword in name.lower() for keyword in ['insole', 'pressure', 'sensor', 'esp32', 'arduino']):
                        insole_devices.append((addr, name))
                
                if not insole_devices:
                    return {
                        "status": "error",
                        "message": "No Smart Insole devices found. Make sure device is paired and in range.",
                        "devices_found": len(nearby_devices),
                        "type": "bluetooth"
                    }
                
                # Try to connect to the first compatible device
                addr, name = insole_devices[0]
                print(f"🔗 Attempting to connect to: {name} ({addr})")
                
                # Create RFCOMM socket connection
                self.bluetooth_connection = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.bluetooth_connection.connect((addr, 1))  # Port 1 for RFCOMM
                
                self.connection_type = "bluetooth"
                self.device_name = name
                self.is_simulation_mode = False
                
                # Notify all clients about connection status change
                await self.broadcast_connection_status()
                
                return {
                    "status": "connected",
                    "device": name,
                    "address": addr,
                    "type": "bluetooth"
                }
                
            except bluetooth.BluetoothError as e:
                print(f"❌ Bluetooth connection failed: {e}")
                return {
                    "status": "error",
                    "message": f"Bluetooth connection failed: {str(e)}",
                    "type": "bluetooth"
                }
            except Exception as e:
                print(f"❌ General Bluetooth error: {e}")
                return {
                    "status": "error",
                    "message": f"Bluetooth error: {str(e)}",
                    "type": "bluetooth"
                }
        
        @self.app.post("/api/connect/serial")
        async def connect_serial(port: str = None):
            """Real Serial port detection and connection"""
            print(f"🔗 Serial connection requested")
            
            if not SERIAL_AVAILABLE:
                return {
                    "status": "error",
                    "message": "Serial library not available. Install pyserial.",
                    "type": "serial"
                }
            
            try:
                # Get available serial ports
                available_ports = await self.scan_real_serial_ports()
                
                if not available_ports["ports"]:
                    return {
                        "status": "error",
                        "message": "No serial devices found. Connect your Smart Insole device.",
                        "type": "serial"
                    }
                
                # Use specified port or first available
                target_port = port if port else available_ports["ports"][0]["device"]
                
                # Try to connect
                print(f"🔗 Attempting to connect to: {target_port}")
                self.serial_connection = serial.Serial(
                    port=target_port,
                    baudrate=115200,
                    timeout=2
                )
                
                # Test connection by sending a ping
                self.serial_connection.write(b"PING\n")
                response = self.serial_connection.readline().decode().strip()
                
                if not response:
                    self.serial_connection.close()
                    return {
                        "status": "error",
                        "message": f"Device on {target_port} is not responding. Check if it's a Smart Insole device.",
                        "type": "serial"
                    }
                
                self.connection_type = "serial"
                self.device_name = target_port
                self.is_simulation_mode = False
                
                # Notify all clients about connection status change
                await self.broadcast_connection_status()
                
                return {
                    "status": "connected",
                    "device": target_port,
                    "response": response,
                    "type": "serial"
                }
                
            except serial.SerialException as e:
                print(f"❌ Serial connection failed: {e}")
                return {
                    "status": "error",
                    "message": f"Serial connection failed: {str(e)}",
                    "type": "serial"
                }
            except Exception as e:
                print(f"❌ General serial error: {e}")
                return {
                    "status": "error",
                    "message": f"Serial error: {str(e)}",
                    "type": "serial"
                }
        
        @self.app.get("/api/scan/serial")
        async def scan_serial_ports():
            """Real serial port scanning"""
            return await self.scan_real_serial_ports()
        
        @self.app.post("/api/disconnect")
        async def disconnect():
            """Disconnect from real device"""
            print("❌ Disconnection requested")
            
            try:
                if self.serial_connection:
                    self.serial_connection.close()
                    self.serial_connection = None
                
                if self.bluetooth_connection:
                    self.bluetooth_connection.close()
                    self.bluetooth_connection = None
                
                self.connection_type = None
                self.device_name = None
                self.is_simulation_mode = True  # Return to simulation mode
                
                # Notify all clients about connection status change
                await self.broadcast_connection_status()
                
                return {"status": "disconnected"}
                
            except Exception as e:
                print(f"❌ Disconnect error: {e}")
                return {"status": "error", "message": str(e)}
        
        @self.app.get("/api/data/current")
        async def get_current_data():
            """Get current sensor readings and analysis"""
            forces = [max(0, (val - 2) * 2.5) for val in self.sensor_data['sensors']]
            total_force = sum(forces)
            max_force = max(forces) if forces else 0
            avg_force = total_force / len(forces) if forces else 0
            
            # Gait phase detection
            heel_pressure = (forces[6] + forces[7]) / 2 if len(forces) >= 8 else 0
            toe_pressure = (forces[0] + forces[1] + forces[2]) / 3 if len(forces) >= 3 else 0
            
            gait_phase = 'Swing'
            if heel_pressure > 5:
                gait_phase = 'Heel Strike'
            elif avg_force > 3:
                gait_phase = 'Stance'
            elif toe_pressure > 5:
                gait_phase = 'Toe Off'
            
            return {
                "sensors": {
                    f"sensor{i}": {
                        "capacitance": self.sensor_data['sensors'][i],
                        "filtered": self.sensor_data['sensors'][i],
                        "force": forces[i]
                    } for i in range(8)
                },
                "analysis": {
                    "total_force": total_force,
                    "max_force": max_force,
                    "avg_force": avg_force,
                    "gait_phase": gait_phase,
                    "center_of_pressure": self.calculate_center_of_pressure(forces)
                },
                "connection": {
                    "type": self.connection_type,
                    "device": self.device_name,
                    "simulation_mode": self.is_simulation_mode
                }
            }
    
    async def scan_real_serial_ports(self):
        """Scan for real serial ports"""
        ports = []
        try:
            available_ports = serial.tools.list_ports.comports()
            for port in available_ports:
                ports.append({
                    "device": port.device,
                    "description": port.description,
                    "manufacturer": port.manufacturer or "Unknown"
                })
        except Exception as e:
            print(f"❌ Error scanning serial ports: {e}")
        
        return {"ports": ports}
    
    async def broadcast_connection_status(self):
        """Broadcast connection status to all clients"""
        message = json.dumps({
            'action': 'connection_status',
            'simulation_mode': self.is_simulation_mode,
            'connection_type': self.connection_type,
            'device_name': self.device_name
        })
        
        for client in self.connected_clients:
            try:
                await client.send_text(message)
            except:
                pass
    
    async def handle_websocket_message(self, data: dict, websocket: WebSocket):
        """Handle incoming WebSocket messages"""
        action = data.get('action')
        
        # Only allow simulation controls when in simulation mode
        if not self.is_simulation_mode and action in ['pattern', 'test_sensor', 'play', 'pause', 'stop', 'clear']:
            await websocket.send_text(json.dumps({
                'error': 'Simulation controls disabled when real device is connected'
            }))
            return
        
        if action == 'pattern':
            pattern = data.get('pattern', 'walking')
            if pattern == 'clear':
                self.current_pattern = 'none'
                self.is_running = False
                self.test_mode = False
                print("🛑 Simulation stopped completely")
            else:
                self.current_pattern = pattern
                self.is_running = True
                self.test_mode = False
                print(f"🎮 Pattern changed to: {self.current_pattern}")
            
        elif action == 'test_sensor':
            sensor_index = data.get('sensor', 0)
            await self.start_individual_sensor_test(sensor_index)
            
        elif action == 'play':
            self.is_running = True
            self.test_mode = False
            print("▶️ Simulation resumed")
            
        elif action == 'pause':
            self.is_running = False
            print("⏸️ Simulation paused")
            
        elif action == 'stop':
            self.is_running = False
            self.test_mode = False
            self.current_pattern = 'none'
            print("⏹️ Simulation stopped")
            
        elif action == 'clear':
            self.is_running = False
            self.test_mode = False
            self.current_pattern = 'none'
            print("🗑️ Simulation cleared and stopped")
    
    def calculate_center_of_pressure(self, forces: List[float]) -> Optional[List[float]]:
        """Calculate center of pressure based on sensor forces"""
        positions = [
            [100, 50], [85, 75], [115, 75], [100, 100],
            [85, 130], [115, 130], [90, 200], [110, 200]
        ]
        
        total_weight = sum(forces)
        if total_weight <= 0:
            return None
        
        center_x = sum(pos[0] * force for pos, force in zip(positions, forces)) / total_weight
        center_y = sum(pos[1] * force for pos, force in zip(positions, forces)) / total_weight
        
        return [center_x, center_y]
    
    async def start_individual_sensor_test(self, sensor_index: int):
        """Start testing individual sensor (only in simulation mode)"""
        if not self.is_simulation_mode:
            return
            
        self.test_mode = True
        self.test_sensor_index = sensor_index
        self.test_duration = 30
        self.is_running = True
        
        print(f"🧪 Testing sensor {sensor_index} individually")
    
    async def read_real_device_data(self) -> Optional[List[float]]:
        """Read data from real device"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                # Read line from serial
                line = self.serial_connection.readline().decode().strip()
                if line:
                    # Parse sensor data (expecting comma-separated values)
                    values = [float(x) for x in line.split(',')]
                    if len(values) == 8:
                        return values
            
            elif self.bluetooth_connection:
                # Read from Bluetooth
                data = self.bluetooth_connection.recv(1024).decode().strip()
                if data:
                    values = [float(x) for x in data.split(',')]
                    if len(values) == 8:
                        return values
                        
        except Exception as e:
            print(f"❌ Error reading device data: {e}")
            # Connection lost, return to simulation mode
            self.is_simulation_mode = True
            self.connection_type = None
            self.device_name = None
            await self.broadcast_connection_status()
        
        return None
    
    def generate_realistic_data(self) -> List[float]:
        """Generate realistic sensor data based on current pattern (simulation only)"""
        if not self.is_simulation_mode:
            return self.sensor_data.get('sensors', [0.0] * 8)
            
        self.simulation_time += 0.1
        sensors = []
        
        # Handle individual sensor testing
        if self.test_mode and self.test_duration > 0:
            self.test_duration -= 1
            
            for i in range(8):
                if i == self.test_sensor_index:
                    sensors.append(15 + random.uniform(2, 5))
                else:
                    sensors.append(self.baseline_values[i] + random.uniform(-0.2, 0.2))
            
            if self.test_duration <= 0:
                self.test_mode = False
                print(f"✅ Sensor {self.test_sensor_index} test completed")
            
            return sensors
        
        # Normal pattern simulation
        for i in range(8):
            base_noise = self.baseline_values[i] + random.uniform(-0.3, 0.3) * self.noise_level
            sensor_value = base_noise
            
            if self.current_pattern == 'walking':
                phase = (self.simulation_time + i * 0.1) % 2.0
                if phase < 1.0:
                    if i in [6, 7]:  # Heel sensors
                        sensor_value += 8 + math.sin(phase * math.pi) * 6
                    elif i in [0, 1, 2]:  # Toe sensors
                        sensor_value += 4 + math.sin((phase + 0.5) * math.pi) * 8
                    elif i in [3, 4, 5]:  # Mid-foot sensors
                        sensor_value += 3 + math.sin((phase + 0.3) * math.pi) * 5
                        
            elif self.current_pattern == 'standing':
                shift = math.sin(self.simulation_time * 0.3) * 2
                if i in [6, 7]:
                    sensor_value += 6 + shift + math.sin(self.simulation_time * 0.5 + i) * 2
                elif i in [3, 4, 5]:
                    sensor_value += 3 + shift * 0.5
                else:
                    sensor_value += 1 + shift * 0.3
                    
            elif self.current_pattern == 'running':
                phase = (self.simulation_time * 1.8 + i * 0.05) % 1.2
                if phase < 0.4:
                    impact_factor = math.sin(phase * math.pi / 0.4)
                    if i in [6, 7]:
                        sensor_value += 12 + impact_factor * 8
                    elif i in [0, 1, 2]:
                        sensor_value += 8 + impact_factor * 10
                    elif i in [3, 4, 5]:
                        sensor_value += 6 + impact_factor * 6
            
            elif self.current_pattern == 'none':
                sensor_value = base_noise
            
            min_val, max_val = self.sensor_ranges[i]
            sensors.append(max(0, min(max_val, sensor_value)))
        
        return sensors
    
    async def broadcast_sensor_data(self, sensor_values: List[float]):
        """Broadcast sensor data to all connected clients"""
        if not self.connected_clients:
            return
        
        data = {
            'sensors': sensor_values,
            'timestamp': time.time(),
            'pattern': self.current_pattern,
            'connection': self.connection_type,
            'simulation_mode': self.is_simulation_mode,
            'test_mode': self.test_mode,
            'test_sensor': self.test_sensor_index if self.test_mode else -1
        }
        
        self.sensor_data = data
        self.data_history.append(data)
        if len(self.data_history) > 1000:
            self.data_history.pop(0)
        
        message = json.dumps(data)
        disconnected = []
        
        for client in self.connected_clients:
            try:
                await client.send_text(message)
            except Exception as e:
                disconnected.append(client)
        
        for client in disconnected:
            if client in self.connected_clients:
                self.connected_clients.remove(client)
    
    async def simulation_loop(self):
        """Main data loop"""
        print("🎮 Starting professional data loop...")
        
        while True:
            try:
                if self.connected_clients:
                    if self.is_simulation_mode:
                        # Use simulation data
                        if self.is_running:
                            sensor_data = self.generate_realistic_data()
                            await self.broadcast_sensor_data(sensor_data)
                    else:
                        # Try to read from real device
                        real_data = await self.read_real_device_data()
                        if real_data:
                            await self.broadcast_sensor_data(real_data)
                
                await asyncio.sleep(0.1)  # 10 Hz update rate
                
            except Exception as e:
                print(f"❌ Data loop error: {e}")
                await asyncio.sleep(1)

async def main():
    print("🚀 Professional Smart Insole Analytics Server Starting...")
    print("📊 Dashboard: http://localhost:8000")
    print("🖼️ PNG Image Support: ENABLED")
    print("🔗 API: http://localhost:8000/api/")
    print("📱 Real Bluetooth Detection: ENABLED" if BLUETOOTH_AVAILABLE else "📱 Bluetooth: Install pybluez")
    print("🔗 Real Serial Detection: ENABLED" if SERIAL_AVAILABLE else "🔗 Serial: Install pyserial")
    print("🎮 Simulation Mode: Active (will hide when real device connects)")
    print()
    
    server = SmartInsoleServer()
    
    simulation_task = asyncio.create_task(server.simulation_loop())
    
    config = uvicorn.Config(
        server.app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info"
    )
    web_server = uvicorn.Server(config)
    
    try:
        await asyncio.gather(
            simulation_task,
            web_server.serve()
        )
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        simulation_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
