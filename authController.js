
/**
 * Authentication Controller
 */

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { User } = require('../models/User');
const logger = require('../utils/logger');

class AuthController {
    async demoLogin(req, res) {
        try {
            const { name } = req.body;
            
            // Find or create demo user
            let user = await User.findOne({ where: { username: name } });
            
            if (!user) {
                user = await User.create({
                    username: name,
                    email: `${name}@demo.local`,
                    is_demo: true,
                    xp: 0,
                    level: 1
                });
            }

            const token = jwt.sign(
                { userId: user.id, username: user.username },
                process.env.JWT_SECRET || 'demo-secret',
                { expiresIn: '24h' }
            );

            res.json({
                success: true,
                user: {
                    id: user.id,
                    username: user.username,
                    email: user.email,
                    xp: user.xp,
                    level: user.level
                },
                token
            });
        } catch (error) {
            logger.error('Demo login error:', error);
            res.status(500).json({ success: false, error: 'Login failed' });
        }
    }

    async register(req, res) {
        try {
            const { username, email, password } = req.body;
            
            // Check if user exists
            const existingUser = await User.findOne({
                where: { email }
            });
            
            if (existingUser) {
                return res.status(400).json({
                    success: false,
                    error: 'User already exists'
                });
            }

            // Hash password
            const hashedPassword = await bcrypt.hash(password, 10);
            
            // Create user
            const user = await User.create({
                username,
                email,
                password: hashedPassword,
                xp: 0,
                level: 1
            });

            const token = jwt.sign(
                { userId: user.id, username: user.username },
                process.env.JWT_SECRET || 'demo-secret',
                { expiresIn: '24h' }
            );

            res.status(201).json({
                success: true,
                user: {
                    id: user.id,
                    username: user.username,
                    email: user.email,
                    xp: user.xp,
                    level: user.level
                },
                token
            });
        } catch (error) {
            logger.error('Registration error:', error);
            res.status(500).json({ success: false, error: 'Registration failed' });
        }
    }

    async login(req, res) {
        try {
            const { email, password } = req.body;
            
            const user = await User.findOne({ where: { email } });
            
            if (!user || !await bcrypt.compare(password, user.password)) {
                return res.status(401).json({
                    success: false,
                    error: 'Invalid credentials'
                });
            }

            const token = jwt.sign(
                { userId: user.id, username: user.username },
                process.env.JWT_SECRET || 'demo-secret',
                { expiresIn: '24h' }
            );

            res.json({
                success: true,
                user: {
                    id: user.id,
                    username: user.username,
                    email: user.email,
                    xp: user.xp,
                    level: user.level
                },
                token
            });
        } catch (error) {
            logger.error('Login error:', error);
            res.status(500).json({ success: false, error: 'Login failed' });
        }
    }

    async logout(req, res) {
        res.json({ success: true, message: 'Logged out successfully' });
    }

    async getProfile(req, res) {
        try {
            const user = await User.findByPk(req.userId);
            
            if (!user) {
                return res.status(404).json({
                    success: false,
                    error: 'User not found'
                });
            }

            res.json({
                success: true,
                user: {
                    id: user.id,
                    username: user.username,
                    email: user.email,
                    xp: user.xp,
                    level: user.level,
                    created_at: user.created_at
                }
            });
        } catch (error) {
            logger.error('Get profile error:', error);
            res.status(500).json({ success: false, error: 'Failed to get profile' });
        }
    }
}

module.exports = new AuthController();
