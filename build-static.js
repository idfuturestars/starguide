
const fs = require('fs');
const path = require('path');

console.log('🔧 Building static version of IDFS StarGuide...');

// Create public directory
const publicDir = path.join(__dirname, 'public');
if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir);
}

// Copy main files to public directory
const filesToCopy = [
    'index.html',
    'config.js',
    'manifest.json'
];

filesToCopy.forEach(file => {
    if (fs.existsSync(file)) {
        fs.copyFileSync(file, path.join(publicDir, file));
        console.log(`✅ Copied ${file} to public/`);
    }
});

// Copy assets if they exist
const assetsDir = path.join(__dirname, 'assets');
const publicAssetsDir = path.join(publicDir, 'assets');
if (fs.existsSync(assetsDir)) {
    if (!fs.existsSync(publicAssetsDir)) {
        fs.mkdirSync(publicAssetsDir);
    }
    // Copy assets recursively would go here
}

// Read and modify index.html for static deployment
const indexPath = path.join(publicDir, 'index.html');
let indexContent = fs.readFileSync(indexPath, 'utf8');

// Remove server-dependent features for static version
indexContent = indexContent.replace(/<!-- Socket\.IO.*?-->/g, '');
indexContent = indexContent.replace(/socket\.io\/socket\.io\.js/g, '#');

// Add note about limited functionality
const staticNote = `
<div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px; border-radius: 5px; text-align: center;">
    <strong>Static Version:</strong> Some features like real-time chat, battles, and server-side AI are not available in this static deployment.
</div>
`;

indexContent = indexContent.replace('<body>', `<body>${staticNote}`);

fs.writeFileSync(indexPath, indexContent);

console.log('✅ Static build complete! Files are in the public/ directory');
console.log('📁 Use "./public" as your public directory in Static Deployment');
