#!/usr/bin/env node

/**
 * Reset KDS test data
 * Usage: node reset-kds-data.js
 */

const http = require('http');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/api/v1/kds/reset',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
};

console.log('🔄 Resetting KDS test data...\n');

const req = http.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    try {
      const response = JSON.parse(data);
      console.log('✅ Success!');
      console.log('Response:', response);
      console.log('\n📱 Refresh your browser to see fresh test data.');
      process.exit(0);
    } catch (e) {
      console.error('❌ Error parsing response:', e.message);
      process.exit(1);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Error resetting data:', error.message);
  console.error('Make sure the backend is running on http://localhost:8000');
  process.exit(1);
});

req.end();
