import 'package:shared_preferences/shared_preferences.dart';

class SettingsService {
  static final SettingsService _instance = SettingsService._internal();
  factory SettingsService() => _instance;
  SettingsService._internal();

  late SharedPreferences _prefs;
  bool _initialized = false;

  static const String _baseUrlKey = 'api_base_url';
  static const String _defaultBaseUrl = 'http://localhost:8000';
  static const String _modelNameKey = 'model_name';
  static const String _defaultModelName = 'khoj-ai';

  Future<void> init() async {
    if (_initialized) return;
    _prefs = await SharedPreferences.getInstance();
    _initialized = true;
  }

  String get baseUrl => _prefs.getString(_baseUrlKey) ?? _defaultBaseUrl;
  String get modelName => _prefs.getString(_modelNameKey) ?? _defaultModelName;

  Future<void> setBaseUrl(String url) async {
    await _prefs.setString(_baseUrlKey, url);
  }

  Future<void> setModelName(String name) async {
    await _prefs.setString(_modelNameKey, name);
  }

  Future<void> resetToDefaults() async {
    await _prefs.remove(_baseUrlKey);
    await _prefs.remove(_modelNameKey);
  }
}
