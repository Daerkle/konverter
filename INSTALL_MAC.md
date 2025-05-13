# Installation von marker auf macOS

## Voraussetzungen

- Python 3.12+
- Git
- Xcode Command Line Tools (für Watchdog)

```bash
xcode-select --install
```

## Repository klonen

```bash
git clone https://github.com/VikParuchuri/marker.git
cd marker
```

## Virtuelle Umgebung anlegen und aktivieren

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Abhängigkeiten installieren

```bash
pip install --upgrade pip
pip install -e .
pip install torch streamlit watchdog
```

## Streamlit-GUI starten

```bash
streamlit run marker/scripts/streamlit_app.py