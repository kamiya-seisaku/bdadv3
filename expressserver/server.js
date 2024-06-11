const express = require('express');
const app = express();
const port = 3000;
const path = require('path');
const ini = require('ini');
const fs = require('fs');
const WebSocket = require('ws');

const imgDir = path.join(__dirname, 'img');
console.log(imgDir);
const webSocketPort = 8080;

// // Serve images
// app.use('/img', express.static(imgDir));
// console.log('/img using');

// // WebSocket server
// const wss = new WebSocket.Server({ port: webSocketPort });

// // Read configuration from config.ini
// const config = ini.parse(fs.readFileSync('./config.ini', 'utf-8'));
// const maxFrame = 99; // Match the maxFrame in index.html
// let currentFrame = 0; 

// // Serve the latest image
// app.get('/latest-image', (req, res) => {
//     // const imageName = `ucd${currentFrame.toString().padStart(2, '0')}.png`;
//     const imageName = `ucd${currentFrame.toString()}.png`;
//     const imagePath = path.join(imgDir, imageName);

//     if (fs.existsSync(imagePath)) {
//         currentFrame = (currentFrame + 1) % (maxFrame + 1);
//         res.sendFile(imagePath);
//     } else {
//         res.status(404).send('Image not found'); 
//     }
// });

// Serve index.html
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
    console.log('index.html serving');
});

// Start Express server
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
    console.log(`WebSocket server listening on port ${webSocketPort}`);
});