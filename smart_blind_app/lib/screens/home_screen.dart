import 'dart:async';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:vibration/vibration.dart';
import '../services/api_service.dart';
import 'sos_screen.dart';

class HomeScreen extends StatefulWidget {
  final List<CameraDescription> cameras;
  const HomeScreen({super.key, required this.cameras});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late CameraController _camera;
  final FlutterTts   _tts = FlutterTts();
  final SpeechToText _stt = SpeechToText();

  static const _locale        = "fr_FR";
  static const _ttsLocale     = "fr-FR";
  static const _obstacleDelay = Duration(seconds: 5);
  static const _listenFor     = Duration(seconds: 10);
  static const _pauseFor      = Duration(seconds: 3);
  static const _sttTimeout    = Duration(seconds: 12);

  // 🆕 Mots-clés d'annulation (cohérents avec le backend)
  static const _cancelKeywords = ["stop", "annuler", "arrête", "arreter", "stopper", "quitter", "terminer"];

  String _mode         = "normal";
  String _lastMessage  = "Système prêt";
  bool   _listening    = false;
  bool   _ttsPlaying   = false;
  bool   _sttReady     = false;
  bool   _pipelineBusy = false;

  Timer? _obstacleTimer;
  Timer? _loopTimer;
  Timer? _sttTimeoutTimer;

  @override
  void initState() {
    super.initState();
    _initCamera();
    _initTts();
    _initStt();
    _startObstacleDetection();
  }

  Future<void> _initCamera() async {
    try {
      _camera = CameraController(widget.cameras[0], ResolutionPreset.medium);
      await _camera.initialize();
      if (mounted) setState(() {});
    } catch (e) {
      await _speak("Accès caméra refusé. L'application ne peut pas fonctionner.", interrupt: true);
    }
  }

  Future<void> _initTts() async {
    await _tts.setLanguage(_ttsLocale);
    await _tts.setSpeechRate(0.45);
    await _tts.setPitch(1.0);
    await _tts.setVolume(1.0);

    final voices = await _tts.getVoices;
    final frVoice = (voices as List).firstWhere(
      (v) => v['locale'].toString().startsWith('fr'),
      orElse: () => null,
    );
    if (frVoice != null) {
      await _tts.setVoice({"name": frVoice['name'], "locale": frVoice['locale']});
    }

    _tts.setStartHandler(() { if (mounted) setState(() => _ttsPlaying = true); });
    _tts.setCompletionHandler(() { if (mounted) setState(() => _ttsPlaying = false); });
  }

  Future<void> _initStt() async {
    final available = await _stt.initialize(
      onError: (error) {
        debugPrint("STT error: $error");
        if (mounted) setState(() => _listening = false);
      },
      onStatus: (status) {
        debugPrint("STT status: $status");
        if (status == "done" || status == "notListening") {
          if (_listening && mounted) setState(() => _listening = false);
        }
      },
    );
    if (mounted) setState(() => _sttReady = available);
  }

  Future<void> _speak(String text, {bool interrupt = false}) async {
    if (interrupt) {
      await _tts.stop();
      if (mounted) setState(() => _ttsPlaying = false);
      await Future.delayed(const Duration(milliseconds: 100));
    } else {
      if (_ttsPlaying) return;
    }
    if (mounted) setState(() => _lastMessage = text);
    await _tts.speak(text);
  }

  Future<Uint8List?> _captureFrame() async {
    if (!_camera.value.isInitialized) return null;
    try {
      final xfile = await _camera.takePicture();
      return await xfile.readAsBytes();
    } catch (e) {
      return null;
    }
  }

