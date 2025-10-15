const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_API_BASE_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:5005';

// Enable CORS
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'build')));

// API proxy middleware
app.use('/api', createProxyMiddleware({
    target: BACKEND_API_BASE_URL,
    changeOrigin: true,
    pathRewrite: {
        '^/api': '', // Remove /api prefix when forwarding to backend
    },
    onError: (err, req, res) => {
        console.error('Proxy error:', err);
        res.status(500).json({ error: 'Backend service unavailable' });
    }
}));

// Catch-all handler: send back React's index.html file for SPA routing
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Proxying API calls to: ${BACKEND_API_BASE_URL}`);
});
