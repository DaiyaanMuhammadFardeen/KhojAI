# Quick Start Guide - Testing the Crash Fixes

## Starting the App

### On Linux Desktop
```bash
cd mobile_application
flutter run -d linux
```

### On Windows Desktop
```bash
cd mobile_application
flutter run -d windows
```

### On macOS Desktop
```bash
cd mobile_application
flutter run -d macos
```

## Reading Debug Logs

The app now prints detailed logs to the console showing exactly what's happening at each step.

### Start the app and watch the console output:
```
[main] Starting KhojAI app...
[main] Initializing sqflite FFI...
[main] sqlfiteFfiInit FFI initialized
[main] Initializing settings service...
[main] Settings service initialized
[main] Initialization complete, running app
```

### When you click "Start New Chat" button:
```
[HomeScreen] FAB pressed - Creating new conversation...
[ConversationCubit] Creating conversation: New Conversation
[DatabaseHelper] Inserting conversation: New Conversation
[DatabaseHelper] Conversation inserted with ID: 1
[ConversationCubit] Loading conversations...
[DatabaseHelper] Querying all conversations...
[DatabaseHelper] Found 1 conversations
[ConversationCubit] Loaded 1 conversations
  - ID: 1, Title: New Conversation
[HomeScreen] FAB: New conversation ID: 1, Title: New Conversation
[ChatScreen] initState - Conversation ID: 1, Title: New Conversation
[ChatCubit] Initializing new conversation with empty messages
```

### When you click on a conversation in the list:
```
[HomeScreen] Tapped conversation: ID=1, Title=New Conversation
[ChatScreen] initState - Conversation ID: 1, Title: New Conversation
[ChatCubit] Loading messages for conversation ID: 1
[DatabaseHelper] Querying messages for conversation: 1
[DatabaseHelper] Found 0 messages
[ChatCubit] Loaded 0 messages
```

## What to Look For

### ✅ Success Indicators
- Logs show IDs incrementing (1, 2, 3, etc.)
- "ID: X" appears in logs after creation
- App navigates to ChatScreen without hanging
- No "ERROR" messages in console
- Conversations appear in sidebar with titles

### ❌ Failure Indicators
- "Invalid ID: null" or "Invalid ID: 0" in logs
- Database errors like "no such table"
- Async gaps or missing await messages
- App hangs instead of navigating
- No logs appearing at all

## Test Scenarios

### Scenario 1: Create Multiple Conversations
1. Click FAB
2. Wait for navigation to ChatScreen
3. Click "+ New Conversation" in sidebar
4. Create another conversation
5. Check logs - IDs should be 1, 2, etc.
6. Both conversations should appear in sidebar when you go back

### Scenario 2: Navigate Between Conversations
1. Create 2 conversations
2. Open sidebar on second conversation
3. Click first conversation in list
4. App should switch without crash
5. Logs should show proper ID switching

### Scenario 3: Send a Message
1. Create conversation
2. Type a message
3. Click send button
4. Watch logs:
   - `[ChatInput] Sending message:`
   - `[ChatCubit] Sending message for conversation ID:`
   - `[DatabaseHelper] Inserting message for conversation:`
5. Message should appear in chat

### Scenario 4: Test Error Recovery
1. Create conversation
2. Type message
3. Stop API server
4. Try to send message
5. Should see error message in app
6. App should NOT crash
7. Logs should show error details

## Common Issues and Solutions

### Issue: No Logs Appearing
**Possible Cause:** 
- App crashed during initialization
- Check if ErrorApp is showing

**Solution:**
- Check if there's a red error screen
- Look for error message on screen
- Restart app with `flutter run -d linux`

### Issue: Conversation Created But Not in List
**Possible Cause:**
- Conversation has invalid ID (null or 0)
- State not updating properly

**Solution:**
- Check logs for "Conversation created with ID: X"
- Verify ID is > 0
- Check if `loadConversations()` was called after creation

### Issue: App Crashes When Clicking Conversation
**Possible Cause:**
- Conversation ID is null or 0
- Message loading failed

**Solution:**
- Check logs: "Tapped conversation: ID=..."
- If ID=null, check conversation creation logs
- Look for database errors in logs

### Issue: Weird State After Multiple Actions
**Solution:**
- Close app completely
- Delete app data: `flutter clean`
- Rebuild: `flutter pub get && flutter build linux`
- Start fresh

## Interpreting Error Messages

### Database Errors
```
[DatabaseHelper] Error querying conversations: database closed
```
- Database connection was lost
- Try restarting app

### State Mismatch
```
[HomeScreen] ERROR: Cubit state is not ConversationsLoaded
```
- State transition issue
- Check if `loadConversations()` was called

### Invalid Data
```
[ChatScreen] ERROR: Selected conversation has invalid ID: null
```
- Conversation object is malformed
- Check creation logs to find where ID went missing

## Enabling Console Output on Windows

If you're on Windows and logs aren't showing:

1. Open Windows Terminal
2. Run: `flutter run -d windows`
3. Logs should appear in the terminal window

## Filtering Logs

You can filter logs to see only specific components:

```bash
# Only show database logs
flutter run | grep "\[DatabaseHelper\]"

# Only show errors
flutter run | grep "ERROR"

# Show conversation-related operations
flutter run | grep -E "\[.*Conversation"
```

## Performance Notes

- First app launch will initialize database (takes a few seconds)
- Creating conversation adds ~200ms delay (intentional for state sync)
- Switching conversations should be instant
- Message loading depends on number of messages

## Next Steps for Production

1. Suppress print statements using `kDebugMode`
2. Implement crash reporting service
3. Add analytics logging
4. Set up error tracking
5. Test on actual devices

## Getting Help

If crashes still occur:

1. **Note the exact steps** to reproduce
2. **Screenshot the error** if visible
3. **Copy the full console log** output
4. **Check for ERROR messages** with red text
5. **Report with logs and reproduction steps**

The comprehensive logging system should provide all the information needed to diagnose any remaining issues.
