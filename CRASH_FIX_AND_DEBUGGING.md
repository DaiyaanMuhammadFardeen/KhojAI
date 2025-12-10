# Crash Fix and Comprehensive Debugging Guide

## Overview
This document describes the comprehensive fixes applied to prevent crashes when opening the chat window and navigating between conversations.

## Issues Fixed

### 1. **Crash on "Start New Conversation" Button Click**
**Problem:** The application crashed when clicking the floating action button or "Start New Chat" button.

**Root Cause:** 
- The `createConversation()` method was not awaiting the database save completion
- The newly created conversation object didn't have a valid ID assigned
- Navigation was happening with a conversation that had ID = null
- ChatCubit tried to load messages with conversationId = 0 or null

**Solution Implemented:**
1. Modified `createConversation()` in `ConversationCubit` to:
   - Wait for the database insert to complete
   - Immediately call `loadConversations()` to refresh the list
   - This ensures the newly created conversation is retrieved with its proper database ID
2. Added validation in all navigation handlers to check if `conversation.id != null && conversation.id! > 0`
3. Added fallback UI error messages for users
4. Added comprehensive logging at every step

### 2. **Crash on Conversation Selection**
**Problem:** Clicking on an existing conversation from the list caused a crash.

**Root Cause:**
- Invalid conversation IDs in the sidebar or list
- Missing null checks before navigation
- Improper state management when transitioning between conversations

**Solution Implemented:**
1. Added ID validation guards in all `onTap` handlers:
   ```dart
   if (conversation.id != null && conversation.id! > 0) {
     // Safe to navigate
   }
   ```
2. Added error UI feedback when invalid conversation is selected
3. Enhanced logging to track conversation selection

### 3. **Widget Initialization Issues**
**Problem:** ChatScreen would crash during initialization if passed invalid conversation data.

**Root Cause:**
- No error handling in `initState()`
- Concurrent async operations without proper synchronization
- State mismanagement with BLoC

**Solution Implemented:**
1. Wrapped ChatScreen's `initState()` in try-catch with detailed logging
2. Added different initialization paths:
   - For existing conversations (ID > 0): `loadMessages(conversationId)`
   - For new conversations (ID = null): `initializeNewConversation()`
3. Added proper mounted checks before UI updates

## Debug Logging System

### Logging Prefix Convention
Each module logs with a prefix for easy filtering:
- `[main]` - Application initialization
- `[DatabaseHelper]` - Database operations
- `[ConversationCubit]` - Conversation state management
- `[ChatCubit]` - Chat state and message management
- `[ChatScreen]` - Chat UI screen
- `[HomeScreen]` - Home/list screen
- `[Sidebar]` - Sidebar navigation
- `[ChatInput]` - Message input widget

### How to Read Logs

When the app crashes or behaves unexpectedly, check the console/terminal for logs:

```
[main] Starting KhojAI app...
[main] Initializing sqflite FFI...
[main] sqflite FFI initialized
[main] Initializing settings service...
[main] Settings service initialized
[main] Initialization complete, running app
[DatabaseHelper] Initializing database...
[DatabaseHelper] Database path: /path/to/khoj_ai.db
[DatabaseHelper] Creating database tables...
[DatabaseHelper] Database tables created successfully
[ConversationCubit] Loading conversations...
[ConversationCubit] Loaded 2 conversations
  - ID: 1, Title: First Conversation
  - ID: 2, Title: Second Conversation
```

### Critical Error Patterns

#### Pattern 1: Database Issues
```
[DatabaseHelper] Error querying conversations: database closed
[ConversationCubit] Error loading conversations: database closed
```
**Action:** Restart the app. Database might be corrupted.

#### Pattern 2: Invalid Conversation ID
```
[HomeScreen] ERROR: New conversation has invalid ID: null
[HomeScreen] ERROR: Conversations list is empty or state is not ConversationsLoaded
```
**Action:** Check that `createConversation()` is awaiting database completion.

#### Pattern 3: Navigation Issues
```
[ChatScreen] initState - Conversation ID: null, Title: New Conversation
[ChatScreen] ERROR in initState: Invalid conversation with ID: null
```
**Action:** Check the navigation logic - valid conversations should have ID > 0.

