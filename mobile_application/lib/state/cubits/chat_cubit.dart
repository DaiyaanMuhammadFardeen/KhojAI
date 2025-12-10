import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/models/message.dart';
import '../../data/database/database_helper.dart';
import '../../services/api/api_service.dart';

// Chat States
abstract class ChatState {}

class ChatInitial extends ChatState {}

class ChatLoading extends ChatState {}

class ChatLoaded extends ChatState {
  final List<Message> messages;
  ChatLoaded(this.messages);
}

// Intermediate streaming states for real-time updates
class ChatIntentDetected extends ChatState {
  final List<Message> messages;
  final Map<String, dynamic> intentData;
  ChatIntentDetected(this.messages, this.intentData);
}

class ChatSearchStarted extends ChatState {
  final List<Message> messages;
  ChatSearchStarted(this.messages);
}

class ChatSearchProgress extends ChatState {
  final List<Message> messages;
  final Map<String, dynamic> progressData;
  ChatSearchProgress(this.messages, this.progressData);
}

class ChatSearchResultsReceived extends ChatState {
  final List<Message> messages;
  final List<Map<String, dynamic>> results;
  ChatSearchResultsReceived(this.messages, this.results);
}

class ChatSearchCompleted extends ChatState {
  final List<Message> messages;
  final Map<String, dynamic> completionData;
  ChatSearchCompleted(this.messages, this.completionData);
}

class ChatResponseStarted extends ChatState {
  final List<Message> messages;
  final String currentResponse;
  ChatResponseStarted(this.messages, this.currentResponse);
}

class ChatResponseStreaming extends ChatState {
  final List<Message> messages;
  final String currentResponse;
  final bool isStreaming;
  ChatResponseStreaming(this.messages, this.currentResponse, this.isStreaming);
}

class ChatError extends ChatState {
  final String message;
  ChatError(this.message);
}

// Chat Cubit
class ChatCubit extends Cubit<ChatState> {
  final DatabaseHelper _dbHelper = DatabaseHelper();
  final ApiService _apiService = ApiService();
  StreamSubscription<Map<String, dynamic>>? _streamSubscription;

  ChatCubit() : super(ChatInitial());

  Future<void> initializeNewConversation() async {
    // For newly created conversations, initialize with empty loaded state
    print('[ChatCubit] Initializing new conversation with empty messages');
    emit(ChatLoaded([]));
  }

  Future<void> loadMessages(int conversationId) async {
    emit(ChatLoading());
    try {
      print(
        '[ChatCubit] Loading messages for conversation ID: $conversationId',
      );
      final messages = await _dbHelper.getMessagesByConversation(
        conversationId,
      );
      print('[ChatCubit] Loaded ${messages.length} messages');
      emit(ChatLoaded(messages));
    } catch (e) {
      print('[ChatCubit] Error loading messages: $e');
      emit(ChatError('Failed to load messages: ${e.toString()}'));
    }
  }

  Future<void> sendMessage(String text, int conversationId) async {
    try {
      print('[ChatCubit] Sending message for conversation ID: $conversationId');

      if (conversationId <= 0) {
        emit(ChatError('Invalid conversation ID: $conversationId'));
        return;
      }

      // Save user message to database
      final userMessage = Message(
        conversationId: conversationId,
        role: 'user',
        content: text,
        timestamp: DateTime.now(),
      );

      await _dbHelper.insertMessage(userMessage);
      print('[ChatCubit] User message saved');

      // Load current messages
      final messages = await _dbHelper.getMessagesByConversation(
        conversationId,
      );

      // Emit loaded state with user message
      emit(ChatLoaded([...messages, userMessage]));

      // Start streaming response
      _streamSubscription?.cancel();
      _streamSubscription = _apiService
          .streamAIResponse(text, conversationId)
          .listen(
            (jsonData) {
              _processStreamEvent(jsonData, conversationId);
            },
            onError: (error) {
              print('[ChatCubit] Stream error: $error');
              emit(ChatError('Stream error: ${error.toString()}'));
            },
            onDone: () async {
              // Stream ended, save final message if there's accumulated response
              print('[ChatCubit] Stream done');
              if (state is ChatResponseStreaming) {
                final currentState = state as ChatResponseStreaming;
                if (currentState.currentResponse.isNotEmpty) {
                  final finalMessage = Message(
                    conversationId: conversationId,
                    role: 'assistant',
                    content: currentState.currentResponse,
                    timestamp: DateTime.now(),
                  );

                  await _dbHelper.insertMessage(finalMessage);

                  // Reload all messages
                  final updatedMessages = await _dbHelper
                      .getMessagesByConversation(conversationId);
                  emit(ChatLoaded(updatedMessages));
                }
              } else if (state is ChatResponseStarted) {
                final currentState = state as ChatResponseStarted;
                if (currentState.currentResponse.isNotEmpty) {
                  final finalMessage = Message(
                    conversationId: conversationId,
                    role: 'assistant',
                    content: currentState.currentResponse,
                    timestamp: DateTime.now(),
                  );

                  await _dbHelper.insertMessage(finalMessage);

                  // Reload all messages
                  final updatedMessages = await _dbHelper
                      .getMessagesByConversation(conversationId);
                  emit(ChatLoaded(updatedMessages));
                }
              }
            },
          );
    } catch (e) {
      print('[ChatCubit] Error sending message: $e');
      emit(ChatError('Failed to send message: ${e.toString()}'));
    }
  }

