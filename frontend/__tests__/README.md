# Frontend Tests

This directory contains tests for the KhojAI frontend application.

## Structure

- `/api` - Tests for API service functions
- `/components` - Tests for React components
- `/integration` - Integration tests
- `/utils` - Tests for utility functions

## Running Tests

To run all tests:

```bash
npm test
```

To run tests in watch mode:

```bash
npm test -- --watch
```

To run tests with coverage:

```bash
npm test -- --coverage
```

## Test Descriptions

### Document API Tests (`/api/document-api.test.ts`)

Tests for the DocumentAPI service functions:
- `getByUser` - Fetching documents for a user
- `upload` - Uploading a new document
- `delete` - Deleting a document

### Document Uploader Component Tests (`/components/document-uploader.test.tsx`)

Tests for the DocumentUploader component:
- Opening the upload modal via event
- Handling file selection
- Handling drag and drop operations
- Uploading documents
- Error handling
- Closing the modal

### Sidebar Component Tests (`/components/sidebar.test.tsx`)

Tests for the modified Sidebar component:
- Rendering conversations and documents sections
- Loading states
- Empty states
- Document selection events
- Upload button functionality

### Chat Interface Tests (`/components/chat-interface.test.tsx`)

Tests for the ChatInterface component with document functionality:
- Empty state when no chat is selected
- Rendering chat interface
- Drag and drop hints
- Drag event handling
- Document attachment
- Document removal

## Technologies Used

- Jest - Testing framework
- React Testing Library - For component testing
- Mock Service Worker (MSW) - For API mocking (if needed)