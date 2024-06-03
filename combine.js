const fs = require('fs');
const path = require('path');

const directory = './';
const outputFile = 'combined_code.txt';
const filesToCombine = [
    'README.md', 
    'expressserver/server.js', 
    'expressserver/index.html', 
    'expressserver/config.ini',
    'expressserver/package.json',
    'scripts/ksgame/__main__.py', 
]; // list of files to be combined

function combineFiles(directoryPath, outputFilePath, filesToInclude) {
    const ignorePatterns = getIgnorePatterns(); // Function to read .combine_ignore
    let combinedContent = '';

    for (const file of filesToInclude) {
        const filePath = path.join(directoryPath, file);
        if (fs.existsSync(filePath) && !isIgnored(filePath, ignorePatterns)) {
            console.log(`Adding ${file} to ${outputFilePath}`);
            const fileContent = fs.readFileSync(filePath, 'utf-8');
            combinedContent += `// --- [${file}] -------------------------------\n\n${fileContent}\\nn\n`;
        } else {
            console.warn(`File not found or ignored: ${file}`);
        }
    }

    fs.writeFileSync(outputFilePath, combinedContent, 'utf-8');
}

function getIgnorePatterns() {
    try {
        const ignoreFileContent = fs.readFileSync('.combine_ignore', 'utf-8');
        return ignoreFileContent.split('\n').filter(Boolean).map(pattern => pattern.trim());
    } catch (err) {
        return [];
    }
}

function isIgnored(filePath, ignorePatterns) {
    for (const pattern of ignorePatterns) {
        if (filePath.includes(pattern)) {
            return true;
        }
    }
    return false;
}

combineFiles(directory, outputFile, filesToCombine);
