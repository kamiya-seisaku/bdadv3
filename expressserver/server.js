const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const imgDir = path.join(__dirname, 'img');

// Serve the index.html file at the root URL
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/latest-image', (req, res) => {
    fs.readdir(imgDir, (err, files) => {
        if (err) {
            console.error(err);
            res.status(500).send('Error reading image directory');
            return;
        }

        // Filter out the ucd*.png files
        const ucdFiles = files.filter(file => file.startsWith('ucd') && file.endsWith('.png'));

        // Get the latest file
        const latestFile = ucdFiles.sort((a, b) => {
            return fs.statSync(path.join(imgDir, b)).mtime.getTime() - 
                   fs.statSync(path.join(imgDir, a)).mtime.getTime();
        })[0];

        // Send the latest file
        res.sendFile(path.join(imgDir, latestFile));
    });
});

app.listen(3000, () => {
    console.log('Server listening on port 3000');
});
