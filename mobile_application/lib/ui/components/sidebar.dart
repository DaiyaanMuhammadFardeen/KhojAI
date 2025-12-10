import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../screens/chat_screen.dart';
import '../screens/settings_screen.dart';
import '../../state/cubits/conversation_cubit.dart';
import '../../data/models/conversation.dart';

class Sidebar extends StatelessWidget {
  final VoidCallback onClose;
  final ValueChanged<Conversation> onConversationSelected;

  const Sidebar({
    super.key,
    required this.onClose,
    required this.onConversationSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: [
          // Header
          Container(
            height: 100,
            padding: const EdgeInsets.all(16),
            color: Theme.of(context).colorScheme.primary,
            child: Row(
              children: [
                const Icon(Icons.chat, color: Colors.white, size: 32),
                const SizedBox(width: 12),
                Text(
                  'KhojAI',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),

          // Settings Button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: OutlinedButton.icon(
              onPressed: () {
                try {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const SettingsScreen(),
                    ),
                  );
                } catch (e) {
                  print('[Sidebar] Error opening settings: $e');
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Error opening settings: $e')),
                    );
                  }
                }
              },
              icon: const Icon(Icons.settings),
              label: const Text('Settings'),
            ),
          ),

          // New Conversation Button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ElevatedButton(
              onPressed: () {
                try {
                  print('[Sidebar] New conversation button pressed');
                  // Create and save the conversation using the cubit
                  context.read<ConversationCubit>().createConversation(
                    'New Conversation',
                  );
                } catch (e) {
                  print('[Sidebar] Exception creating conversation: $e');
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Error creating conversation: $e')),
                    );
                  }
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.secondary,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.add, size: 16),
                  SizedBox(width: 8),
                  Text('New Conversation'),
                ],
              ),
            ),
          ),

          // Conversation List
          Expanded(
            child: BlocBuilder<ConversationCubit, ConversationState>(
              builder: (context, state) {
                if (state is ConversationsLoading) {
                  return const Center(child: CircularProgressIndicator());
                } else if (state is ConversationError) {
                  return Center(child: Text('Error: ${state.message}'));
                } else if (state is ConversationsLoaded) {
                  final conversations = state.conversations;
                  return ListView.builder(
                    itemCount: conversations.length,
                    itemBuilder: (context, index) {
                      final conversation = conversations[index];
                      return ListTile(
                        title: Text(
                          conversation.title,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        subtitle: Text(
                          'Last updated: ${conversation.updatedAt.toLocal().toString().split(' ')[0]}',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                        onTap: () {
                          try {
                            print(
                              '[Sidebar] Conversation tapped: ID=${conversation.id}, Title=${conversation.title}',
                            );

                            // Only navigate if conversation has a valid ID
                            if (conversation.id != null &&
                                conversation.id! > 0) {
                              onConversationSelected(conversation);
                            } else {
                              print(
                                '[Sidebar] ERROR: Conversation has invalid ID: ${conversation.id}',
                              );
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Error: Invalid conversation'),
                                  ),
                                );
                              }
                            }
                          } catch (e) {
                            print('[Sidebar] Exception in onTap: $e');
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: $e')),
                              );
                            }
                          }
                        },
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.edit, size: 18),
                              onPressed: () async {
                                try {
                                  final controller = TextEditingController(
                                    text: conversation.title,
                                  );
                                  final result = await showDialog<String>(
                                    context: context,
                                    builder: (context) => AlertDialog(
                                      title: const Text('Rename Conversation'),
                                      content: TextField(
                                        controller: controller,
                                        decoration: const InputDecoration(
                                          labelText: 'Title',
                                        ),
                                      ),
                                      actions: [
                                        TextButton(
                                          onPressed: () =>
                                              Navigator.pop(context, null),
                                          child: const Text('Cancel'),
                                        ),
                                        TextButton(
                                          onPressed: () => Navigator.pop(
                                            context,
                                            controller.text.trim(),
                                          ),
                                          child: const Text('Rename'),
                                        ),
                                      ],
                                    ),
                                  );

                                  if (result != null && result.isNotEmpty) {
                                    final updated = conversation.copyWith(
                                      title: result,
                                      updatedAt: DateTime.now(),
                                    );
                                    await context
                                        .read<ConversationCubit>()
                                        .updateConversation(updated);
                                  }
                                } catch (e) {
                                  print('[Sidebar] Error renaming: $e');
                                  if (context.mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('Error renaming: $e')),
                                    );
                                  }
                                }
                              },
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete, size: 18),
                              onPressed: () {
                                try {
                                  // Delete conversation using the cubit
                                  context
                                      .read<ConversationCubit>()
                                      .deleteConversation(conversation.id ?? 0);
                                } catch (e) {
                                  print('[Sidebar] Error deleting: $e');
                                  if (context.mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('Error deleting: $e')),
                                    );
                                  }
                                }
                              },
                            ),
                          ],
                        ),
                      );
                    },
                  );
                }
                return const SizedBox();
              },
            ),
          ),
        ],
      ),
    );
  }
}