import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class ChatMessage extends StatefulWidget {
  final String text;
  final bool isUser;
  final bool isStreaming;
  final String messageType; // 'intent', 'search', 'response', 'final', 'user'

  const ChatMessage({
    super.key,
    required this.text,
    required this.isUser,
    this.isStreaming = false,
    this.messageType = 'response',
  });

  @override
  State<ChatMessage> createState() => _ChatMessageState();
}

class _ChatMessageState extends State<ChatMessage>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  bool _showCopyFeedback = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    if (widget.isStreaming) {
      _animationController.forward();
    }
  }

  @override
  void didUpdateWidget(covariant ChatMessage oldWidget) {
    super.didUpdateWidget(oldWidget);
    // If streaming state changed, start or reverse the animation accordingly
    if (!oldWidget.isStreaming && widget.isStreaming) {
      _animationController.forward();
    } else if (oldWidget.isStreaming && !widget.isStreaming) {
      _animationController.reverse();
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _copyToClipboard() {
    Clipboard.setData(ClipboardData(text: widget.text));
    setState(() {
      _showCopyFeedback = true;
    });
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _showCopyFeedback = false;
        });
      }
    });
  }

  Color _getBackgroundColor(BuildContext context) {
    if (widget.isUser) {
      return Theme.of(context).colorScheme.primary;
    }

    switch (widget.messageType) {
      case 'intent':
        return Colors.blue.withOpacity(0.1);
      case 'search':
        return Colors.green.withOpacity(0.1);
      case 'response':
        return Theme.of(context).colorScheme.surfaceContainerHighest;
      default:
        return Theme.of(context).colorScheme.surfaceContainerHighest;
    }
  }

  Color _getTextColor(BuildContext context) {
    if (widget.isUser) {
      return Theme.of(context).colorScheme.onPrimary;
    }

    switch (widget.messageType) {
      case 'intent':
        return Colors.blue;
      case 'search':
        return Colors.green;
      default:
        return Theme.of(context).colorScheme.onSurfaceVariant;
    }
  }

  String _getMessageLabel() {
    switch (widget.messageType) {
      case 'intent':
        return 'Intent Detected';
      case 'search':
        return 'Web Search';
      case 'response':
        return widget.isStreaming ? 'Generating Response' : 'Response';
      default:
        return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    try {
      return Align(
        alignment: widget.isUser ? Alignment.centerRight : Alignment.centerLeft,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Flexible(
                child: Container(
                  margin: const EdgeInsets.symmetric(vertical: 4),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _getBackgroundColor(context),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Message label
                      if (!widget.isUser && widget.messageType != 'response')
                        Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getTextColor(context).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            _getMessageLabel(),
                            style: TextStyle(
                              color: _getTextColor(context),
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      // Main text content
                      Text(
                        widget.text.isEmpty ? '[Empty message]' : widget.text,
                        style: TextStyle(
                          color: _getTextColor(context),
                          fontSize: 14,
                        ),
                      ),
                      // Streaming indicator
                      if (widget.isStreaming)
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: SizedBox(
                            height: 20,
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                SizedBox(
                                  width: 12,
                                  height: 12,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 1.5,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                      _getTextColor(context),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Streaming...',
                                  style: TextStyle(
                                    color: _getTextColor(context),
                                    fontSize: 11,
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              // Copy button (only for non-user messages with content)
              if (!widget.isUser && widget.text.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Material(
                        color: Colors.transparent,
                        child: InkWell(
                          onTap: () {
                            try {
                              _copyToClipboard();
                            } catch (e) {
                              print(
                                '[ChatMessage] Error copying to clipboard: $e',
                              );
                            }
                          },
                          borderRadius: BorderRadius.circular(20),
                          child: Padding(
                            padding: const EdgeInsets.all(8),
                            child: Icon(
                              _showCopyFeedback ? Icons.check : Icons.copy,
                              size: 16,
                              color: _showCopyFeedback
                                  ? Colors.green
                                  : Theme.of(context).colorScheme.outline,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      );
    } catch (e) {
      print('[ChatMessage] Error building message: $e');
      return Padding(
        padding: const EdgeInsets.all(8.0),
        child: Text(
          'Error displaying message: $e',
          style: const TextStyle(color: Colors.red),
        ),
      );
    }
  }
}
