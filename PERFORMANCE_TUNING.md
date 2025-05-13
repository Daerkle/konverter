# Performance-Optimierung für marker

`marker` nutzt mehrere Machine-Learning-Modelle, deren Geschwindigkeit von Hardware, Softwarekonfiguration und den spezifischen Einstellungen abhängt. Hier sind einige Ansätze zur Beschleunigung der Verarbeitung:

## 1. Hardware-Beschleunigung nutzen

Stelle sicher, dass PyTorch die verfügbare Hardware-Beschleunigung korrekt nutzt.

### Für macOS (Apple Silicon mit MPS - Metal Performance Shaders)
- **PyTorch-Version:** Verwende eine aktuelle PyTorch-Version, da die MPS-Unterstützung kontinuierlich verbessert wird.
- **Datentyp:** `marker` verwendet bereits `torch.float16` für MPS im Streamlit-Skript, was die Geschwindigkeit erhöhen kann.
  ```python
  # Beispiel aus marker Code (vereinfacht)
  # model.to("mps", dtype=torch.float16)
  ```
- **Umgebungsvariable (Fallback):** Die Variable `PYTORCH_ENABLE_MPS_FALLBACK=1` ist im Streamlit-Skript gesetzt. Dies ist eher ein Kompatibilitäts-Fallback und nicht primär für Performance. Für reine Performance-Tests auf MPS kann man versuchen, diesen Fallback zu deaktivieren, falls alle Operationen nativ auf MPS laufen.

### Für Nvidia GPUs (CUDA)
- **CUDA und cuDNN:** Installiere die passenden Versionen von CUDA Toolkit und cuDNN für deine GPU und PyTorch-Version.
- **PyTorch mit CUDA:** Stelle sicher, dass du eine PyTorch-Version mit CUDA-Unterstützung installiert hast (z.B. von der offiziellen PyTorch-Website die passende Installationsanweisung auswählen).
- **Geräteauswahl:** Sorge dafür, dass PyTorch die CUDA-GPU verwendet:
  ```python
  # device = "cuda" if torch.cuda.is_available() else "cpu"
  # model.to(device)
  ```
- **Mixed Precision (AMP):** Verwende `torch.cuda.amp` für Automatic Mixed Precision, um die Geschwindigkeit mit Tensor Cores zu erhöhen, falls deine GPU dies unterstützt.
- **`torch.compile()` (PyTorch 2.0+):** Kann Modelle signifikant beschleunigen.
  ```python
  # model = torch.compile(model) # Vor der Inferenz
  ```

## 2. Batch-Größen anpassen
- Die internen Modelle von `marker` verarbeiten Daten in Batches. Die optimale Batch-Größe hängt vom Modell, der GPU-Speicherkapazität und der spezifischen Aufgabe ab.
- Größere Batch-Größen können die GPU-Auslastung verbessern, benötigen aber mehr Speicher.
- Kleinere Batch-Größen können bei Speicherknappheit helfen oder manchmal auf MPS besser funktionieren.
- Die Anpassung der Batch-Größen erfordert Änderungen im `marker`-Quellcode, da diese oft fest codiert oder über interne Konfigurationen gesteuert werden.

## 3. Modell-spezifische Optimierungen
- `marker` verwendet verschiedene Modelle (Layout-Erkennung, OCR, Tabellen-Erkennung etc.).
- **Leichtere Modelle:** Falls verfügbar oder konfigurierbar, könnten kleinere Varianten dieser Modelle schneller sein, eventuell mit geringfügigen Genauigkeitseinbußen.
- **ONNX / TensorRT:** Für maximale Inferenzgeschwindigkeit auf Nvidia-GPUs können Modelle nach ONNX exportiert und dann mit TensorRT optimiert werden. Dies ist ein fortgeschrittener Schritt und erfordert Anpassungen.

## 4. Software und Abhängigkeiten
- **Aktuelle Versionen:** Halte `marker`, PyTorch und andere relevante Bibliotheken aktuell.
- **Python-Version:** Neuere Python-Versionen können manchmal leichte Performance-Verbesserungen bringen.
- **Betriebssystem-Optimierungen:** Stelle sicher, dass dein Betriebssystem und die Treiber aktuell sind.

## 5. Verarbeitungsparameter von `marker`
- **`--use_llm`:** Die Verwendung eines LLM (wie über die Option `--use_llm` oder die entsprechende Einstellung im GUI) kann die Verarbeitung erheblich verlangsamen, da dies oft API-Aufrufe zu externen Diensten oder die Ausführung großer lokaler Modelle beinhaltet. Deaktiviere diese Option, wenn Geschwindigkeit kritisch ist und die LLM-Verbesserungen nicht zwingend benötigt werden.
- **`pdftext_workers`:** Im Streamlit-Skript ist `config_dict["pdftext_workers"] = 1` gesetzt. Für die PDF-Vorverarbeitung (Text-Extraktion) könnte eine Erhöhung dieser Zahl (z.B. auf die Anzahl der CPU-Kerne) die Geschwindigkeit verbessern, wenn die CPU der Engpass ist. Dies betrifft aber nicht die GPU-beschleunigten Modellinferenzen.
  ```python
  # In marker/scripts/streamlit_app.py, Funktion convert_pdf:
  # config_dict["pdftext_workers"] = os.cpu_count() # Beispiel für Nutzung aller CPU-Kerne
  ```
- **Seitenbereich:** Verarbeite nur die notwendigen Seiten, um die Gesamtzeit zu reduzieren.

## 6. Profiling
- Um spezifische Engpässe zu finden:
  - **Python Profiler:** `cProfile` kann helfen, langsame Python-Funktionen zu identifizieren.
  - **PyTorch Profiler:** `torch.profiler` liefert detaillierte Informationen über die Ausführungszeiten von GPU-Operationen.

## Fazit
Fine-Tuning für maximale Geschwindigkeit ist oft ein iterativer Prozess:
1. Stelle sicher, dass die GPU-Beschleunigung (MPS oder CUDA) aktiv ist.
2. Beginne mit den Standardeinstellungen von `marker`.
3. Deaktiviere rechenintensive Optionen wie LLM-Nutzung, wenn nicht unbedingt nötig.
4. Experimentiere mit Parametern wie `pdftext_workers`.
5. Für tiefgreifendere Optimierungen (Batch-Größen, `torch.compile`, AMP, ONNX) sind Änderungen am `marker`-Quellcode notwendig und erfordern ein gutes Verständnis der internen Modellarchitekturen.

Die spezifischen "richtigen" Einstellungen hängen stark von deiner Hardware und den zu verarbeitenden Dokumenten ab.