  void _startObstacleDetection() {
    _obstacleTimer?.cancel();
    _obstacleTimer = Timer.periodic(_obstacleDelay, (_) async {
      if (_mode == "sos") return;
      if (_listening) return;
      if (_pipelineBusy) return;

      final frame = await _captureFrame();
      if (frame == null) return;

      try {
        final result    = await ApiService.detectObstacle(frame);
        final tts       = result['tts_message'];
        final interrupt = result['interrupt'] ?? false;
        final priorite  = result['priorite'] ?? 0;

        if (tts == null) return;

        if (interrupt || priorite >= 4) {
          await _speak(tts, interrupt: true);
          return;
        }

        if (_mode == "normal" && !_ttsPlaying) {
          await _speak(tts);
        }
      } catch (_) {}
    });
  }

  void _stopObstacleDetection() => _obstacleTimer?.cancel();
  void _resumeObstacleDetection() => _startObstacleDetection();

  // 🆕 Annulation via appui long ou commande vocale
  Future<void> _cancelCurrentAction() async {
    if (_mode == "normal") return;

    _loopTimer?.cancel();
    _pipelineBusy = false;

    try {
      final result = await ApiService.cancel(deviceId: "default");
      final tts    = result['tts_message'] ?? "Action annulée.";
      await _speak(tts, interrupt: true);
    } catch (_) {
      await _speak("Action annulée.", interrupt: true);
    }

    if (mounted) setState(() => _mode = "normal");
    _resumeObstacleDetection();
  }

  Future<void> _listen() async {
    if (_listening) return;
    if (!_sttReady) {
      await _speak("Microphone non disponible", interrupt: true);
      return;
    }

    if (_stt.isListening) {
      await _stt.stop();
      await Future.delayed(const Duration(milliseconds: 500));
    }

    await _tts.stop();
    if (mounted) setState(() { _ttsPlaying = false; _listening = true; });

    await _speak("Je vous écoute");

    await Future.doWhile(() async {
      await Future.delayed(const Duration(milliseconds: 100));
      return _ttsPlaying;
    });

    await Future.delayed(const Duration(milliseconds: 300));

    await _stt.listen(
      localeId: _locale,
      listenFor: _listenFor,
      pauseFor: _pauseFor,
      onResult: (result) async {
        if (!result.finalResult) return;
        final phrase = result.recognizedWords;

        _sttTimeoutTimer?.cancel();

        if (phrase.isEmpty) {
          if (mounted) setState(() => _listening = false);
          await _speak("Je n'ai rien entendu, réessayez.");
          return;
        }

        if (mounted) setState(() => _listening = false);

        // 🆕 Détection annulation vocale avant d'appeler le pipeline
        final phraseLower = phrase.toLowerCase().trim();
        if (_cancelKeywords.any((kw) => phraseLower.contains(kw)) && _mode != "normal") {
          await _cancelCurrentAction();
          return;
        }

        await _callPipeline(phrase);
      },
    );

    _sttTimeoutTimer?.cancel();
    _sttTimeoutTimer = Timer(_sttTimeout, () {
      if (_listening) {
        _stt.stop();
        if (mounted) setState(() => _listening = false);
      }
    });
  }

