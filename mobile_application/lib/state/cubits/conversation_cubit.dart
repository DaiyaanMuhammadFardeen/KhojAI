import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/models/conversation.dart';
import '../../data/database/database_helper.dart';

abstract class ConversationState {}

class ConversationInitial extends ConversationState {}

class ConversationsLoading extends ConversationState {}

class ConversationsLoaded extends ConversationState {
  final List<Conversation> conversations;

  ConversationsLoaded(this.conversations);
}

class ConversationCreated extends ConversationState {
  final Conversation conversation;

  ConversationCreated(this.conversation);
}

class ConversationUpdated extends ConversationState {
  final Conversation conversation;

  ConversationUpdated(this.conversation);
}

class ConversationError extends ConversationState {
  final String message;

  ConversationError(this.message);
}

class ConversationCubit extends Cubit<ConversationState> {
  final DatabaseHelper _dbHelper = DatabaseHelper();

  ConversationCubit() : super(ConversationInitial());

  Future<void> loadConversations() async {
    emit(ConversationsLoading());
    try {
      print('[ConversationCubit] Loading conversations...');
      final conversations = await _dbHelper.getAllConversations();
      print('[ConversationCubit] Loaded ${conversations.length} conversations');
      conversations.forEach((c) => print('  - ID: ${c.id}, Title: ${c.title}'));
      emit(ConversationsLoaded(conversations));
    } catch (e) {
      print('[ConversationCubit] Error loading conversations: $e');
      emit(ConversationError('Failed to load conversations: ${e.toString()}'));
    }
  }

  Future<void> createConversation(String title) async {
    try {
      print('[ConversationCubit] Creating conversation: $title');
      final now = DateTime.now();
      final conversation = Conversation(
        title: title,
        createdAt: now,
        updatedAt: now,
      );

      final newId = await _dbHelper.insertConversation(conversation);
      print('[ConversationCubit] Conversation created with ID: $newId');
      
      // Fetch the newly created conversation with its ID
      final updatedConversation = Conversation(
        id: newId,
        title: conversation.title,
        createdAt: conversation.createdAt,
        updatedAt: conversation.updatedAt,
      );
      
      emit(ConversationCreated(updatedConversation));
      
      // Load all conversations to update the list
      await loadConversations();
    } catch (e) {
      print('[ConversationCubit] Error creating conversation: $e');
      emit(ConversationError('Failed to create conversation: ${e.toString()}'));
    }
  }

  Future<void> updateConversation(Conversation conversation) async {
    try {
      final updatedConversation = Conversation(
        id: conversation.id,
        title: conversation.title,
        createdAt: conversation.createdAt,
        updatedAt: DateTime.now(),
      );

      await _dbHelper.updateConversation(updatedConversation);
      emit(ConversationUpdated(updatedConversation));
      loadConversations(); // Reload the list
    } catch (e) {
      emit(ConversationError(e.toString()));
    }
  }

  Future<void> deleteConversation(int id) async {
    try {
      await _dbHelper.deleteConversation(id);
      loadConversations(); // Reload the list
    } catch (e) {
      emit(ConversationError(e.toString()));
    }
  }
}