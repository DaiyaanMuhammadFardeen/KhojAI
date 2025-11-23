#Deployment Guide

## Environment Configuration

To properly deploy the application and avoid CORS issues, especially when accessing from mobile devices, you need to configure the environment variables correctly.

### Environment Files

The frontend application uses the following environment files:

1. `.env` - Default environment variables
2.`.env.local` - Local development environment variables (not committed to git)
3. `.env.production` - Production environment variables

### Required Environment Variables

```
NEXT_PUBLIC_API_URL=https://your-backend-subdomain.trycloudflare.com
```

### Configuration for Different Environments

#### Local Development with Cloudflare Tunnel
Create a `.env.local` file in the `frontend/` directory:
```
NEXT_PUBLIC_API_URL=https://your-backend-subdomain.trycloudflare.com
```

#### Production Deployment
Create a `.env.production` file in the `frontend/` directory with the actual backend URL:
```
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## Backend Deployment

Your backend(Spring Boot application) must be deployed and accessible from client devices. You have several options:

### Option 1: Cloudflare Tunnel (Recommended for Development)
1. Run your Spring Boot backend locally on port 5000:
   ```bash
   ./mvnw spring-boot:run
   ```
2.Install `cloudflared` if you haven't already
3. Create a tunnel for your backend:
   ```bash
   cloudflared tunnel --hostname your-backend-subdomain.trycloudflare.com --url http://localhost:5000
   ```
4. Update your frontend environment files with the backend tunnel URL### Option 2: Deploy to a Cloud Provider
1. Build your Spring Boot application:
   ```bash
   ./mvnw clean package
   ```
2. Deploy the JAR file to a cloud provider
3. Update your frontend environment files with the deployed backend URL

### Option 3: Use aFree Hosting Service
Services like Render, Railway, or Heroku allow you to deploy Spring Boot applications for free (with some limitations).

## Common Issues and Solutions

### CORS Issues on Mobile Devices

If you're experiencing CORS issues when accessing the application from mobile devices:

1. Make sure the `NEXT_PUBLIC_API_URL`environment variable is correctly set to your backend URL
2. Ensure your backend CORS configuration allows requests from your frontend domain
3. When using Cloudflare Tunnel, makesure both frontend and backend are accessible through the tunnel

### Network Connectivity Issues

If the application cannot connect to the backend:

1. Verify that the backend server is running
2. Check that the `NEXT_PUBLIC_API_URL` points to the correct backend address
3. Ensure that there are no firewall rules blocking the connection4. If deploying on different servers, make sure they can communicate with each other

### UserAPI.create() Fails on Other Machines

If `UserAPI.create()` works on your development machine but fails on other machines (including mobile devices), check:

1. **Backend Accessibility**: The most common cause is that your backendis only accessible from localhost. You must deploy or tunnel your backend to make it accessible from other devices.
2. **Environment Variables**: Ensure `NEXT_PUBLIC_API_URL` is correctly set in the appropriate `.env` file for your deployment environment
3. **Network Configuration**: Make sure there are no network restrictions preventing access tothe backend
4. **Cloudflare Tunnel**: If using Cloudflare Tunnel, ensure both frontend and backend are tunneled and accessible
5. **Firewall Settings**: Check that firewalls are not blocking the connection

To debug this issue:
- Check browser console logs for detailed error messages
- Verify the API URLbeing used matches your backend address
- Test direct access to your backend API endpoints

## Deployment Steps

1. Configure environment variables in the appropriate `.env` file
2. Deploy your backend server or set up a tunnel
3. Update the `NEXT_PUBLIC_API_URL` in your environment files to point to your backend4. Build the frontend application:
   ```bash
   cd frontend
   npm run build
   ```
5. Start the frontend application:
   ```bash
   npm start
   ```
6. Access the application through your browser or mobile device

## Quick Start with All Services

For development purposes, you canstart all services at once:

```bash
./run.sh
```

This script will start:
- Spring Boot backend on port 5000
- Next.js frontend on port 3000

To stop all services:

```bash
./stop.sh
```