  Future<void> _callPipeline(String phrase) async {
    if (_pipelineBusy) return;
    _pipelineBusy = true;

    await _speak("Traitement en cours...", interrupt: true);

    final frame = await _captureFrame();
    if (frame == null) { _pipelineBusy = false; return; }

    try {
      final result = await ApiService.pipeline(phrase: phrase, imageBytes: frame);
      if (!mounted) { _pipelineBusy = false; return; }

      final action = result['action'] ?? {};
      final tts    = result['tts_message'] ?? "";

      await _speak(tts, interrupt: true);

      final newMode   = action['mode'] ?? "normal";
      final stopObs   = action['stop_obstacle'] ?? false;
      final loop      = action['loop'] ?? false;
      final interval  = action['loop_interval'] ?? 5;
      final vibration = action['vibration'] ?? "none";
      final emergency = action['show_emergency'] ?? false;

      if (mounted) setState(() => _mode = newMode);

      if (vibration == "strong") Vibration.vibrate(duration: 1000);

      if (emergency) {
        _pipelineBusy = false;
        if (mounted) Navigator.push(context, MaterialPageRoute(builder: (_) => const SosScreen()));
        return;
      }

      if (stopObs) _stopObstacleDetection();

      _loopTimer?.cancel();
      if (loop) {
        _loopTimer = Timer.periodic(Duration(seconds: interval), (_) async {
          if (_pipelineBusy) return;
          _pipelineBusy = true;

          final f = await _captureFrame();
          if (f == null) { _pipelineBusy = false; return; }

          try {
            final r   = await ApiService.pipeline(phrase: phrase, imageBytes: f);
            if (!mounted) { _pipelineBusy = false; return; }

            final a   = r['action'] ?? {};
            final msg = r['tts_message'] ?? "";

            await _speak(msg);

            // 🆕 Si le backend renvoie mode "normal" (objet trouvé ou annulé) → stop loop
            if ((a['mode'] ?? "normal") == "normal") {
              _loopTimer?.cancel();
              if (mounted) setState(() => _mode = "normal");
              _resumeObstacleDetection();
            }
          } catch (e) {
            await _speak("Erreur lors de la mise à jour.", interrupt: true);
          } finally {
            _pipelineBusy = false;
          }
        });
      } else {
        if (mounted) setState(() => _mode = "normal");
        _resumeObstacleDetection();
      }
    } catch (e) {
      final msg = e.toString().contains('timeout')
          ? "Délai dépassé, réessayez."
          : "Erreur de connexion au serveur.";
      await _speak(msg, interrupt: true);
    } finally {
      _pipelineBusy = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          if (_camera.value.isInitialized)
            Positioned.fill(child: CameraPreview(_camera)),

          Positioned.fill(child: Container(color: Colors.black.withOpacity(0.4))),

          Positioned(
            top: 50, left: 20, right: 20,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: _modeColor().withOpacity(0.8),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                _modeLabel(),
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),

          Positioned(
            bottom: 160, left: 20, right: 20,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.7),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _lastMessage,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 18),
              ),
            ),
          ),

          Positioned(
            bottom: 50, left: 0, right: 0,
            child: Center(
              // 🆕 Appui court = écouter / Appui long = annuler
              child: GestureDetector(
                onTap: _listen,
                onLongPress: _cancelCurrentAction,
                child: Container(
                  width: 90, height: 90,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _listening
                        ? Colors.red
                        : _pipelineBusy
                            ? Colors.orange
                            : _mode != "normal"
                                ? Colors.blue  // 🆕 bleu = action en cours, appui long pour annuler
                                : Colors.white,
                    boxShadow: [BoxShadow(color: Colors.white.withOpacity(0.3), blurRadius: 20, spreadRadius: 5)],
                  ),
                  child: Icon(
                    _listening
                        ? Icons.mic
                        : _mode != "normal"
                            ? Icons.stop  // 🆕 icône stop quand action en cours
                            : Icons.mic_none,
                    size: 45,
                    color: _listening || _mode != "normal" ? Colors.white : Colors.black,
                  ),
                ),
              ),
            ),
          ),

          // 🆕 Indicateur appui long quand une action est en cours
          if (_mode != "normal")
            Positioned(
              bottom: 145, left: 0, right: 0,
              child: Center(
                child: Text(
                  "Appui long pour annuler",
                  style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 13),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Color _modeColor() {
    switch (_mode) {
      case "find_object": return Colors.orange;
      case "navigate":    return Colors.blue;
      case "sos":         return Colors.red;
      default:            return Colors.green;
    }
  }

  String _modeLabel() {
    switch (_mode) {
      case "find_object": return "🔍 Recherche d'objet en cours...";
      case "navigate":    return "🧭 Navigation en cours...";
      case "sos":         return "🚨 SOS déclenché";
      default:            return "✅ Surveillance active";
    }
  }

  @override
  void dispose() {
    _obstacleTimer?.cancel();
    _loopTimer?.cancel();
    _sttTimeoutTimer?.cancel();
    _camera.dispose();
    _tts.stop();
    super.dispose();
  }
}