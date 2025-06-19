
/**
 * Database configuration for IDFS StarGuide
 */

const path = require('path');

const config = {
    development: {
        dialect: 'sqlite',
        storage: path.join(__dirname, '../../../data/starguide.db'),
        logging: console.log,
        define: {
            timestamps: true,
            underscored: true
        }
    },
    production: {
        dialect: 'sqlite',
        storage: path.join(__dirname, '../../../data/starguide.db'),
        logging: false,
        define: {
            timestamps: true,
            underscored: true
        }
    }
};

module.exports = config;
