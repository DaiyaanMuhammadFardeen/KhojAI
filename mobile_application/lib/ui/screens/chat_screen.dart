import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../widgets/chat_message.dart';
import '../widgets/chat_input.dart';
import '../widgets/error_boundary.dart';
import '../../state/cubits/chat_cubit.dart';
import '../../data/models/conversation.dart';
import '../../data/models/message.dart';
import '../components/sidebar.dart';
import '../../state/cubits/conversation_cubit.dart';

class ChatScreen extends StatefulWidget {
  final Conversation conversation;

  const ChatScreen({super.key, required this.conversation});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    print(
      '[ChatScreen] initState - Conversation ID: ${widget.conversation.id}, Title: ${widget.conversation.title}',
    );

    // Get the ChatCubit from context and load messages
    WidgetsBinding.instance.addPostFrameCallback((_) {
      try {
        final chatCubit = context.read<ChatCubit>();
        // Only load messages if conversation has a valid ID (>0)
        if (widget.conversation.id != null && widget.conversation.id! > 0) {
          print(
            '[ChatScreen] Loading messages for existing conversation (ID: ${widget.conversation.id})',
          );
          chatCubit.loadMessages(widget.conversation.id!);
        } else {
          // For newly created conversations, initialize with empty loaded state
          print(
            '[ChatScreen] Initializing new conversation with empty messages',
          );
          chatCubit.initializeNewConversation();
        }
      } catch (e) {
        print('[ChatScreen] ERROR in initState: $e');
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Text(widget.conversation.title ?? 'New Conversation'),
        leading: IconButton(
          icon: const Icon(Icons.menu),
          onPressed: () {
            _scaffoldKey.currentState?.openDrawer();
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () async {
              try {
                print('[ChatScreen] New conversation button pressed');
                // Create and save a new conversation
                context.read<ConversationCubit>().createConversation(
                  'New Conversation',
                );

                // Wait for the database to save
                await Future.delayed(const Duration(milliseconds: 200));

                if (mounted) {
                  // Get the newly created conversation from the cubit state
                  final cubitState = context.read<ConversationCubit>().state;
                  print(
                    '[ChatScreen] New button: Cubit state: ${cubitState.runtimeType}',
                  );

                  if (cubitState is ConversationsLoaded &&
                      cubitState.conversations.isNotEmpty) {
                    final newConversation = cubitState.conversations.last;
                    print(
                      '[ChatScreen] New button: Created conversation ID: ${newConversation.id}',
                    );

                    if (mounted) {
                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              ChatScreen(conversation: newConversation),
                        ),
                      );
                    }
                  } else {
                    print(
                      '[ChatScreen] New button ERROR: Failed to get new conversation from state',
                    );
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Error: Failed to create conversation'),
                      ),
                    );
                  }
                }
              } catch (e) {
                print('[ChatScreen] New button Exception: $e');
                if (mounted) {
                  ScaffoldMessenger.of(
                    context,
                  ).showSnackBar(SnackBar(content: Text('Error: $e')));
                }
              }
            },
          ),
        ],
      ),
      drawer: Sidebar(
        onClose: () {
          Navigator.pop(context);
        },
        onConversationSelected: (conversation) {
          try {
            print(
              '[ChatScreen] Conversation selected: ID=${conversation.id}, Title=${conversation.title}',
            );
            Navigator.pop(context);

            if (conversation.id != null && conversation.id! > 0) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (context) => ChatScreen(conversation: conversation),
                ),
              );
            } else {
              print(
                '[ChatScreen] ERROR: Selected conversation has invalid ID: ${conversation.id}',
              );
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Error: Invalid conversation')),
              );
            }
          } catch (e) {
            print('[ChatScreen] Exception in onConversationSelected: $e');
            Navigator.pop(context);
            ScaffoldMessenger.of(
              context,
            ).showSnackBar(SnackBar(content: Text('Error: $e')));
          }
        },
      ),
      body: ErrorBoundary(
        context: 'ChatScreen',
        child: BlocConsumer<ChatCubit, ChatState>(
          listener: (context, state) {
            try {
              _scrollToBottom();
            } catch (e) {
              print('[ChatScreen] Error in listener: $e');
            }
          },
          builder: (context, state) {
            try {
              List<Message> messages = [];
              String? intentText;
              bool isSearchStarted = false;
              String? searchProgressText;
              List<Map<String, dynamic>> searchResults = [];
              String? searchCompletedText;
              String currentStreamingResponse = '';
              bool isStreaming = false;

              if (state is ChatLoaded) {
                messages = state.messages ?? [];
              } else if (state is ChatIntentDetected) {
                messages = state.messages ?? [];
                final intentData = state.intentData;
                final intents = intentData['intents'] as List<dynamic>? ?? [];
                final searchQueries = intentData['search_queries'] as List<dynamic>? ?? [];
                
                if (intents.isNotEmpty) {
                  intentText = 'Detected Intent: ${intents.map((i) => i.toString()).join(', ')}';
                } else {
                  intentText = 'Intent detection completed';
                }
                
                if (searchQueries.isNotEmpty) {
                  intentText += '\nSearch Queries: ${searchQueries.map((q) => q.toString()).join(', ')}';
                }
              } else if (state is ChatSearchStarted) {
                messages = state.messages ?? [];
                isSearchStarted = true;
              } else if (state is ChatSearchProgress) {
                messages = state.messages ?? [];
                final progressData = state.progressData;
                final query = progressData['query'] as String? ?? '';
                final current = progressData['current'] as int? ?? 0;
                final total = progressData['total'] as int? ?? 0;
                searchProgressText = 'Searching ($current/$total): $query';
              } else if (state is ChatSearchResultsReceived) {
                messages = state.messages ?? [];
                searchResults = state.results ?? [];
              } else if (state is ChatSearchCompleted) {
                messages = state.messages ?? [];
                final completionData = state.completionData;
                final sources = completionData['sources'] as int? ?? 0;
                searchCompletedText = 'Search completed. Found information from $sources sources.';
              } else if (state is ChatResponseStarted) {
                messages = state.messages ?? [];
                currentStreamingResponse = state.currentResponse ?? '';
                isStreaming = true;
              } else if (state is ChatResponseStreaming) {
                messages = state.messages ?? [];
                currentStreamingResponse = state.currentResponse ?? '';
                isStreaming = state.isStreaming;
              } else if (state is ChatLoading) {
                return const Center(child: CircularProgressIndicator());
              } else if (state is ChatError) {
                return Center(child: Text('Error: ${state.message}'));
              }

              return Column(
                children: [
                  Expanded(
                    child: messages.isEmpty && currentStreamingResponse.isEmpty
                        ? Center(
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Text(
                                'No messages yet. Start typing to begin the conversation!',
                                textAlign: TextAlign.center,
                                style: Theme.of(context).textTheme.bodyLarge,
                              ),
                            ),
                          )
                        : ListView.builder(
                            controller: _scrollController,
                            itemCount:
                                messages.length +
                                (intentText != null ? 1 : 0) +
                                (isSearchStarted ? 1 : 0) +
                                (searchProgressText != null ? 1 : 0) +
                                (searchResults.isNotEmpty ? searchResults.length : 0) +
                                (searchCompletedText != null ? 1 : 0) +
                                (currentStreamingResponse.isNotEmpty ? 1 : 0),
                            itemBuilder: (context, index) {
                              print(
                                '[ChatScreen.itemBuilder] Rendering item at index $index, total: ${messages.length + (intentText != null ? 1 : 0) + (isSearchStarted ? 1 : 0) + (searchProgressText != null ? 1 : 0) + (searchResults.isNotEmpty ? searchResults.length : 0) + (searchCompletedText != null ? 1 : 0) + (currentStreamingResponse.isNotEmpty ? 1 : 0)}',
                              );
                              try {
                                int currentIndex = 0;

                                // Show user/assistant messages
                                if (index < messages.length) {
                                  try {
                                    final message = messages[index];
                                    print(
                                      '[ChatScreen.itemBuilder] Message at index $index: role=${message?.role}, content_length=${message?.content?.length ?? 0}',
                                    );
                                    if (message == null) {
                                      print(
                                        '[ChatScreen] WARNING: Message at index $index is null',
                                      );
                                      return const SizedBox();
                                    }
                                    return ChatMessage(
                                      text: message.content ?? '',
                                      isUser:
                                          (message.role ?? 'assistant') ==
                                          'user',
                                      isStreaming: false,
                                      messageType:
                                          (message.role ?? 'assistant') ==
                                              'user'
                                          ? 'user'
                                          : 'response',
                                    );
                                  } catch (e) {
                                    print(
                                      '[ChatScreen] Error rendering message at index $index: $e',
                                    );
                                    return Container(
                                      padding: const EdgeInsets.all(16),
                                      child: Text(
                                        'Error displaying message: $e',
                                        style: const TextStyle(
                                          color: Colors.red,
                                        ),
                                      ),
                                    );
                                  }
                                }
                                currentIndex = messages.length;

                                // Show intent bubble
                                if (intentText != null &&
                                    index == currentIndex) {
                                  try {
                                    return ChatMessage(
                                      text: intentText,
                                      isUser: false,
                                      isStreaming: false,
                                      messageType: 'intent',
                                    );
                                  } catch (e) {
                                    print(
                                      '[ChatScreen] Error rendering intent: $e',
                                    );
                                    return const SizedBox();
                                  }
                                }
                                if (intentText != null) currentIndex++;

                                // Show search started bubble
                                if (isSearchStarted &&
                                    index == currentIndex) {
                                  try {
                                    return ChatMessage(
                                      text: 'Starting web search...',
                                      isUser: false,
                                      isStreaming: true,
                                      messageType: 'search',
                                    );
                                  } catch (e) {
                                    print(
                                      '[ChatScreen] Error rendering search started: $e',
                                    );
                                    return const SizedBox();
                                  }
                                }
                                if (isSearchStarted) currentIndex++;

                                // Show search progress bubble
                                if (searchProgressText != null &&
                                    index == currentIndex) {
                                  try {
                                    return ChatMessage(
                                      text: searchProgressText,
                                      isUser: false,
                                      isStreaming: true,
                                      messageType: 'search',
                                    );
                                  } catch (e) {
                                    print(
                                      '[ChatScreen] Error rendering search progress: $e',
                                    );
                                    return const SizedBox();
                                  }
                                }
                                if (searchProgressText != null) currentIndex++;

                                // Show search results
                                if (searchResults.isNotEmpty &&
                                    index >= currentIndex &&
                                    index < currentIndex + searchResults.length) {
                                  try {
                                    final resultIndex = index - currentIndex;
                                    final result = searchResults[resultIndex];
                                    final title = result['title'] as String? ?? 'Untitled';
                                    final url = result['url'] as String? ?? '';
                                    
                                    return ChatMessage(
                                      text: '$title\n$url',
                                      isUser: false,
                                      isStreaming: false,
                                      messageType: 'search',
                                    );
                                  } catch (e) {
                                    print(
                                      '[ChatScreen] Error rendering search result: $e',
                                    );
                                    return const SizedBox();
                                  }
                                }
                                if (searchResults.isNotEmpty) currentIndex += searchResults.length;

                                // Show search completed
                                if (searchCompletedText != null &&
                                    index == currentIndex) {
                                  try {
                                    return ChatMessage(
                                      text: searchCompletedText,
                                      isUser: false,
                                      isStreaming: false,
                                      messageType: 'search',
                                    );
                                  } catch (e) {
                                    print(
                                      '[ChatScreen] Error rendering search completed: $e',
                                    );
                                    return const SizedBox();
                                  }
                                }
                                if (searchCompletedText != null) currentIndex++;

                                // Show streaming response
                                if (currentStreamingResponse.isNotEmpty &&
                                    index == currentIndex) {
                                  try {
                                    return ChatMessage(
                                      text: currentStreamingResponse,
                                      isUser: false,
                                      isStreaming: isStreaming,
                                      messageType: 'response',
                                    );
                                  } catch (e) {
                                    print(
                                      '[ChatScreen] Error rendering streaming response: $e',
                                    );
                                    return const SizedBox();
                                  }
                                }

                                return const SizedBox();
                              } catch (e) {
                                print(
                                  '[ChatScreen] ERROR in itemBuilder at index $index: $e',
                                );
                                return Container(
                                  padding: const EdgeInsets.all(16),
                                  child: Text(
                                    'Error: $e',
                                    style: const TextStyle(color: Colors.red),
                                  ),
                                );
                              }
                            },
                          ),
                  ),
                  ChatInput(
                    onSend: (message) {
                      try {
                        context.read<ChatCubit>().sendMessage(
                          message,
                          widget.conversation.id ?? 0,
                        );
                        final updatedConversation = Conversation(
                          id: widget.conversation.id,
                          title: widget.conversation.title,
                          createdAt: widget.conversation.createdAt,
                          updatedAt: DateTime.now(),
                        );
                        context.read<ConversationCubit>().updateConversation(
                          updatedConversation,
                        );
                      } catch (e) {
                        print('[ChatScreen] Error sending message: $e');
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Error sending message: $e')),
                        );
                      }
                    },
                    onCancel: () {
                      try {
                        context.read<ChatCubit>().cancelStream();
                      } catch (e) {
                        print('[ChatScreen] Error canceling stream: $e');
                      }
                    },
                  ),
                ],
              );
            } catch (e) {
              print('[ChatScreen] ERROR in builder: $e');
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error, size: 64, color: Colors.red),
                      const SizedBox(height: 16),
                      Text(
                        'An error occurred: $e',
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          try {
                            context.read<ChatCubit>().loadMessages(
                              widget.conversation.id ?? 0,
                            );
                          } catch (e2) {
                            print('[ChatScreen] Error reloading: $e2');
                          }
                        },
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              );
            }
          },
        ),
      ),
    );
  }
}