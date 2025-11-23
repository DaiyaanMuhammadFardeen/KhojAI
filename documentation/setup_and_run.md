# Setup and Run Guide

## Prerequisites

Before you begin, ensure you have the following installed:
- Java 25 or higher
- Maven 3.6+
- Node.js 18+ and npm
- PostgreSQL 12+

## Backend Setup

### Database Configuration

1. Install PostgreSQL if not already installed
2. Create a database named `khojai_db`
3. Create a user with appropriate permissions:
   ```sql
   CREATE USER khojai_user WITH PASSWORD 'khojai_pass_1620#';
   GRANT ALL PRIVILEGES ON DATABASE khojai_db TO khojai_user;
   ```

### Environment Configuration

The backend configuration is located in `src/main/resources/application.properties`. Key configurations include:

```properties
# Server Configuration
server.port=5000

# Database Configuration
spring.datasource.url=jdbc:postgresql://localhost:5432/khojai_db
spring.datasource.username=khojai_user
spring.datasource.password=khojai_pass_1620#

# JWT Configuration
jwt.secret=mySecretKey
jwt.expiration=86400
```

### Building the Backend

To build the backend application:

```bash
./mvnw clean package
```

To skip tests during build:

```bash
./mvnw clean package -DskipTests
```

### Running the Backend

To run the backend application:

```bash
./mvnw spring-boot:run
```

Or after building:

```bash
java -jar target/KhojAI-0.0.1-SNAPSHOT.jar
```

## Frontend Setup

### Environment Configuration

Create a `.env.local` file in the `frontend/` directory with the following content:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

For production deployment, create a `.env.production` file:

```env
NEXT_PUBLIC_API_URL=https://your-production-domain.com
```

### Installing Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

### Running the Frontend

To run the frontend in development mode:

```bash
npm run dev
```

To build for production:

```bash
npm run build
```

To start the production build:

```bash
npm start
```

## All-in-One Setup Script

For development purposes, you can use the provided scripts to start all services:

```bash
# Start all services
./run.sh

# Stop all services
./stop.sh
```

## Service Ports

The application uses the following ports:
- Frontend: 3000
- Backend: 5000 (changed from 8080 to avoid conflicts)

## Troubleshooting

### Database Connection Issues

1. Verify PostgreSQL is running
2. Check database credentials in `application.properties`
3. Ensure the database and user exist

### Port Conflicts

If you encounter port conflicts:
1. Check which services are running on the required ports
2. Stop conflicting services or change port configurations
3. The backend now runs on port 5000 to avoid conflicts with other services

### CORS Issues

1. Ensure `NEXT_PUBLIC_API_URL` is correctly set in your environment files
2. Verify the backend CORS configuration allows requests from your frontend domain