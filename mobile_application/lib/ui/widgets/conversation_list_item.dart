import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import '../../data/models/conversation.dart';

class ConversationListItem extends StatelessWidget {
  final Conversation conversation;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const ConversationListItem({
    super.key,
    required this.conversation,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: 1),
      duration: const Duration(milliseconds: 500),
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, 50 * (1 - value)),
            child: Card(
              margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              elevation: value * 2,
              child: ListTile(
                title: Text(conversation.title, overflow: TextOverflow.ellipsis),
                subtitle: Text(
                  '${conversation.updatedAt.hour}:${conversation.updatedAt.minute.toString().padLeft(2, '0')}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                onTap: onTap,
                trailing: IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: onDelete,
                  mouseCursor: SystemMouseCursors.click,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
