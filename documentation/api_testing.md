#API Testing GuideThis document provides examples of how to test the KhojAI API endpoints using curl commands.

## Authentication

### User Login
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
   "username": "testuser",
    "password": "testpassword"
  }'
```

### User Registration
```bash
curl -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "newpassword"
  }'
```

## User Management

### Get User Details
```bash
curl -X GET http://localhost:5000/api/v1/users/{userId} \
  -H "Authorization: Bearer{token}"
```

### Update User
```bash
curl -X PUT http://localhost:5000/api/v1/users/{userId} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "username": "updateduser",
    "email": "updateduser@example.com"
  }'
```

### Delete User
```bash
curl -X DELETE http://localhost:5000/api/v1/users/{userId} \
  -H "Authorization: Bearer {token}"
```

## Conversation Management

### Create Conversation```bash
curl -X POST http://localhost:5000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "userId": "{userId}",
    "title": "New Conversation"
}'
```

### Get Conversation
```bash
curl -X GET http://localhost:5000/api/v1/conversations/{conversationId} \
  -H "Authorization: Bearer {token}"
```

### Get User Conversations
```bash
curl -X GET http://localhost:5000/api/v1/conversations/user/{userId} \
  -H "Authorization: Bearer {token}"
```

### Update Conversation Title
```bash
curl -X PUT http://localhost:5000/api/v1/conversations/{conversationId}/title \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "title": "Updated Title"
  }'
```

### Delete Conversation
```bash
curl -X DELETE http://localhost:5000/api/v1/conversations/{conversationId} \
  -H"Authorization: Bearer {token}"
```

##Message Management

### Create Message
```bash
curl -X POST http://localhost:5000/api/v1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "convId": "{conversationId}",
   "role": "USER",
    "content": "Hello, how can you help me?"
  }'
```

### Update Message
```bash
curl -X PUT http://localhost:5000/api/v1/messages/{messageId} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "content": "Updated message content"
  }'
```

### Delete Message
```bash
curl -X DELETE http://localhost:5000/api/v1/messages/{messageId} \
  -H "Authorization: Bearer{token}"
```

## AI Services

### Analyze Content
```bash
curl -X POST http://localhost:5000/api/v1/ai/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
"prompt": "Analyze this content for sentiment"
  }'
```

### Generate Response
```bash
curl -X POST http://localhost:5000/api/v1/ai/generate-response \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
-d '{
    "prompt": "Whatis the capital of France?"
  }'
```

## Document Management

### Upload Document
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/document.pdf" \
  -F "userId={userId}"
```

### Get User Documents
```bash
curl -X GET http://localhost:5000/api/documents/user/{userId} \
  -H "Authorization: Bearer {token}"
```

### Delete Document
```bash
curl -X DELETE http://localhost:5000/api/documents/{documentId} \
  -H "Authorization: Bearer {token}"
```

### Check Document Processing Status
```bash
curl -X GET http://localhost:5000/api/documents/{documentId}/processed \
  -H "Authorization: Bearer {token}"
```

##Error Handling

All API responses follow standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses will include a JSON body with an error message:
```json
{
  "timestamp": "2023-01-01T12:00:00.000+00:00",
  "status": 400,
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "path": "/api/v1/resource"
}
```#API Testing Documentation

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/login
- **Description**: Authenticate user and generate JWT token
- **Example Request**:
```http
POST /api/v1/auth/login HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpassword"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "testuser",
  "userId": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### POST /api/v1/users
- **Description**: Create a new user
- **Example Request**:
```http
POST /api/v1/users HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "newuser",
  "email": "newuser@example.com"
}
```

#### GET /api/v1/users/{id}
- **Description**: Retrieve user information by ID
- **Example Request**:
```http
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "newuser",
  "email": "newuser@example.com"
}
```

#### PUT/api/v1/users/{id}
- **Description**: Update user information
- **Example Request**:
```http
PUT /api/v1/users/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "username": "updateduser",
  "email": "updateduser@example.com",
  "password": "newpassword"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
"username": "updateduser",
  "email": "updateduser@example.com"
}
```

#### DELETE /api/v1/users/{id}
- **Description**: Delete a user
- **Example Request**:
```http
DELETE /api/v1/users/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Expected Response**:
```http
HTTP/1.1 204No Content
```

### Conversation Endpoints

#### POST /api/v1/conversations
- **Description**: Create a new conversation
- **Example Request**:
```http
POST /api/v1/conversations HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "title": "New Conversation"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "title": "New Conversation",
  "createdAt": "2023-01-01T00:00:00Z",
  "messages": []
}
```

