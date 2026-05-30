import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';

class ApiService {

  // 🆕 Timeout global pour tous les appels
  static const _timeout = Duration(seconds: 15);

  // ── Pipeline principal ───────────────────────────────────────────────
  static Future<Map<String, dynamic>> pipeline({
    required String phrase,
    required Uint8List imageBytes,
    String deviceId = "default",
    double? heading,
  }) async {
    var request = http.MultipartRequest(
      'POST', Uri.parse('${ApiConfig.baseUrl}/pipeline'),
    );
    request.fields['phrase']    = phrase;
    request.fields['device_id'] = deviceId;
    if (heading != null) request.fields['heading'] = heading.toString();
    request.files.add(http.MultipartFile.fromBytes('image', imageBytes, filename: 'frame.jpg'));

    // 🆕 Timeout sur l'envoi
    final response = await request.send().timeout(_timeout);
    final body     = await response.stream.bytesToString();
    return json.decode(body);
  }

  // ── Détection d'obstacles ────────────────────────────────────────────
  static Future<Map<String, dynamic>> detectObstacle(Uint8List imageBytes) async {
    var request = http.MultipartRequest(
      'POST', Uri.parse('${ApiConfig.baseUrl}/detect-obstacle'),
    );
    request.files.add(http.MultipartFile.fromBytes('image', imageBytes, filename: 'frame.jpg'));

    // 🆕 Timeout
    final response = await request.send().timeout(_timeout);
    final body     = await response.stream.bytesToString();
    return json.decode(body);
  }

  // 🆕 Annuler l'action en cours
  static Future<Map<String, dynamic>> cancel({
    String deviceId = "default",
  }) async {
    var request = http.MultipartRequest(
      'POST', Uri.parse('${ApiConfig.baseUrl}/cancel'),
    );
    request.fields['device_id'] = deviceId;

    final response = await request.send().timeout(_timeout);
    final body     = await response.stream.bytesToString();
    return json.decode(body);
  }
}