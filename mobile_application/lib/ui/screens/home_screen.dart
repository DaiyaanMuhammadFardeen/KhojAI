import'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import './chat_screen.dart';
import './settings_screen.dart';
import '../widgets/error_boundary.dart';
import '../../state/cubits/conversation_cubit.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    context.read<ConversationCubit>().loadConversations();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
appBar: AppBar(
        title: const Text('Khoj AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
body: ErrorBoundary(
        context: 'HomeScreen',
        child: BlocConsumer<ConversationCubit, ConversationState>(
          listener: (context, state) {
            // Listen for newly created conversations and navigate to them
            if (state is ConversationCreated) {
              WidgetsBinding.instance.addPostFrameCallback((_) {
                if (context.mounted) {
                  Navigator.push(
                    context,
                   MaterialPageRoute(
                      builder: (context) => ChatScreen(conversation: state.conversation),
                    ),
                  );
                }
              });
            }
          },
          builder: (context, state) {
            try {
              if (state is ConversationsLoaded) {
                if (state.conversations.isEmpty) {
                  return Center(
child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.chat, size: 64, color: Colors.grey),
                        const SizedBox(height: 16),
                        const Text(
                          'No conversations yet',
                          style: TextStyle(fontSize: 18),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () {
try{
                              print(
                                '[HomeScreen] Creating new conversation...',
                              );
                              context
                                  .read<ConversationCubit>()
                                  .createConversation('New Conversation');
                            } catch (e) {
                              print('[HomeScreen] Exception: $e');
                              if (mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Error: $e')),
                                );
                              }
                            }
                          },
                          child: const Text('Start New Chat'),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  itemCount: state.conversations.length,
                  itemBuilder: (context, index) {
                   try {
                      final conversation = state.conversations[index];
                      if (conversation == null) {
                        print(
                          '[HomeScreen] WARNING: Null conversation at index $index',
                        );
                        return const SizedBox();
                      }
                      return Card(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical:4,
                        ),
                        child: ListTile(
                          title: Text(conversation.title ?? 'Untitled'),
                          subtitle: Text(
                            '${conversation.updatedAt.day}/${conversation.updatedAt.month}/${conversation.updatedAt.year}',
                          ),
                          onTap: () {
                            try {
                              print(
                                '[HomeScreen] Tapped conversation:ID=${conversation.id}',
                              );

                              if (conversation.id != null &&
                                  conversation.id! > 0) {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>
                                        ChatScreen(conversation: conversation),
                                  ),
                                );
                              } else {
                                print('[HomeScreen] ERROR:Invalid ID');
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text(
                                      'Error: Invalid conversation',
                                    ),
                                  ),
                                );
                              }
                            } catch (e) {
                              print('[HomeScreen] Exception in onTap: $e');
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: $e')),
                              );
                            }
                          },
                          trailing: IconButton(
                            icon: const Icon(Icons.delete),
                            onPressed: () {
                              try {
                                if (conversation.id != null) {
                                  context
                                      .read<ConversationCubit>()
                                      .deleteConversation(conversation.id!);
                                }
                              } catch (e) {
                                print('[HomeScreen] Error deleting: $e');
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Error: $e')),
                                );
                              }
                            },
                          ),
                        ),
                      );
                    } catch (e) {
print('[HomeScreen] ERROR in itemBuilder: $e');
                      return Container(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          'Error: $e',
                          style: const TextStyle(color: Colors.red),
                        ),
                      );
                    }
                  },
                );
              } else if (state is ConversationsLoading) {
                return const Center(child: CircularProgressIndicator());
              } else if (state is ConversationError) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error, size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        Text('Error: ${state.message}'),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () {
                            context
                                .read<ConversationCubit>()
                                .loadConversations();
                          },
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                );
              } else {
                return const Center(child: Text('Something went wrong'));
              }
            } catch (e) {
              print('[HomeScreen] ERROR in builder: $e');
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error, size: 64, color: Colors.red),
                      const SizedBox(height: 16),
                      Text('Unexpected error: $e'),
const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          context.read<ConversationCubit>().loadConversations();
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
      floatingActionButton: FloatingActionButton(
       onPressed: () {
try {
            print('[HomeScreen] FAB pressed');
            context.read<ConversationCubit>().createConversation(
              'New Conversation',
            );
          } catch (e) {
            print('[HomeScreen] FAB Exception: $e');
            if (mounted) {
              ScaffoldMessenger.of(
                context,
).showSnackBar(SnackBar(content: Text('Error: $e')));
            }
          }
        },
        child: const Icon(Icons.chat),
      ),
    );
  }
}
