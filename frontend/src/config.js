// src/config.js
// const API_URL = "localhost";
// const API_PORT = "8000"
// const RECOMMENDATION_API_PORT = "8080"
// const RECOMMENDATION_API_URL = "localhost"
// export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `http://${API_URL}:${API_PORT}`;
// export const RECOMMENDATION_API_BASE_URL = process.env.REACT_APP_RECOMMENDATION_API_BASE_URL || `http://${RECOMMENDATION_API_URL}:${RECOMMENDATION_API_PORT}`;

// src/config.js

// Detect if running in Docker (production build)
const isDocker = process.env.NODE_ENV === 'production';

// Base URLs
export const API_BASE_URL = isDocker
	? '/api' // Docker/Nginx proxy
	: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api'; // local dev

export const RECOMMENDATION_API_BASE_URL = isDocker
	? '/api/recommendation'
	: process.env.REACT_APP_RECOMMENDATION_API_BASE_URL ||
	  'http://localhost:8080/api';
