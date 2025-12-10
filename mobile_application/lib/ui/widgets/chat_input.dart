import 'package:flutter/material.dart';
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

        return Container(
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
                IconButton(
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
            ],
          ),
        );
      },
    );
  }
}