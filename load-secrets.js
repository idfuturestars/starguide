// Enhanced secrets loader for IDFS StarGuide
console.log('🔑 Loading Replit Secrets...');

// Function to safely load secrets
async function loadSecrets() {
    try {
        const secrets = {};

        // List of required secrets
        const secretKeys = [
            'OPENAI_API_KEY',
            'CLAUDE_API_KEY', 
            'GEMINI_API_KEY',
            'OPENAI_MODEL'
        ];

        // Load from injected secrets (from build process)
        if (typeof window !== 'undefined' && window.INJECTED_SECRETS) {
            console.log('🔑 Using injected secrets from build process');
            for (const key of secretKeys) {
                if (window.INJECTED_SECRETS[key] && window.INJECTED_SECRETS[key].trim()) {
                    secrets[key] = window.INJECTED_SECRETS[key].trim();
                    console.log(`🔑 Found ${key} in injected secrets`);
                }
            }
        }

        // Fallback: Try environment variables if available
        if (typeof process !== 'undefined' && process.env) {
            for (const key of secretKeys) {
                if (!secrets[key] && process.env[key]) {
                    secrets[key] = process.env[key];
                    console.log(`🔑 Found ${key} in process.env`);
                }
            }
        }

        // Inject secrets into window for immediate use
        if (typeof window !== 'undefined') {
            window.INJECTED_SECRETS = {
                ...secrets,
                OPENAI_MODEL: secrets.OPENAI_MODEL || 'gpt-3.5-turbo'
            };

            // Also set individual keys for backward compatibility
            window.openaiKey = secrets.OPENAI_API_KEY || '';
            window.claudeKey = secrets.CLAUDE_API_KEY || '';
            window.geminiKey = secrets.GEMINI_API_KEY || '';

            console.log('🔑 Secrets loaded successfully:', {
                hasOpenAI: !!(secrets.OPENAI_API_KEY && secrets.OPENAI_API_KEY !== ''),
                hasClaude: !!(secrets.CLAUDE_API_KEY && secrets.CLAUDE_API_KEY !== ''),
                hasGemini: !!(secrets.GEMINI_API_KEY && secrets.GEMINI_API_KEY !== ''),
                providersConfigured: Object.keys(secrets).filter(key => secrets[key]).length
            });
        }

        return secrets;

    } catch (error) {
        console.error('🔑 Error loading secrets:', error);
        return {};
    }
}

// Function to refresh secrets manually
function refreshSecrets() {
    console.log('🔄 Refreshing secrets...');
    return loadSecrets().then(secrets => {
        console.log('🔑 Secrets refresh complete');

        // Update AI provider availability
        if (typeof window !== 'undefined' && window.aiProviders) {
            window.aiProviders.refreshKeys();
        }

        // Trigger a custom event when secrets are refreshed
        window.dispatchEvent(new CustomEvent('secretsRefreshed', { 
            detail: { secrets } 
        }));

        return secrets;
    });
}

// Load secrets immediately if in browser
if (typeof window !== 'undefined') {
    loadSecrets().then(secrets => {
        console.log('🔑 Secrets loading complete');

        // Trigger a custom event when secrets are loaded
        window.dispatchEvent(new CustomEvent('secretsLoaded', { 
            detail: { secrets } 
        }));
    });

    // Make refresh function globally available
    window.refreshSecrets = refreshSecrets;
}

// Export for Node.js if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { loadSecrets };
}