  void _processStreamEvent(Map<String, dynamic> jsonData, int conversationId) {
    try {
      print('[ChatCubit] Processing stream event: ${jsonData['type']}');
      print('[ChatCubit] Full event data: $jsonData');

      final type = jsonData['type'] as String?;
      final data = (jsonData['data'] ?? {}) as Map<String, dynamic>;

      List<Message> currentMessages = [];
      try {
        if (state is ChatLoaded) {
          currentMessages = (state as ChatLoaded).messages ?? [];
        } else if (state is ChatIntentDetected) {
          currentMessages = (state as ChatIntentDetected).messages ?? [];
        } else if (state is ChatSearchStarted) {
          currentMessages = (state as ChatSearchStarted).messages ?? [];
        } else if (state is ChatSearchProgress) {
          currentMessages = (state as ChatSearchProgress).messages ?? [];
        } else if (state is ChatSearchResultsReceived) {
          currentMessages = (state as ChatSearchResultsReceived).messages ?? [];
        } else if (state is ChatSearchCompleted) {
          currentMessages = (state as ChatSearchCompleted).messages ?? [];
        } else if (state is ChatResponseStarted) {
          currentMessages = (state as ChatResponseStarted).messages ?? [];
        } else if (state is ChatResponseStreaming) {
          currentMessages = (state as ChatResponseStreaming).messages ?? [];
        }
      } catch (e) {
        print('[ChatCubit] Error extracting messages from state: $e');
        currentMessages = [];
      }

      switch (type) {
        case 'intent_detected':
          try {
            print('[ChatCubit] Processing intent_detected with data: $data');
            emit(ChatIntentDetected(currentMessages, data));
          } catch (e) {
            print('[ChatCubit] Error processing intent_detected: $e');
          }
          break;

        case 'search_started':
          try {
            print('[ChatCubit] Processing search_started with data: $data');
            emit(ChatSearchStarted(currentMessages));
          } catch (e) {
            print('[ChatCubit] Error processing search_started: $e');
          }
          break;

        case 'search_progress':
          try {
            print('[ChatCubit] Processing search_progress with data: $data');
            emit(ChatSearchProgress(currentMessages, data));
          } catch (e) {
            print('[ChatCubit] Error processing search_progress: $e');
          }
          break;

        case 'search_result':
          try {
            print('[ChatCubit] Processing search_result with data: $data');
            final results = <Map<String, dynamic>>[];
            final resultsList = [data]; // Each event is a single result
            
            // Check if we already have search results in the state
            if (state is ChatSearchResultsReceived) {
              final existingResults = (state as ChatSearchResultsReceived).results;
              results.addAll(existingResults);
            }
            
            results.addAll(resultsList);
            emit(ChatSearchResultsReceived(currentMessages, results));
          } catch (e) {
            print('[ChatCubit] Error processing search_result: $e');
          }
          break;

        case 'search_completed':
          try {
            print('[ChatCubit] Processing search_completed with data: $data');
            emit(ChatSearchCompleted(currentMessages, data));
          } catch (e) {
            print('[ChatCubit] Error processing search_completed: $e');
          }
          break;

        case 'response_started':
          try {
            print('[ChatCubit] Processing response_started with data: $data');
            final startedText = 'Generating Response...';
            emit(ChatResponseStarted(currentMessages, startedText));
          } catch (e) {
            print('[ChatCubit] Error processing response_started: $e');
          }
          break;

        case 'response_token':
          try {
            final token = data['token'] as String? ?? '';
            print('[ChatCubit] Processing response_token: $token');
            String currentResponse = '';

            if (state is ChatResponseStreaming) {
              final streamState = state as ChatResponseStreaming;
              currentResponse = (streamState.currentResponse ?? '') + token;
            } else if (state is ChatResponseStarted) {
              final streamState = state as ChatResponseStarted;
              // Don't include "Generating Response..." in the final response
              if (streamState.currentResponse == 'Generating Response...') {
                currentResponse = token;
              } else {
                currentResponse = (streamState.currentResponse ?? '') + token;
              }
            } else {
              currentResponse = token;
            }

            emit(ChatResponseStreaming(currentMessages, currentResponse, true));
          } catch (e) {
            print('[ChatCubit] Error processing response_token: $e');
          }
          break;

        case 'stream_complete':
          try {
            print('[ChatCubit] Processing stream_complete');
            // Mark streaming as complete but keep the response
            if (state is ChatResponseStreaming) {
              final streamState = state as ChatResponseStreaming;
              emit(
                ChatResponseStreaming(
                  streamState.messages,
                  streamState.currentResponse ?? '',
                  false,
                ),
              );
            }
          } catch (e) {
            print('[ChatCubit] Error processing stream_complete: $e');
          }
          break;

        default:
          print('[ChatCubit] Unknown event type: $type');
          // Unknown event type, ignore
          break;
      }
    } catch (e) {
      print('[ChatCubit] FATAL ERROR in _processStreamEvent: $e');
      emit(ChatError('Error processing stream event: ${e.toString()}'));
    }
  }

  void cancelStream() {
    _streamSubscription?.cancel();
    _streamSubscription = null;
  }

  @override
  Future<void> close() {
    _streamSubscription?.cancel();
    return super.close();
  }
}