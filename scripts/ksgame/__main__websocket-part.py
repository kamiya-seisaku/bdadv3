##############################
#server/client websocket

# 6/11 from gemini
import asyncio
import websockets
import subprocess

# Replace with your Node.js Express app's WebSocket URL
uri = "ws://localhost:<your_websocket_port>"  # Replace "<your_websocket_port>" with the actual port

async def handle_incoming_message(message):
  if message.startswith("key:"):
    key = message.substring(4)  # Python doesn't have substring, use slicing instead
    key = key.strip()  # Remove potential leading/trailing whitespace

    # Send the key to Blender process (assuming Blender is running game.blend)
    with open("game.blend", "a") as blend_file:
      blend_file.write(f"{key}\n")

async def main():
  async with websockets.serve(handle_incoming_message, "", websockets.serve_forever):
    # Start serving WebSocket connections
    print("WebSocket server listening...")
    await asyncio.Future()  # Wait indefinitely

# Start the WebSocket server
asyncio.run(main())


##############################
#client only

import asyncio
import websockets

# Replace with your Node.js Express app's WebSocket URL
uri = "ws://localhost:<your_websocket_port>"  # Replace "<your_websocket_port>" with the actual port

async def handle_incoming_message(message):
  if message.startswith("key:"):
    key = message.substring(4)  # Python doesn't have substring, use slicing instead
    key = key.strip()  # Remove potential leading/trailing whitespace
    print(f"Received key press: {key}")

async def main():
  async with websockets.connect(uri) as websocket:
    await websocket.recv()  # Wait for the first message (optional)
    await websocket.wait_closed()  # Wait for the connection to close

if __name__ == "__main__":
  asyncio.run(main())
