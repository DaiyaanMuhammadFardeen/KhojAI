import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'dart:async';
import 'ui/screens/home_screen.dart';
import 'state/cubits/conversation_cubit.dart';
import 'state/cubits/chat_cubit.dart';
import 'services/settings_service.dart';

void main() async {
  print('[main] Starting KhojAI app...');

  // Create a zone that catches all errors
  runZonedGuarded(
    () async {
      try {
        // Initialize sqflite_common_ffi for desktop platforms (Linux, Windows, macOS)
        print('[main] Initializing sqflite FFI...');
        sqfliteFfiInit();
        databaseFactory = databaseFactoryFfi;
        print('[main] sqflite FFI initialized');

        // Initialize settings service
        print('[main] Initializing settings service...');
        await SettingsService().init();
        print('[main] Settings service initialized');

        print('[main] Initialization complete, running app');
        runApp(const MyApp());
      } catch (e, stackTrace) {
        print('[main] ERROR during initialization: $e');
        print('[main] Stack: $stackTrace');
        runApp(
          ErrorApp(error: e.toString(), stackTrace: stackTrace.toString()),
        );
      }
    },
    (Object error, StackTrace stackTrace) {
      print('[ZONE UNCAUGHT ERROR] $error');
      print('[ZONE UNCAUGHT ERROR Stack] $stackTrace');
    },
  );
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  bool _isDarkMode = SettingsService().getDarkMode();

  @override
  void initState() {
    super.initState();
    // Listen for theme changes
    SettingsService.themeChangeStream.listen((isDarkMode) {
      if (mounted) {
        setState(() {
          _isDarkMode = isDarkMode;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    try {
      // Set up Flutter error handler
      FlutterError.onError = (FlutterErrorDetails details) {
        print('[FLUTTER ERROR] ${details.exceptionAsString()}');
        print('[FLUTTER ERROR STACK] ${details.stack}');
      };

      return MultiBlocProvider(
        providers: [
          BlocProvider(create: (context) => ConversationCubit()),
          BlocProvider(create: (context) => ChatCubit()),
        ],
        child: MaterialApp(
          title: 'Khoj AI',
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
          ),
          darkTheme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(
              seedColor: Colors.deepPurple,
              brightness: Brightness.dark,
            ),
          ),
          themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
          home: const HomeScreen(),
          builder: (context, child) {
            return Builder(
              builder: (BuildContext context) {
                // Wrap with error boundary
                return child ?? const SizedBox();
              },
            );
          },
        ),
      );
    } catch (e, st) {
      print('[MyApp] ERROR building app: $e');
      print('[MyApp] Stack: $st');
      return MaterialApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('Error')),
          body: Center(child: Text('App build error: $e\n\n$st')),
        ),
      );
    }
  }
}

class ErrorApp extends StatelessWidget {
  final String error;
  final String? stackTrace;

  const ErrorApp({super.key, required this.error, this.stackTrace});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Khoj AI - Error',
      home: Scaffold(
        appBar: AppBar(title: const Text('Initialization Error')),
        body: SingleChildScrollView(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  const Text(
                    'Failed to initialize application',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    error,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 14, color: Colors.red),
                  ),
                  if (stackTrace != null) ...[
                    const SizedBox(height: 16),
                    Text(
                      'Stack trace:\n$stackTrace',
                      textAlign: TextAlign.left,
                      style: const TextStyle(
                        fontSize: 10,
                        color: Colors.grey,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  const Text(
                    'Please check the console logs for more details.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}