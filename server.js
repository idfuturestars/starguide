
const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const cors = require('cors');
const path = require('path');

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Store connected users
let connectedUsers = new Map();

// Serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    const uptime = process.uptime();
    const memoryUsage = process.memoryUsage();
    
    res.json({ 
        status: 'ok', 
        message: 'IDFS StarGuide server is running',
        timestamp: new Date().toISOString(),
        connectedUsers: connectedUsers.size,
        uptime: Math.floor(uptime),
        services: {
            firebase: {
                admin: true,
                firestore: true
            },
            ai: {
                openai: !!process.env.OPENAI_API_KEY,
                claude: !!process.env.CLAUDE_API_KEY,
                gemini: !!process.env.GEMINI_API_KEY
            }
        },
        memory: {
            used: Math.round(memoryUsage.heapUsed / 1024 / 1024),
            total: Math.round(memoryUsage.heapTotal / 1024 / 1024)
        }
    });
});

// API endpoints for user data
app.get('/api/users/online', (req, res) => {
    res.json({ count: connectedUsers.size });
});

app.post('/api/progress', (req, res) => {
    try {
        const { userId, progress } = req.body;
        
        if (!userId) {
            return res.status(400).json({ error: 'User ID is required' });
        }
        
        if (!progress) {
            return res.status(400).json({ error: 'Progress data is required' });
        }
        
        // In a real app, save to database
        console.log('Progress update for user:', userId, 'with data:', JSON.stringify(progress));
        res.json({ success: true, message: 'Progress saved' });
    } catch (error) {
        console.error('Progress save error:', error);
        res.status(500).json({ error: 'Failed to save progress' });
    }
});

// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log('New client connected:', socket.id);
    
    socket.on('userJoined', (userData) => {
        console.log('User joined:', userData);
        connectedUsers.set(socket.id, userData);
        
        // Broadcast online user count
        io.emit('onlineUsers', connectedUsers.size);
    });
    
    socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
        connectedUsers.delete(socket.id);
        
        // Broadcast updated online user count
        io.emit('onlineUsers', connectedUsers.size);
    });
    
    socket.on('chatMessage', (data) => {
        console.log('Chat message:', data);
        // Broadcast message to all clients
        io.emit('chatMessage', data);
    });
    
    socket.on('battleInvite', (data) => {
        console.log('Battle invite:', data);
        // Send invite to specific user
        socket.to(data.targetUserId).emit('battleInvite', data);
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Handle 404s
app.use((req, res) => {
    res.status(404).sendFile(path.join(__dirname, 'index.html'));
});

// Start server
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0'; // Important: bind to 0.0.0.0 for Replit

server.listen(PORT, HOST, () => {
    console.log(`🚀 IDFS StarGuide server running on ${HOST}:${PORT}`);
    console.log(`📱 Access your app at: https://${process.env.REPL_SLUG || 'your-repl'}.${process.env.REPL_OWNER || 'username'}.repl.co`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('Received SIGTERM, shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});
