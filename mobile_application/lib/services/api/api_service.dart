import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../settings_service.dart';

class ApiService {
  static const String streamEndpoint = '/stream';
  final SettingsService _settingsService = SettingsService();

  /// Streams AI responses token by token from the backend
  Stream<Map<String, dynamic>> streamAIResponse(
    String message,
    int conversationId,
  ) async* {
    try {
      final baseUrl = _settingsService.baseUrl;
      print('[ApiService] Streaming from: $baseUrl$streamEndpoint');
      final url = Uri.parse('$baseUrl$streamEndpoint');

      try {
        final request = http.Request('POST', url)
          ..headers['Content-Type'] = 'application/json'
          ..body = jsonEncode({
            'message': message,
            'conversation_id': conversationId,
          });

        print('[ApiService] Sending request to: $url');
        final response = await request.send();
        print('[ApiService] Response status: ${response.statusCode}');

        if (response.statusCode == 200) {
          await for (final chunk in response.stream.transform(utf8.decoder)) {
            try {
              // Split by newlines to handle SSE format if applicable
              final lines = chunk.split('\n');
              for (final line in lines) {
                if (line.startsWith('data: ')) {
                  final data = line.substring(6); // Remove 'data: ' prefix
                  try {
                    final jsonData = jsonDecode(data);
                    yield jsonData;
                  } catch (e) {
                    print(
                      '[ApiService] Skipping invalid JSON: $data, Error: $e',
                    );
                    // Skip invalid JSON lines
                    continue;
                  }
                } else if (line.isNotEmpty && !line.startsWith(':')) {
                  // Handle non-SSE format directly
                  try {
                    final jsonData = jsonDecode(line);
                    yield jsonData;
                  } catch (e) {
                    print(
                      '[ApiService] Skipping invalid JSON: $line, Error: $e',
                    );
                    // Skip invalid JSON lines
                    continue;
                  }
                }
              }
            } catch (e) {
              print('[ApiService] Error processing chunk: $e');
              throw Exception('Error processing stream: $e');
            }
          }
        } else {
          print('[ApiService] ERROR: Status ${response.statusCode}');
          throw Exception('Failed to load AI response: ${response.statusCode}');
        }
      } catch (e) {
        print('[ApiService] Network error: $e');
        throw Exception('Network error: $e');
      }
    } catch (e) {
      print('[ApiService] Fatal error in streamAIResponse: $e');
      throw Exception('Fatal error: $e');
    }
  }
}
