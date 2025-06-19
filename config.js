// IDFS StarGuide Configuration
console.log('🔧 Loading StarGuide Configuration...');

// Stronger guard against multiple executions
if (window.starguideConfigLoaded) {
    console.log('🔧 StarGuide configuration already loaded, skipping...');
} else if (window.starguideConfigLoading) {
    console.log('🔧 StarGuide configuration already loading, skipping...');
} else {
    // Mark as loading immediately
    window.starguideConfigLoading = true;

    // Main configuration object
    window.starGuideConfig = {
        version: "1.0.0",
        features: {
            realTimeChat: true,
            battleArena: true,
            aiQuestions: true,
            achievements: true
        }
    };

    // Firebase Configuration
    const firebaseConfig = {
        apiKey: "AIzaSyCujSh0q3ScaMAAl9czorKRtXcUcYLiLKI",
        authDomain: "stargate-dcfb7.firebaseapp.com",
        projectId: "stargate-dcfb7",
        storageBucket: "stargate-dcfb7.firebasestorage.app",
        messagingSenderId: "826981107429",
        appId: "1:826981107429:web:f346421800e6348b64360c",
        databaseURL: "https://stargate-dcfb7-default-rtdb.firebaseio.com",
        measurementId: "G-L9KCCD0RV9"
    };

    // Make firebaseConfig available globally
    window.firebaseConfig = firebaseConfig;

    // Helper function to get environment variables
    function getEnvVar(varName, fallback) {
        if (typeof window !== 'undefined' && window.INJECTED_SECRETS && window.INJECTED_SECRETS[varName]) {
            return window.INJECTED_SECRETS[varName];
        }
        if (typeof window !== 'undefined' && window.env && window.env[varName]) {
            return window.env[varName];
        }
        return fallback;
    }

    // Multi-AI Provider Configuration
    const openaiKey = getEnvVar('OPENAI_API_KEY', '');
    const claudeKey = getEnvVar('CLAUDE_API_KEY', '');
    const geminiKey = getEnvVar('GEMINI_API_KEY', '');
    const openaiModel = getEnvVar('OPENAI_MODEL', 'gpt-3.5-turbo');

    // Enhanced AI configuration object
    window.aiConfig = {
        openaiKey: openaiKey,
        claudeKey: claudeKey,
        geminiKey: geminiKey,
        model: openaiModel,
        providers: {
            openai: {
                name: 'OpenAI',
                model: openaiModel,
                available: !!(openaiKey && openaiKey.length > 10)
            },
            claude: {
                name: 'Claude',
                model: 'claude-3-sonnet-20240229',
                available: !!(claudeKey && claudeKey.length > 10)
            },
            gemini: {
                name: 'Gemini',
                model: 'gemini-pro',
                available: !!(geminiKey && geminiKey.length > 10)
            }
        }
    };

    // Set global variables for compatibility
    window.openaiKey = openaiKey;
    window.claudeKey = claudeKey;
    window.geminiKey = geminiKey;

    // Enhanced Error Logging System
    window.errorLog = window.errorLog || [];
    window.errorStats = {
        totalErrors: 0,
        criticalErrors: 0,
        recoveredErrors: 0,
        lastError: null
    };

    // Platform Configuration (Don't change these)
    window.platformConfig = {
        appName: 'IDFS StarGuide',
        version: '1.0.0',
        features: {
            realTimeChat: true,
            battleArena: true,
            aiQuestions: true,
            achievements: true
        }
    };

    // Log configuration status
    const availableProviders = Object.entries(window.aiConfig.providers)
        .filter(([key, provider]) => provider.available)
        .map(([key, provider]) => provider.name);

    if (availableProviders.length > 0) {
        console.log('✅ Multi-AI Config initialized successfully');
        console.log('🔧 Available providers:', availableProviders.join(', '));
    } else {
        console.log('🔧 Multi-AI Config initialized without any API keys');
        console.log('🔧 To enable AI features, add API keys to Secrets');
    }

    // Success check - Firebase will be loaded separately when needed
    console.log('🚀 IDFS StarGuide is ready!');
    console.log('📚 All features enabled');
    console.log('🔧 Configuration loaded successfully');

    console.log('✅ StarGuide Configuration loaded successfully');

    // Mark as fully loaded - THIS IS CRITICAL
    window.starguideConfigLoaded = true;
    window.starguideConfigLoading = false;

} // Close configuration guard