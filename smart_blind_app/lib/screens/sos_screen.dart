import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';

class SosScreen extends StatefulWidget {
  const SosScreen({super.key});
  @override
  State<SosScreen> createState() => _SosScreenState();
}

class _SosScreenState extends State<SosScreen> {
  final FlutterTts _tts = FlutterTts();

  @override
  void initState() {
    super.initState();
    _tts.setLanguage("fr-FR");
    _tts.speak("SOS déclenché. Les secours ont été alertés. Restez en ligne.");
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.red,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.emergency, color: Colors.white, size: 100),
            const SizedBox(height: 30),
            const Text("SOS DÉCLENCHÉ",
              style: TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            const Text("Les secours ont été alertés",
              style: TextStyle(color: Colors.white, fontSize: 18)),
            const SizedBox(height: 60),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.white),
              onPressed: () => Navigator.pop(context),
              child: const Text("Annuler", style: TextStyle(color: Colors.red, fontSize: 18)),
            )
          ],
        ),
      ),
    );
  }
}