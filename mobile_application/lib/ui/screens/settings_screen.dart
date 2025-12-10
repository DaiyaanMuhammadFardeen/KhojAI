import 'package:flutter/material.dart';
import '../../services/settings_service.dart';
import '../../services/api/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _baseUrlController;
  late TextEditingController _modelNameController;
  late TextEditingController _usernameController;
  late TextEditingController _systemPromptController;
  
  final SettingsService _settingsService = SettingsService();
  final ApiService _apiService = ApiService();
  
  // Personalization options
  bool _darkMode = false;
  bool _enableAnimations = true;
  bool _showWordCount = true;
  double _fontSize = 14.0;
  
  bool _isSaving = false;
  bool _isCheckingConnectivity = false;
  ApiHealthStatus? _lastHealthCheck;

  @override
  void initState() {
    super.initState();
    _baseUrlController = TextEditingController(text: _settingsService.baseUrl);
    _modelNameController = TextEditingController(
      text: _settingsService.modelName,
    );
    _usernameController = TextEditingController(
      text: _settingsService.getUsername(),
    );
    _systemPromptController = TextEditingController(
      text: _settingsService.getSystemPrompt(),
    );
    
    // Load personalization settings
    _darkMode = _settingsService.getDarkMode();
    _enableAnimations = _settingsService.getEnableAnimations();
    _showWordCount = _settingsService.getShowWordCount();
    _fontSize = _settingsService.getFontSize();
  }

  @override
  void dispose() {
    _baseUrlController.dispose();
    _modelNameController.dispose();
    _usernameController.dispose();
    _systemPromptController.dispose();
    super.dispose();
  }

  Future<void> _saveSettings() async {
    setState(() => _isSaving = true);
    try {
      await _settingsService.setBaseUrl(_baseUrlController.text);
      await _settingsService.setModelName(_modelNameController.text);
      await _settingsService.setUsername(_usernameController.text);
      await _settingsService.setSystemPrompt(_systemPromptController.text);
      
      // Save personalization settings
      await _settingsService.setDarkMode(_darkMode);
      await _settingsService.setEnableAnimations(_enableAnimations);
      await _settingsService.setShowWordCount(_showWordCount);
      await _settingsService.setFontSize(_fontSize);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Settings saved successfully')),
      );

      // Don't pop the context since we want to show the changes
      // Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error saving settings: $e')));
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  Future<void> _resetToDefaults() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset to Defaults'),
        content: const Text('Are you sure you want to reset all settings?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Reset'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _settingsService.resetToDefaults();
      if (!mounted) return;
      _baseUrlController.text = _settingsService.baseUrl;
      _modelNameController.text = _settingsService.modelName;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Settings reset to defaults')),
      );
    }
  }

  Future<void> _checkApiConnectivity() async {
    setState(() => _isCheckingConnectivity = true);
    try {
      final healthStatus = await _apiService.checkApiHealth();
      if (mounted) {
        setState(() {
          _lastHealthCheck = healthStatus;
          _isCheckingConnectivity = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _lastHealthCheck = ApiHealthStatus(success: false, error: e.toString());
          _isCheckingConnectivity = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // API Settings Section
              Text(
                'API Configuration',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _baseUrlController,
                decoration: InputDecoration(
                  labelText: 'Base URL',
                  hintText: 'http://localhost:8000',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.link),
                ),
                keyboardType: TextInputType.url,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _modelNameController,
                decoration: InputDecoration(
                  labelText: 'Model Name',
                  hintText: 'khoj-ai',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.settings),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _usernameController,
                decoration: InputDecoration(
                  labelText: 'Username',
                  hintText: 'Enter your name',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.person),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _systemPromptController,
                maxLines: 3,
                decoration: InputDecoration(
                  labelText: 'System Prompt',
                  hintText: 'Instructions for the AI...',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.psychology),
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 16),
              // API Connectivity Check
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'API Connection Status',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          if (_isCheckingConnectivity)
                            const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          else
                            IconButton(
                              icon: const Icon(Icons.refresh),
                              onPressed: _checkApiConnectivity,
                            ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      if (_lastHealthCheck != null) ...[
                        if (_lastHealthCheck!.success) ...[
                          Row(
                            children: [
                              const Icon(Icons.check_circle, color: Colors.green),
                              const SizedBox(width: 8),
                              Text(
                                'Connected successfully (Status: ${_lastHealthCheck!.statusCode})',
                                style: const TextStyle(color: Colors.green),
                              ),
                            ],
                          ),
                        ] else ...[
                          Row(
                            children: [
                              const Icon(Icons.error, color: Colors.red),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _lastHealthCheck!.error ?? 'Unknown error occurred',
                                  style: const TextStyle(color: Colors.red),
                                  softWrap: true,
                                ),
                              ),
                            ],
                          ),
                        ]
                      ] else ...[
                        const Text(
                          'Click refresh to check API connectivity',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              // Personalization Options
              Text(
                'Personalization',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 16),
              SwitchListTile.adaptive(
                title: const Text('Dark Mode'),
                value: _darkMode,
                onChanged: (value) {
                  setState(() {
                    _darkMode = value;
                  });
                },
              ),
              SwitchListTile.adaptive(
                title: const Text('Enable Animations'),
                value: _enableAnimations,
                onChanged: (value) {
                  setState(() {
                    _enableAnimations = value;
                  });
                },
              ),
              SwitchListTile.adaptive(
                title: const Text('Show Word Count'),
                value: _showWordCount,
                onChanged: (value) {
                  setState(() {
                    _showWordCount = value;
                  });
                },
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  const Text('Font Size'),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Slider(
                      value: _fontSize,
                      min: 10,
                      max: 20,
                      divisions: 10,
                      label: _fontSize.round().toString(),
                      onChanged: (value) {
                        setState(() {
                          _fontSize = value;
                        });
                      },
                    ),
                  ),
                  Text('${_fontSize.round()}'),
                ],
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _isSaving ? null : _saveSettings,
                      child: _isSaving
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Save Settings'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  OutlinedButton(
                    onPressed: _isSaving ? null : _resetToDefaults,
                    child: const Text('Reset'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                'Note: Settings are applied instantly without restarting the app.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontStyle: FontStyle.italic,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              // Information Section
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Information',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Base URL: The HTTP endpoint where your Khoj AI backend is running.\n\n'
                      'Model Name: The name of the language model to use for responses.',
                      style: TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}