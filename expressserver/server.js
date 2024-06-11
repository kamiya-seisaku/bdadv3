const ini = require('ini');
const express = require('express');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

const app = express();
const imgDir = path.join(__dirname, 'img');
console.log(imgDir)
const port = 3000;
const webSocketPort = 8080;

// Serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Serve images
app.use('/img', express.static(imgDir));

// WebSocket server
const wss = new WebSocket.Server({ port: webSocketPort });
let blenderProcess = null;

// WebSocket client is to be implemented in blender 
// here pass through message and just console log key for now
wss.on('connection', (ws) => {
    console.log('WebSocket client connected');

    // [TODO]: To be removed: 
    // WebSocket client is to be implemented in blender 
    // ws.on('message', (message) => {
    //     const message_str = String(message);
    //     if (message_str.startsWith('key:')) {
    //         const key_str = message_str.substring(4);
    //         if (blenderProcess) {
    //             blenderProcess.stdin.write(key_str + '\n');
    //         }
    //     }
    // });

    // ws.on('close', () => {
    //     console.log('WebSocket client disconnected');
    //     webSocket = new WebSocket('ws://localhost:8080');
    //     console.log('WebSocket client reestablished');
    // });
});

// Read configuration from config.ini
const config = ini.parse(fs.readFileSync('./config.ini', 'utf-8'));
const maxFrame = 99; // Match the maxFrame in index.html
let currentFrame = 0; 

// Serve the latest image
app.get('/latest-image', (req, res) => {
    // const imageName = `ucd${currentFrame.toString().padStart(2, '0')}.png`;
    const imageName = `ucd${currentFrame.toString()}.png`;
    const imagePath = path.join(imgDir, imageName);

    if (fs.existsSync(imagePath)) {
        currentFrame = (currentFrame + 1) % (maxFrame + 1);
        res.sendFile(imagePath);
    } else {
        res.status(404).send('Image not found'); 
    }
});


// // Start Blender process
// blenderProcess = require('child_process').spawn(config.blender.exePath, [
//     '-b', // Background mode (no UI)
//     '-P', config.blender.launchscript, // Run the Python script
//     config.blender.blendFile
// ]);

// blenderProcess.stdout.on('data', (data) => {
//     console.log(`Blender output: ${data}`);
// });

// blenderProcess.stderr.on('data', (data) => {
//     console.error(`Blender error: ${data}`);
// });

// blenderProcess.on('close', (code) => {
//     console.log(`Blender process exited with code ${code}`);
// });

// Start Express server
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
    console.log(`WebSocket server listening on port ${webSocketPort}`);
});