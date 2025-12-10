# Debug Guide for KhojAI Mobile App Crashes

## What We've Done:

1. **Zone Error Handler** - Catches ALL unhandled exceptions (async and sync)
2. **Flutter Error Handler** - Catches Flutter framework errors
3. **ErrorBoundary Widget** - Catches widget building errors and displays them
4. **Try-Catch Blocks** - Every critical operation is wrapped
5. **Detailed Logging** - Every major operation logs to console with context tags

## How to Run and Debug:

### Option 1: Simple Run (Direct)
```bash
cd /home/daiyaan2002/Desktop/Projects/KhojAI/mobile_application
flutter run -d linux
```

### Option 2: Run with Script
```bash
cd /home/daiyaan2002/Desktop/Projects/KhojAI
bash run_debug.sh
```

## What to Look For When It Crashes:

1. **Console Output Before Crash:**
   - Look for `[ChatScreen.itemBuilder]` logs
   - These show exactly which item is being rendered
   - If you see `Rendering item at index 0` but it crashes, that's the culprit

2. **Error Messages in Red:**
   - `[ZONE UNCAUGHT ERROR]` - Unhandled exception (should not happen now)
   - `[FLUTTER ERROR]` - Flutter framework error
   - `[ErrorBoundary]` - Widget building error (should show red error screen)
   - `[ChatScreen] ERROR in builder` - State building error

3. **Check for:**
   - `NullPointerException` / `null` errors
   - `RenderBox` errors
   - `State not mounted` errors
   - `Type mismatch` errors

## Expected Console Output for Zero Messages:

```
[ChatScreen] initState - Conversation ID: 1, Title: New Conversation
[ChatScreen] Loading messages for existing conversation (ID: 1)
[ChatCubit] Loading messages for conversation ID: 1
[DatabaseHelper] Querying messages for conversation: 1
[DatabaseHelper] Found 0 messages
[ChatCubit] Loaded 0 messages
```

When rendering (NO itemBuilder calls because messages.isEmpty):
```
[ChatScreen] No messages displayed - showing empty state
```

When messages are 0, the app should show:
```
"No messages yet. Start typing to begin the conversation!"
```

## If You Still Get a Crash:

1. **Look at the EXACT error message** (will be on red screen or in console)
2. **Copy the full error** and share it with context
3. **Check the stack trace** for the line number
4. The ErrorBoundary will show you exactly which widget is crashing

## Common Causes We've Fixed:

✅ Null messages list → Now uses `?? []`
✅ Null message content → Now uses `?? ''`
✅ Null message role → Now uses `?? 'assistant'`
✅ Zero messages → Now shows empty state
✅ Unhandled exceptions → Now caught by Zone handler
✅ Flutter errors → Now caught and logged
✅ Widget build errors → Now caught by ErrorBoundary

## If Crash Still Happens:

The error WILL show up either:
1. **Red error screen** on the app (ErrorBoundary caught it)
2. **Console output** with `[ZONE UNCAUGHT ERROR]` prefix
3. **Red text in console** from FlutterError handler

There is NO WAY for an error to escape now without being logged.

## Testing Steps:

1. Start the app
2. Click FAB to create new conversation
3. A new conversation should appear
4. Click it to open chat
5. See "No messages yet" message
6. Type a test message (or if API is off, it should still not crash)

If any crash happens, the entire error will be visible on screen or in console.
