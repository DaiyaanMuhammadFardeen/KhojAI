import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class NewConversationButton extends StatefulWidget {
  final VoidCallback onPressed;

  const NewConversationButton({super.key, required this.onPressed});

  @override
  State<NewConversationButton> createState() => _NewConversationButtonState();
}

class _NewConversationButtonState extends State<NewConversationButton>
    with TickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0.0, end: 1.0),
      duration: const Duration(milliseconds: 500),
      builder: (context, value, child) {
        return Transform.scale(
          scale: value,
          child: RotationTransition(
            turns: Tween<double>(begin: -0.25, end: 0).animate(
              CurvedAnimation(
                parent: _controller,
                curve: Curves.elasticOut,
              ),
            ),
            child: FloatingActionButton(
              backgroundColor: Theme.of(context).colorScheme.primary,
              onPressed: widget.onPressed,
              child: const Icon(Icons.add),
            ),
          ),
        );
      },
    );
  }
}
