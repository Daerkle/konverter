# Konverter: PDF- und Bild-zu-Text-Konvertierung mit GUI

Dieses Projekt bietet eine benutzerfreundliche Streamlit-Oberfläche für die leistungsstarke Dokumentenkonvertierungsbibliothek `marker`. Es ermöglicht die Umwandlung von PDF- und verschiedenen Bilddateien in strukturierte Formate wie Markdown, HTML oder JSON. Dabei werden Textinhalte, Bilder, Tabellen, mathematische Formeln und mehr aus den Dokumenten extrahiert.

Diese Anwendung basiert auf dem Open-Source-Projekt [marker von VikParuchuri](https://github.com/VikParuchuri/marker) und erweitert es um eine interaktive GUI sowie zusätzliche Funktionen für den Download und die Benutzerführung.

## Features

*   **Vielseitige Konvertierung:** Wandelt PDF-, PNG-, JPG-, GIF-Dateien (und weitere über `marker` unterstützte Formate wie DOCX, PPTX, EPUB) in Markdown, HTML oder JSON um.
*   **Strukturierte Ausgabe:** Extrahiert Text, Bilder, Tabellen, Formeln und behält die Struktur des Dokuments bei.
*   **Interaktive Streamlit-GUI:** Einfach zu bedienende Weboberfläche für Upload, Konfiguration und Anzeige der Ergebnisse.
*   **Batch-Verarbeitung:** Möglichkeit, mehrere Dateien gleichzeitig hochzuladen und zu verarbeiten.
*   **Flexible Download-Optionen:**
    *   Markdown: Download als ZIP-Archiv mit der reinen Text-Markdown-Datei und einem separaten Ordner für alle extrahierten Bilder (mit relativen Pfaden im Markdown).
    *   JSON/HTML: Direkter Download der konvertierten Datei.
*   **Anpassbare Verarbeitung:** Optionen zur Verwendung von LLMs (falls konfiguriert), Erzwingung von OCR, Umgang mit vorhandenem OCR-Text und mehr.
*   **Integrierte Hilfestellungen:** Modals mit Anleitungen zur Installation, Performance-Optimierung und Fehlerbehebung direkt in der GUI.
*   **Deutsche Benutzeroberfläche.**

## Setup und Installation

Es gibt verschiedene Wege, diese Anwendung einzurichten:

### 1. Lokale Installation (macOS)

Detaillierte Schritte finden Sie in der Datei: [`INSTALL_MAC.md`](INSTALL_MAC.md)

Kurzübersicht:
1.  Stellen Sie sicher, dass Python 3.10+ und Git installiert sind.
2.  Klonen Sie dieses Repository:
    ```bash
    git clone https://github.com/Daerkle/konverter.git
    cd konverter
    ```
3.  Erstellen und aktivieren Sie eine virtuelle Umgebung:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
4.  Installieren Sie die Abhängigkeiten (inklusive `marker` und Streamlit):
    ```bash
    pip install --upgrade pip
    pip install -e .  # Für die marker-Basisinstallation
    pip install torch streamlit watchdog # Zusätzliche Abhängigkeiten für die GUI und Performance
    # Für Apple Silicon (MPS) wird PyTorch automatisch passend installiert.
    # Für Nvidia GPUs, installieren Sie PyTorch mit CUDA-Support gemäß https://pytorch.org/
    ```

### 2. Docker-Installation

Detaillierte Schritte und ein Beispiel-Dockerfile finden Sie in der Datei: [`INSTALL_DOCKER.md`](INSTALL_DOCKER.md)

### 3. Allgemeine Python-Installation (Andere Systeme)

Die Schritte ähneln der macOS-Installation. Stellen Sie sicher, dass die Systemvoraussetzungen für `marker` (insbesondere für PyTorch und ggf. CUDA für Nvidia-GPUs) erfüllt sind.

## Verwendung

1.  **Starten der Streamlit-GUI:**
    Nach der Installation und Aktivierung der virtuellen Umgebung (falls zutreffend), starten Sie die Anwendung mit:
    ```bash
    streamlit run marker/marker/scripts/streamlit_app.py
    ```
    (Stellen Sie sicher, dass Sie sich im Hauptverzeichnis des geklonten `konverter`-Repositorys befinden.)

2.  **GUI-Bedienung:**
    *   **Datei-Upload:** Wählen Sie eine oder mehrere Dateien über die Seitenleiste aus.
    *   **Seitenauswahl:** Geben Sie die zu verarbeitende Seite oder den Seitenbereich an.
    *   **Ausgabeformat:** Wählen Sie Markdown, JSON oder HTML.
    *   **Optionen:** Konfigurieren Sie weitere Verarbeitungsparameter wie LLM-Nutzung, OCR-Verhalten etc.
    *   **Verarbeiten:** Klicken Sie auf "Verarbeiten", um die Konvertierung zu starten.
    *   **Ergebnisansicht:** Das konvertierte Dokument wird im Hauptbereich angezeigt.
    *   **Download:** Nutzen Sie den Download-Button, um das Ergebnis im gewählten Format zu speichern.
    *   **Hilfe & Anleitungen:** Ein Button in der Hauptansicht öffnet ein Modal mit Links zu detaillierten Anleitungen für Installation, Performance und Fehlerbehebung.

## Konfiguration (Optional)

*   **LLM-Nutzung (z.B. Google Gemini):** Wenn Sie die LLM-basierten Features von `marker` nutzen möchten, müssen Sie möglicherweise API-Keys konfigurieren. Erstellen Sie dazu eine `.env`-Datei im Hauptverzeichnis des Projekts mit dem entsprechenden Inhalt, z.B.:
    ```
    gemini_api_key=DEIN_API_KEY_HIER
    ```
    Details dazu finden Sie auch in der `STREAMLIT_TROUBLESHOOTING.md`.

## Fehlerbehebung

Bei Problemen mit der Streamlit-Anwendung, insbesondere im Zusammenhang mit PyTorch oder Watchdog, konsultieren Sie bitte:
[`STREAMLIT_TROUBLESHOOTING.md`](STREAMLIT_TROUBLESHOOTING.md)

## Performance-Optimierung

Tipps zur Beschleunigung der Verarbeitung auf macOS (MPS) und Nvidia-GPUs finden Sie hier:
[`PERFORMANCE_TUNING.md`](PERFORMANCE_TUNING.md)

## Lizenz

Dieses Projekt basiert auf `marker` von VikParuchuri, welches unter der Apache 2.0 Lizenz veröffentlicht ist. Die hier vorgenommenen Anpassungen und die Streamlit-GUI stehen unter derselben Lizenz. Bitte beachten Sie die Lizenzbedingungen des Originalprojekts.

## Danksagung

Ein großer Dank geht an Vik Paruchuri und die Beitragenden des [marker-Projekts](https://github.com/VikParuchuri/marker) für die Bereitstellung dieser exzellenten Dokumentenkonvertierungsbibliothek.