#### GET /api/v1/conversations/{id}
- **Description**: Retrieve a conversation by ID
- **Example Request**:
```http
GET /api/v1/conversations/a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8 HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Expected Response**:
```http
HTTP/1.1 200 OKContent-Type: application/json

{
  "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "title": "New Conversation",
  "createdAt": "2023-01-01T00:00:00Z",
  "messages": [
{
      "id": "b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9",
      "role": "USER",
      "content": "Hello, AI!",
      "sentAt": "2023-01-01T00:01:00Z"
    }
  ]
}
```

#### GET /api/v1/conversations/user/{userId}
- **Description**: Retrieve all conversations for a user
- **Example Request**:
```http
GET /api/v1/conversations/user/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
{
    "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
    "title": "New Conversation",
    "createdAt": "2023-01-01T00:00:00Z",
    "messages": []
  }
]
```

#### PUT /api/v1/conversations/{id}/title
- **Description**: Update conversation title
- **Example Request**:
```http
PUT /api/v1/conversations/a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8/title HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "title": "Updated Conversation Title"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "title": "UpdatedConversation Title",
  "createdAt": "2023-01-01T00:00:00Z",
  "messages": []
}
```

#### DELETE /api/v1/conversations/{id}
- **Description**: Delete a conversation
- **Example Request**:
```http
DELETE /api/v1/conversations/a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8 HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Expected Response**:
```http
HTTP/1.1 204No Content
```

### MessageEndpoints

#### POST /api/v1/messages
- **Description**: Create a new message in a conversation
- **Example Request**:
```http
POST /api/v1/messages HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "convId": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "role": "USER",
  "content": "Hello, how are you?"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "title": "NewConversation",
  "createdAt": "2023-01-01T00:00:00Z",
  "messages": [
{
      "id": "c3d4e5f6-g7h8-9012-i3j4-k5l6m7n8o9p0",
      "role": "USER",
      "content": "Hello, how are you?",
      "sentAt": "2023-01-01T00:02:00Z"
    }
  ]
}
```

#### PUT /api/v1/messages/{id}
- **Description**: Update a message
- **Example Request**:
```http
PUT /api/v1/messages/c3d4e5f6-g7h8-9012-i3j4-k5l6m7n8o9p0 HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "content": "Hello, how are you today?"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "c3d4e5f6-g7h8-9012-i3j4-k5l6m7n8o9p0",
 "role": "USER",
  "content": "Hello, how are you today?",
  "sentAt": "2023-01-01T00:02:00Z"
}
```

#### DELETE /api/v1/messages/{id}
- **Description**: Delete a message- **Example Request**:
```http
DELETE /api/v1/messages/c3d4e5f6-g7h8-9012-i3j4-k5l6m7n8o9p0 HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Expected Response**:
```http
HTTP/1.1 204No Content
```

### AIEndpoints

#### POST /api/v1/ai/analyze
- **Description**: Analyze a prompt
- **Example Request**:
```http
POST /api/v1/ai/analyze HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "prompt": "What is the weather like today?"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "intent": "information_request",
  "entities": [],
  "keywords": [
    {
      "term": "weather",
      "weight": 0.8
    }
  ],
  "search_queries": [
    "current weather conditions"
  ]
}
```

#### POST /api/v1/ai/generate-response
- **Description**: Generate an AI response
- **Example Request**:
```http
POST /api/v1/ai/generate-response HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "prompt": "What isthe weather like today?"
}
```
- **Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "I don't have access to real-time weather data, but I suggest checking a weather service for current conditions."
}
```

## Testing Goals

### Authorization Testing
1. Validate JWT token generation upon successful login
2. Ensure unauthorized access to protected endpoints is denied
3. Verify token expiration and refresh mechanisms
4. Test role-based access control (if implemented)

### Validation Testing
1. Validate request payload structures and data types
2. Test required field validation
3. Verify proper error responses for invalid inputs
4. Check data sanitization and security measures

### Data Consistency Testing
1. Ensure data integrity across create, read, update, and delete operations
2. Verify foreign key relationships between Users, Conversations, and Messages
3. Test concurrent access scenarios
4. Validate data persistence and retrieval accuracy

### Update Flow Testing
1. Test complete lifecycle of entities (create → update → delete)
2. Verify cascading updatesand deletes where applicable
3. Ensure audit trails are maintained for updated records
4. Test rollback mechanisms for failed updates