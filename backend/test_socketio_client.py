import socketio

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to WebSocket")
    sio.emit('message', "Hello from Python client")

@sio.event
def message(data):
    print(f"Received message: {data}")

@sio.event
def disconnect():
    print("Disconnected")

# Connect to the server
try:
    sio.connect('http://localhost:5000', namespaces=['/socket.io'])
    sio.wait()
except Exception as e:
    print(f"Connection failed: {e}")