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

// wss.on('connection', (ws) => {
//     console.log('WebSocket client connected');

//     ws.on('message', (message) => {
//         if (message.startsWith('key:')) {
//             const key = message.substring(4);
//             if (blenderProcess) {
//                 blenderProcess.stdin.write(key + '\n');
//             }
//         }
//     });

//     ws.on('close', () => {
//         console.log('WebSocket client disconnected');
//     });
// });

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

// Start Express server
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
    console.log(`WebSocket server listening on port ${webSocketPort}`);
});