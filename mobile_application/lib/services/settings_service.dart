import 'package:shared_preferences/shared_preferences.dart';
import 'dart:async';

class SettingsService {
  static final SettingsService _instance = SettingsService._internal();
  factory SettingsService() => _instance;
  SettingsService._internal();

  late SharedPreferences _prefs;
  bool _initialized = false;

  // Stream controller for theme changes
  final StreamController<bool> _themeChangeController = StreamController<bool>.broadcast();
  static Stream<bool> get themeChangeStream => _instance._themeChangeController.stream;

  static const String _baseUrlKey = 'api_base_url';
  static const String _defaultBaseUrl = 'http://localhost:8000';
  static const String _modelNameKey = 'model_name';
  static const String _defaultModelName = 'khoj-ai';
  
  // New settings keys
  static const String _usernameKey = 'username';
  static const String _defaultUsername = 'User';
  static const String _systemPromptKey = 'system_prompt';
  static const String _defaultSystemPrompt = 'You are a helpful AI assistant.';
  static const String _darkModeKey = 'dark_mode';
  static const bool _defaultDarkMode = false;
  static const String _enableAnimationsKey = 'enable_animations';
  static const bool _defaultEnableAnimations = true;
  static const String _showWordCountKey = 'show_word_count';
  static const bool _defaultShowWordCount = true;
  static const String _fontSizeKey = 'font_size';
  static const double _defaultFontSize = 14.0;

  Future<void> init() async {
    if (_initialized) return;
    _prefs = await SharedPreferences.getInstance();
    _initialized = true;
  }

  String get baseUrl => _prefs.getString(_baseUrlKey) ?? _defaultBaseUrl;
  String get modelName => _prefs.getString(_modelNameKey) ?? _defaultModelName;
  
  // New getters
  String getUsername() => _prefs.getString(_usernameKey) ?? _defaultUsername;
  String getSystemPrompt() => _prefs.getString(_systemPromptKey) ?? _defaultSystemPrompt;
  bool getDarkMode() => _prefs.getBool(_darkModeKey) ?? _defaultDarkMode;
  bool getEnableAnimations() => _prefs.getBool(_enableAnimationsKey) ?? _defaultEnableAnimations;
  bool getShowWordCount() => _prefs.getBool(_showWordCountKey) ?? _defaultShowWordCount;
  double getFontSize() => _prefs.getDouble(_fontSizeKey) ?? _defaultFontSize;

  Future<void> setBaseUrl(String url) async {
    await _prefs.setString(_baseUrlKey, url);
  }

  Future<void> setModelName(String name) async {
    await _prefs.setString(_modelNameKey, name);
  }
  
  // New setters
  Future<void> setUsername(String username) async {
    await _prefs.setString(_usernameKey, username);
  }
  
  Future<void> setSystemPrompt(String prompt) async {
    await _prefs.setString(_systemPromptKey, prompt);
  }
  
  Future<void> setDarkMode(bool enabled) async {
    await _prefs.setBool(_darkModeKey, enabled);
    // Notify listeners about theme change
    _themeChangeController.add(enabled);
  }
  
  Future<void> setEnableAnimations(bool enabled) async {
    await _prefs.setBool(_enableAnimationsKey, enabled);
  }
  
  Future<void> setShowWordCount(bool enabled) async {
    await _prefs.setBool(_showWordCountKey, enabled);
  }
  
  Future<void> setFontSize(double size) async {
    await _prefs.setDouble(_fontSizeKey, size);
  }

  Future<void> resetToDefaults() async {
    await _prefs.remove(_baseUrlKey);
    await _prefs.remove(_modelNameKey);
    await _prefs.remove(_usernameKey);
    await _prefs.remove(_systemPromptKey);
    await _prefs.remove(_darkModeKey);
    await _prefs.remove(_enableAnimationsKey);
    await _prefs.remove(_showWordCountKey);
    await _prefs.remove(_fontSizeKey);
  }
  
  // Close the stream controller to prevent memory leaks
  void dispose() {
    _themeChangeController.close();
  }
}