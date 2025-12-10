import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../state/cubits/chat_cubit.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onSend;
  final Function()? onCancel;

  const ChatInput({super.key, required this.onSend, this.onCancel});

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ChatCubit, ChatState>(
      builder: (context, state) {
        bool isStreaming = false;
        
        if (state is ChatResponseStarted) {
          isStreaming = true;
        } else if (state is ChatResponseStreaming) {
          isStreaming = state.isStreaming;
        }

        return TweenAnimationBuilder<double>(
          tween: Tween<double>(begin: 0.5, end: 1.0),
          duration: const Duration(milliseconds: 300),
          builder: (context, value, child) {
            return Transform.scale(
              scale: value,
              child: Container(
                padding: const EdgeInsets.all(8),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _controller,
                        maxLines: null,
                        minLines: 1,
                        keyboardType: TextInputType.multiline,
                        enabled: !isStreaming,
                        decoration: InputDecoration(
                          hintText: 'Type a message...',
                          border: const OutlineInputBorder(
                            borderRadius: BorderRadius.all(Radius.circular(20)),
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 12,
                          ),
                          suffixIcon: isStreaming
                              ? Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                        Theme.of(context).colorScheme.primary,
                                      ),
                                    ),
                                  ),
                                )
                              : null,
                        ),
                        onSubmitted: (value) {
                          if (value.trim().isNotEmpty && !isStreaming) {
                            widget.onSend(value);
                            _controller.clear();
                          }
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    if (isStreaming)
                      IconButton(
                        icon: const Icon(Icons.stop_circle),
                        onPressed: widget.onCancel,
                        tooltip: 'Stop generation',
                        style: IconButton.styleFrom(
                          backgroundColor: Theme.of(
                            context,
                          ).colorScheme.errorContainer,
                          foregroundColor: Theme.of(
                            context,
                          ).colorScheme.onErrorContainer,
                        ),
                      )
                    else
                      ScaleTransition(
                        scale: Tween<double>(begin: 0.0, end: 1.0).animate(
                          CurvedAnimation(
                            parent: AnimationController(
                              duration: const Duration(milliseconds: 200),
                              vsync: Navigator.of(context),
                            )..forward(),
                            curve: Curves.elasticOut,
                          ),
                        ),
                        child: IconButton(
                          icon: const Icon(Icons.send),
                          onPressed: () {
                            try {
                              if (_controller.text.trim().isNotEmpty) {
                                print(
                                  '[ChatInput] Sending message: ${_controller.text}',
                                );
                                widget.onSend(_controller.text);
                                _controller.clear();
                              }
                            } catch (e) {
                              print('[ChatInput] Error sending message: $e');
                              ScaffoldMessenger.of(
                                context,
                              ).showSnackBar(SnackBar(content: Text('Error: $e')));
                            }
                          },
                          tooltip: 'Send message',
                          style: IconButton.styleFrom(
                            backgroundColor: Theme.of(context).colorScheme.primary,
                            foregroundColor: Theme.of(context).colorScheme.onPrimary,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}