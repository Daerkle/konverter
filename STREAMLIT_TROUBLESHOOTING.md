# Fehlerbehebung: Streamlit + marker + PyTorch (macOS)

## Typische Probleme

### 1. Watchdog-Warnung erscheint trotz Installation

- Ursache: Streamlit erkennt Watchdog manchmal nicht korrekt, besonders bei mehreren Python-Installationen oder venv-Problemen.
- Lösung: Stelle sicher, dass du die virtuelle Umgebung aktiviert hast, bevor du `pip install watchdog` ausführst.

### 2. Fehler mit torch.classes / __path__._path

**Fehlermeldung:**
```
RuntimeError: Tried to instantiate class '__path__._path', but it does not exist! Ensure that it is registered via torch::class_
```
- Ursache: Inkompatibilität zwischen Streamlit, PyTorch und Watchdog auf macOS (meist bei MPS/GPU).
- Workarounds:
  - Nutze PyTorch nur auf CPU (setze Umgebungsvariable: `export PYTORCH_ENABLE_MPS_FALLBACK=1`)
  - Downgrade Streamlit auf eine ältere Version (z.B. 1.32)
  - Downgrade PyTorch auf eine ältere Version (z.B. 2.2)
  - Starte Streamlit mit dem Parameter `--server.fileWatcherType=none`:
    ```bash
    streamlit run marker/scripts/streamlit_app.py --server.fileWatcherType=none
    ```
  - Prüfe, ob alle Pakete in der gleichen venv installiert sind.

### 3. Doppelte CLI-Parameter-Warnungen

- Ursache: marker definiert manche CLI-Parameter mehrfach.
- Lösung: Kann meist ignoriert werden, sollte aber im Code bereinigt werden.

### 4. AssertionError: GoogleGeminiService benötigt API-Key

**Fehlermeldung:**
```
AssertionError: In order to use GoogleGeminiService, you must set the configuration values `gemini_api_key, `.
```
- Ursache: Es fehlt der Google Gemini API-Key in der Konfiguration.
- Lösung: Lege eine Datei `.env` im Projektverzeichnis an und trage dort deinen Key ein:
  ```
  gemini_api_key=DEIN_API_KEY
  ```
  oder setze die Variable als Umgebungsvariable:
  ```bash
  export gemini_api_key=DEIN_API_KEY
  ```

---

## Empfehlung

Falls die Fehler weiterhin auftreten, versuche:
- Streamlit mit deaktiviertem FileWatcher zu starten.
- PyTorch auf CPU zu zwingen.
- Die Pakete in einer frischen venv zu installieren.
- API-Keys in `.env` oder als Umgebungsvariable zu setzen.