#### Pattern 4: Message Loading Failure
```
[ChatCubit] Error loading messages for conversation ID: 5: no such table: messages
```
**Action:** Database schema issue. Delete app data and reinstall.

## Testing Checklist

### Test 1: Create New Conversation from Home Screen
```
Steps:
1. Start app
2. See "No conversations yet" screen
3. Click "Start New Chat" button
Expected: Navigates to ChatScreen without crash
Verify in logs:
  [HomeScreen] FAB pressed - Creating new conversation...
  [ConversationCubit] Creating conversation: New Conversation
  [ConversationCubit] Conversation created with ID: 1
  [ConversationCubit] Loading conversations...
  [HomeScreen] New conversation ID: 1, Title: New Conversation
  [ChatScreen] initState - Conversation ID: 1
  [ChatScreen] Initializing new conversation with empty messages
```

### Test 2: Create New Conversation from FAB (multiple times)
```
Steps:
1. Click FAB multiple times rapidly
Expected: Each creates a conversation without crashes
Verify: IDs increment (1, 2, 3, etc.)
```

### Test 3: Navigate to Existing Conversation
```
Steps:
1. Create first conversation (should show in list)
2. Navigate back to home
3. Click on conversation in list
Expected: Navigates to ChatScreen with existing conversation
Verify in logs:
  [HomeScreen] Tapped conversation: ID=1, Title=...
  [ChatScreen] initState - Conversation ID: 1
  [ChatCubit] Loading messages for conversation ID: 1
  [ChatCubit] Loaded 0 messages (if new)
```

### Test 4: Navigation from Sidebar
```
Steps:
1. On ChatScreen, open sidebar
2. Click "New Conversation" button
Expected: Creates and navigates without crash
Verify logs show same patterns as FAB tests
```

### Test 5: Navigation Between Existing Conversations
```
Steps:
1. Have 2+ conversations
2. On ChatScreen, open sidebar
3. Click another conversation from list
Expected: Navigates without crash
Verify logs show proper conversation ID switching
```

### Test 6: Send Message
```
Steps:
1. Open conversation
2. Type message
3. Click send
Expected: Message appears, no crash
Verify logs:
  [ChatInput] Sending message: ...
  [ChatCubit] Sending message for conversation ID: 1
  [ChatCubit] User message saved
  [DatabaseHelper] Inserting message for conversation: 1
```

### Test 7: Error Recovery
```
Steps:
1. Disconnect from API server
2. Try to send message
3. Observe error message
Expected: Error shown in SnackBar, app doesn't crash
```

## Key Code Changes Summary

### 1. ConversationCubit Changes
- `createConversation()` now awaits database save and calls `loadConversations()`
- Added print logging at all key points
- Added error handling and emission of ConversationError state

### 2. ChatCubit Changes
- Added logging for all state transitions
- Improved `sendMessage()` with conversation ID validation
- Added error handling in stream listeners

### 3. UI Changes (ChatScreen, HomeScreen, Sidebar)
- Added try-catch blocks in all async handlers
- Added validation before navigation
- Added user-visible error messages via SnackBar
- Added mounted checks for all context operations

### 4. DatabaseHelper Changes
- Added comprehensive logging for all database operations
- Added try-catch in all methods
- Logs include operation type, parameters, and results

## Performance Notes

- Conversation creation is slightly slower due to the extra `loadConversations()` call
- This is acceptable because it ensures data consistency and provides a better user experience
- The 200ms delay between save and navigation ensures the state has updated

## Future Improvements

1. Implement a proper error recovery system with retry logic
2. Add user preference for error display (show in UI vs. console only)
3. Implement analytics logging for crash tracking
4. Add automated tests for all crash scenarios
5. Consider using a logging library like `logger` package for better control

## Disabling Debug Logs (Production)

If you want to disable all debug logs for production:

1. Replace all `print()` calls with a logging function
2. Example:
```dart
void debugLog(String message) {
  if (kDebugMode) {
    print(message);
  }
}
```

3. Import `dart:developer` and use `kDebugMode`
