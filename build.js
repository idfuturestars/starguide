const fs = require('fs');
const path = require('path');

console.log('🔧 Building IDFS StarGuide with Replit Secrets...');

// Read environment variables from Replit Secrets
const openaiKey = process.env['OPENAI_API_KEY'] || '';
const openaiModel = process.env['OPENAI_MODEL'] || 'gpt-3.5-turbo';
const claudeKey = process.env['CLAUDE_API_KEY'] || '';
const geminiKey = process.env['GEMINI_API_KEY'] || '';

console.log('🔍 Environment check:');
console.log('- OPENAI_API_KEY:', openaiKey ? 'Found' : 'Not found');
console.log('- CLAUDE_API_KEY:', claudeKey ? 'Found' : 'Not found');
console.log('- GEMINI_API_KEY:', geminiKey ? 'Found' : 'Not found');
console.log('- OPENAI_MODEL:', openaiModel);

// Read the index.html file
const indexPath = path.join(__dirname, 'index.html');
let indexContent;
try {
    indexContent = fs.readFileSync(indexPath, 'utf8');
} catch (error) {
    console.error('❌ Error reading index.html:', error.message);
    process.exit(1);
}

// Prepare secrets for injection
const secrets = {
    OPENAI_API_KEY: openaiKey,
    CLAUDE_API_KEY: claudeKey,
    GEMINI_API_KEY: geminiKey,
    OPENAI_MODEL: openaiModel
};

// Create secrets injection script
const secretsScript = `
<script>
window.INJECTED_SECRETS = ${JSON.stringify(secrets, null, 2)};
console.log('🔧 Secrets injected from build process');
</script>
`;

// Replace existing secrets script or insert before closing head tag
const secretsPattern = /<script>\s*window\.INJECTED_SECRETS\s*=[\s\S]*?<\/script>/g;
if (secretsPattern.test(indexContent)) {
    indexContent = indexContent.replace(secretsPattern, secretsScript);
} else {
    indexContent = indexContent.replace('</head>', `${secretsScript}</head>`);
}

// Write back to file
try {
    fs.writeFileSync(indexPath, indexContent);
    console.log('✅ Build complete with secrets injected');
} catch (error) {
    console.error('❌ Error writing index.html:', error.message);
    process.exit(1);
}
console.log('Available secrets count:', Object.keys(secrets).filter(key => secrets[key] && secrets[key] !== '').length);