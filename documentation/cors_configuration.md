# CORS Configuration Guide

## Overview
This document explains how CORS is configured in the KhojAI application to ensure proper communication between the frontend and backend when deployed on Cloudflare.

## Frontend Configuration

### next.config.mjs
The `allowedDevOrigins` array includes all expected domains:
```javascript
allowedDevOrigins: [
  'nationally-award-ver-syndication.trycloudflare.com',
  'holding-exam-brokers-cms.trycloudflare.com',
  'localhost'
]
```

### Environment Variables
Different environment files are used for different deployment scenarios:

1. `.env.development` - Local development
2. `.env.production` - Production deployment
3. `.env` - Default fallback

## Backend Configuration

### CorsConfig.java
The backend allows requests from specific patterns:
```java
config.setAllowedOriginPatterns(List.of(
    "http://localhost:*",
    "https://localhost:*",
    "https://*trycloudflare.com",
    "http://*trycloudflare.com"
));
```

## Deployment Checklist

Before demo day, ensure:

1. [ ] Frontend domain is added to `allowedDevOrigins` in `next.config.mjs`
2. [ ] Backend API URL is correctly set in `.env.production`
3. [ ] Cloudflare tunnel is properly configured
4. [ ] Both frontend and backend are accessible via their respective URLs

## Troubleshooting

### Common CORS Issues

1. **Blocked cross-origin request**: Ensure the requesting domain is in `allowedDevOrigins`
2. **Network errors**: Check that both frontend and backend services are running
3. **Credential issues**: Verify `withCredentials: true` is set in API calls

### Testing CORS

Use the test endpoint: `GET /api/v1/auth/test`

This endpoint will return a simple JSON response to verify CORS is working.