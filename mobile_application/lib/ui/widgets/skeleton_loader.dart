import 'package:flutter/material.dart';

class SkeletonLoader extends StatelessWidget {
  final double width;
  final double height;
  final ShapeBorder shapeBorder;

  const SkeletonLoader.rectangular({
    super.key,
    this.width = double.infinity,
    required this.height,
  }) : shapeBorder = const RoundedRectangleBorder();

  const SkeletonLoader.circular({
    super.key,
    required this.width,
    required this.height,
  }) : shapeBorder = const CircleBorder();

  SkeletonLoader.rounded({
    super.key,
    this.width = double.infinity,
    required this.height,
    double radius = 8.0,
  }) : shapeBorder = RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radius),
        );

  @override
  Widget build(BuildContext context) {
    return ShimmerSkeleton(
      width: width,
      height: height,
      shapeBorder: shapeBorder,
    );
  }
}

class ShimmerSkeleton extends StatefulWidget {
  final double width;
  final double height;
  final ShapeBorder shapeBorder;

  const ShimmerSkeleton({
    super.key,
    required this.width,
    required this.height,
    required this.shapeBorder,
  });

  @override
  State<ShimmerSkeleton> createState() => _ShimmerSkeletonState();
}

class _ShimmerSkeletonState extends State<ShimmerSkeleton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _animation = Tween<double>(begin: 0.2, end: 0.8).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    _controller.repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Opacity(
          opacity: _animation.value,
          child: Container(
            width: widget.width,
            height: widget.height,
            decoration: ShapeDecoration(
              shape: widget.shapeBorder,
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
            ),
          ),
        );
      },
    );
  }
}