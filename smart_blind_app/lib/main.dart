import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  runApp(SmartBlindApp(cameras: cameras));
}

class SmartBlindApp extends StatelessWidget {
  final List<CameraDescription> cameras;
  const SmartBlindApp({super.key, required this.cameras});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Blind Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue)),
      home: HomeScreen(cameras: cameras),
    );
  }
}