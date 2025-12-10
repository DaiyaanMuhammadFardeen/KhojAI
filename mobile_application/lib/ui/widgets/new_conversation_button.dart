import 'package:flutter/material.dart';

class NewConversationButton extends StatelessWidget {
  final VoidCallback onPressed;

  const NewConversationButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton(
      backgroundColor: Theme.of(context).colorScheme.primary,
      onPressed: onPressed,
      child: const Icon(Icons.add),
    );
  }
}
