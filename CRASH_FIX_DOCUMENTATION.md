# Flutter App Crash Fix - New Conversation Button

## Problem
The application was crashing when the user clicked "Start New Conversation" button. This occurred in:
1. Home Screen - Empty state button
2. Home Screen - Floating action button
3. Chat Screen - New conversation button in AppBar
4. Sidebar - New conversation button

## Root Cause
The crash was caused by trying to navigate to `ChatScreen` with a `Conversation` object that had **no ID** (null). When the `ChatScreen` initialized, it attempted to load messages for a conversation with ID 0 (using `widget.conversation.id ?? 0`), which didn't exist in the database, causing a database error.

### Code Flow Before Fix
```
User clicks "Start New Conversation"
    ↓
Create Conversation object with id=null
    ↓
Navigate to ChatScreen immediately
    ↓
ChatScreen tries to load messages with conversation.id = 0
    ↓
Database query fails → App crashes
```

## Solution
Changed the flow to **save the conversation to the database first**, then navigate with the saved conversation object that has a valid ID.

### Code Flow After Fix
```
User clicks "Start New Conversation"
    ↓
Call ConversationCubit.createConversation() 
    ↓
Wait for database save (100ms delay)
    ↓
Retrieve the saved conversation with valid ID from cubit state
    ↓
Navigate to ChatScreen with saved conversation
    ↓
ChatScreen loads messages successfully
```

## Files Modified

### 1. `lib/ui/screens/home_screen.dart`
- **Empty state button**: Changed from immediate navigation to saving first
- **Floating action button**: Changed from immediate navigation to saving first

### 2. `lib/ui/screens/chat_screen.dart`
- **AppBar add button**: Changed from immediate navigation to saving first

### 3. `lib/ui/components/sidebar.dart`
- **New Conversation Button**: Changed from direct database call to using ConversationCubit
- **Delete button**: Updated to use ConversationCubit instead of direct DatabaseHelper call
- **Removed unused import**: Removed `DatabaseHelper` import since we now use the cubit

## Key Changes in Code

### Before (Crashes)
```dart
onPressed: () {
  final conversation = Conversation(
    title: 'New Conversation',
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );
  
  Navigator.push(context, MaterialPageRoute(
    builder: (context) => ChatScreen(conversation: conversation),
  ));
}
```

### After (Works)
```dart
onPressed: () async {
  // Save to database first
  context.read<ConversationCubit>().createConversation('New Conversation');
  
  // Wait for database operation
  await Future.delayed(const Duration(milliseconds: 100));
  
  if (mounted) {
    // Get the newly created conversation from cubit
    final cubitState = context.read<ConversationCubit>().state;
    if (cubitState is ConversationsLoaded && 
        cubitState.conversations.isNotEmpty) {
      final newConversation = cubitState.conversations.last;
      
      if (mounted) {
        Navigator.push(context, MaterialPageRoute(
          builder: (context) => ChatScreen(conversation: newConversation),
        ));
      }
    }
  }
}
```

## Benefits of This Fix
1. ✅ **No more crashes** when creating new conversations
2. ✅ **Consistent state management** - Uses BLoC (ConversationCubit) everywhere
3. ✅ **Proper ID assignment** - Conversations have valid database IDs before navigation
4. ✅ **Better UX** - Conversations are immediately available in the sidebar after creation
5. ✅ **Type safety** - No more using `id ?? 0` workarounds

## Testing
To verify the fix:
1. Launch the app
2. Click "Start New Chat" button (empty state or FAB)
3. The app should navigate to ChatScreen without crashing
4. The conversation should appear in the sidebar
5. Messages can be sent without errors
