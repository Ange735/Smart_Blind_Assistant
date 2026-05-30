import 'package:flutter/foundation.dart';

class ApiConfig {
  static String get baseUrl {
    if (kIsWeb) {
      return "http://127.0.0.1:8000";
    } else {
      return "http://192.168.11.131:8000";
    }
  }
}