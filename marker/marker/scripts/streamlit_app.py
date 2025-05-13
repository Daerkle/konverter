import os
import sys
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["IN_STREAMLIT"] = "true"

from marker.settings import settings
from marker.config.printer import CustomClickPrinter
from streamlit.runtime.uploaded_file_manager import UploadedFile

import base64
import io
import json
import re
import string
import tempfile
import zipfile # Neu für ZIP-Export
from typing import Any, Dict
import click

import pypdfium2
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered
from marker.schema import BlockTypes

COLORS = [
    "#4e79a7",
    "#f28e2c",
    "#e15759",
    "#76b7b2",
    "#59a14f",
    "#edc949",
    "#af7aa1",
    "#ff9da7",
    "#9c755f",
    "#bab0ab"
]

with open(
    os.path.join(os.path.dirname(__file__), "streamlit_app_blocks_viz.html"), encoding="utf-8"
) as f:
    BLOCKS_VIZ_TMPL = string.Template(f.read())


@st.cache_data()
def parse_args():
    # Use to grab common cli options
    @ConfigParser.common_options
    def options_func():
        pass

    def extract_click_params(decorated_function):
        if hasattr(decorated_function, '__click_params__'):
            return decorated_function.__click_params__
        return []

    cmd = CustomClickPrinter("Marker app.")
    extracted_params = extract_click_params(options_func)
    cmd.params.extend(extracted_params)
    ctx = click.Context(cmd)
    try:
        cmd_args = sys.argv[1:]
        cmd.parse_args(ctx, cmd_args)
        return ctx.params
    except click.exceptions.ClickException as e:
        return {"error": str(e)}

@st.cache_resource()
def load_models():
    return create_model_dict()


def convert_pdf(fname: str, config_parser: ConfigParser) -> (str, Dict[str, Any], dict):
    config_dict = config_parser.generate_config_dict()
    config_dict["pdftext_workers"] = 1
    converter_cls = PdfConverter
    converter = converter_cls(
        config=config_dict,
        artifact_dict=model_dict,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service()
    )
    return converter(fname)


def open_pdf(pdf_file):
    stream = io.BytesIO(pdf_file.getvalue())
    return pypdfium2.PdfDocument(stream)


def img_to_html(img, img_alt):
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=settings.OUTPUT_IMAGE_FORMAT)
    img_bytes = img_bytes.getvalue()
    encoded = base64.b64encode(img_bytes).decode()
    img_html = f'<img src="data:image/{settings.OUTPUT_IMAGE_FORMAT.lower()};base64,{encoded}" alt="{img_alt}" style="max-width: 100%;">'
    return img_html


def create_markdown_with_relative_image_paths(markdown_text: str, images: Dict[str, Image.Image], image_folder_name="images"):
    """
    Ersetzt Bild-Tags im Markdown durch relative Pfade und gibt die modifizierte Markdown-Datei
    sowie ein Dictionary mit Bildnamen und PIL-Bildobjekten für den separaten Export zurück.
    """
    updated_markdown = markdown_text
    image_files_for_zip = {} # Speichert {relativer_pfad_im_zip: PIL.Image}

    # Regex, um Markdown-Bild-Tags zu finden: ![alt text](path/to/image.jpg "Optional title")
    # Wir interessieren uns für den Pfad.
    image_tags = re.findall(r'(!\[(?P<alt_text>[^\]]*)\]\((?P<original_path>[^\)\s]+)(?:\s*\"(?P<title>[^\"]*)\")?\))', markdown_text)

    for full_tag, alt_text, original_path, title in image_tags:
        if original_path in images:
            pil_image = images[original_path]
            # Erzeuge einen sicheren Dateinamen für das Bild
            # original_path könnte z.B. "_page_1_Figure_0.jpeg" sein
            base_name = os.path.basename(original_path)
            # Stelle sicher, dass der Dateiname eindeutig ist, falls mehrere Seiten gleiche Bildnamen haben
            # (obwohl marker das normalerweise schon handhabt)
            relative_image_path_in_zip = os.path.join(image_folder_name, base_name)

            # Ersetze den alten Tag durch einen neuen mit relativem Pfad
            new_image_tag = f"![{alt_text}]({relative_image_path_in_zip})"
            if title:
                new_image_tag = f"![{alt_text}]({relative_image_path_in_zip} \"{title}\")"
            
            updated_markdown = updated_markdown.replace(full_tag, new_image_tag)
            image_files_for_zip[relative_image_path_in_zip] = pil_image
            
    return updated_markdown, image_files_for_zip

def embed_images_for_display(markdown_text: str, images: Dict[str, Image.Image]):
    """
    Ersetzt Bild-Tags im Markdown durch eingebettete Base64-Bilder für die GUI-Anzeige.
    Nutzt die vorhandene img_to_html Funktion.
    """
    updated_markdown = markdown_text
    # Regex, um Markdown-Bild-Tags zu finden: ![alt text](path/to/image.jpg "Optional title")
    image_tags = re.findall(r'(!\[(?P<alt_text>[^\]]*)\]\((?P<original_path>[^\)\s]+)(?:\s*\"(?P<title>[^\"]*)\")?\))', markdown_text)

    for full_tag, alt_text, original_path, title in image_tags:
        if original_path in images:
            pil_image = images[original_path]
            # Erzeuge HTML für das eingebettete Bild
            html_image_tag = img_to_html(pil_image, alt_text) # img_to_html kümmert sich um Base64
            updated_markdown = updated_markdown.replace(full_tag, html_image_tag)
            
    return updated_markdown

@st.cache_data()
def get_page_image(pdf_file, page_num, dpi=96):
    if "pdf" in pdf_file.type:
        doc = open_pdf(pdf_file)
        page = doc[page_num]
        png_image = page.render(
            scale=dpi / 72,
        ).to_pil().convert("RGB")
    else:
        png_image = Image.open(pdf_file).convert("RGB")
    return png_image


@st.cache_data()
def page_count(pdf_file: UploadedFile):
    if "pdf" in pdf_file.type:
        doc = open_pdf(pdf_file)
        return len(doc) - 1
    else:
        return 1


def pillow_image_to_base64_string(img: Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def block_display(image: Image, blocks: dict | None = None, dpi=96):
    if blocks is None:
        blocks = {}

    image_data_url = (
        'data:image/jpeg;base64,' + pillow_image_to_base64_string(image)
    )

    template_values = {
        "image_data_url": image_data_url,
        "image_width": image.width, "image_height": image.height,
        "blocks_json": blocks, "colors_json": json.dumps(COLORS),
        "block_types_json": json.dumps({
            bt.name: i for i, bt in enumerate(BlockTypes)
        })
    }
    return components.html(
        BLOCKS_VIZ_TMPL.substitute(**template_values),
        height=image.height
    )


st.set_page_config(layout="wide")
col1, col2 = st.columns([.5, .5])

model_dict = load_models()
cli_options = parse_args()


st.markdown("""
# PDF- und Bildkonvertierung

Diese Anwendung demonstriert die Umwandlung von PDF- und Bilddateien in strukturierte Formate wie Markdown, HTML oder JSON.
Es werden Textinhalte, Bilder, Tabellen, Formeln und mehr aus Ihren Dokumenten erkannt und extrahiert.
""")

# Inhalte der Markdown-Dateien laden (sollte idealerweise nur einmal am Anfang des Skripts geschehen)
# und Fehlerbehandlung für fehlende Dateien hinzufügen.
# Für dieses Beispiel gehen wir davon aus, dass die Dateien existieren.
@st.cache_data # Cache, um Dateien nicht bei jedem Klick neu zu laden
def load_markdown_files():
    files_content = {}
    md_files_info = {
        "performance": {"path": "PERFORMANCE_TUNING.md", "title": "Performance-Optimierung"},
        "install_mac": {"path": "INSTALL_MAC.md", "title": "macOS Installation"},
        "install_docker": {"path": "INSTALL_DOCKER.md", "title": "Docker Installation"},
        "troubleshooting": {"path": "STREAMLIT_TROUBLESHOOTING.md", "title": "Fehlerbehebung (Streamlit)"}
    }
    for key, info in md_files_info.items():
        try:
            # Pfad relativ zum Hauptverzeichnis des Projekts (wo die .md Dateien liegen)
            # Das Skript ist in marker/marker/scripts/streamlit_app.py
            # Also müssen wir drei Ebenen hoch: ../../../
            file_path = os.path.join(os.path.dirname(__file__), "../../../", info["path"])
            with open(file_path, "r", encoding="utf-8") as f:
                files_content[key] = {"content": f.read(), "title": info["title"]}
        except FileNotFoundError:
            files_content[key] = {"content": f"Fehler: Datei {info['path']} nicht gefunden.", "title": info["title"]}
    return files_content

markdown_docs = load_markdown_files()

if 'active_modal' not in st.session_state:
    st.session_state.active_modal = None

def open_doc_modal(doc_key):
    st.session_state.active_modal = doc_key

# Haupt-Button für Hilfe
if st.button("Hilfe & Anleitungen"):
    st.session_state.active_modal = "main_help"

# Haupt-Hilfe-Modal
if st.session_state.active_modal == "main_help":
    # st.dialog wird als Funktion aufgerufen, nicht als Context Manager
    # Der Inhalt wird innerhalb des if-Blocks gerendert, wenn der Dialog aktiv ist.
    # Streamlit behandelt das Anzeigen des Dialogs basierend auf dem ersten Aufruf von st.dialog in einem Skriptlauf.
    # Um den Dialog zu "öffnen", setzen wir den state und Streamlit rendert ihn beim nächsten Durchlauf.
    # Der Dialog selbst muss dann die Buttons zum Schließen oder Navigieren enthalten.
    
    # Da st.dialog() bei jedem Skriptlauf aufgerufen wird, wenn der State gesetzt ist,
    # müssen wir die Logik für die Buttons *innerhalb* des Dialogs platzieren.
    # Streamlit's st.dialog ist so konzipiert, dass es den Rest des Skripts anhält, bis es geschlossen wird.
    # Die Buttons im Dialog steuern dann den `st.session_state.active_modal`.

    # Korrekte Verwendung von st.dialog:
    # Es wird einmal aufgerufen, wenn es angezeigt werden soll.
    # Die Interaktion geschieht dann innerhalb des Dialogs.
    # Korrekte Verwendung von st.dialog:
    # Der Aufruf von st.dialog() öffnet den Dialog.
    # Alle nachfolgenden st-Elemente werden innerhalb dieses Dialogs gerendert,
    # bis der Dialog durch eine Aktion (z.B. Button-Klick, der den State ändert) geschlossen wird
    # und bei einem st.rerun() nicht mehr aufgerufen wird.
    st.dialog("Hilfe & Anleitungen", width="medium") # Dieser Aufruf öffnet den Dialog-Kontext
    
    st.write("Wählen Sie ein Thema aus, um detaillierte Informationen anzuzeigen:")
    if st.button(markdown_docs["performance"]["title"], key="perf_btn_main_modal_dialog_content"):
        st.session_state.active_modal = "performance"
        st.rerun()
    if st.button(markdown_docs["install_mac"]["title"], key="mac_btn_main_modal_dialog_content"):
        st.session_state.active_modal = "install_mac"
        st.rerun()
    if st.button(markdown_docs["install_docker"]["title"], key="docker_btn_main_modal_dialog_content"):
        st.session_state.active_modal = "install_docker"
        st.rerun()
    if st.button(markdown_docs["troubleshooting"]["title"], key="trouble_btn_main_modal_dialog_content"):
        st.session_state.active_modal = "troubleshooting"
        st.rerun()
    
    if st.button("Schließen", key="close_main_help_dialog_content"):
        st.session_state.active_modal = None
        st.rerun()


# Detail-Modals
elif st.session_state.active_modal in markdown_docs:
    doc_info = markdown_docs[st.session_state.active_modal]
    st.dialog(doc_info["title"], width="large") # Öffnet den Dialog-Kontext für das Detail-Modal
    
    st.markdown(doc_info["content"], unsafe_allow_html=True)
    if st.button("Zurück zur Übersicht", key=f"close_detail_{st.session_state.active_modal}_dialog_content"):
        st.session_state.active_modal = "main_help"
        st.rerun()
    if st.button("Ganz schließen", key=f"fully_close_detail_{st.session_state.active_modal}_dialog_content"):
        st.session_state.active_modal = None
        st.rerun()

in_files = st.sidebar.file_uploader(
    "PDF-, Dokument- oder Bilddatei(en) auswählen:",
    type=["pdf", "png", "jpg", "jpeg", "gif", "pptx", "docx", "xlsx", "html", "epub"],
    accept_multiple_files=True,
    key="marker_file_upload_main"  # Eindeutiger Key
)

if not in_files:
    st.stop()

for in_file in in_files:
    st.markdown(f"### Datei: {in_file.name}")

    filetype = in_file.type

    with col1:
        seiten_anzahl = page_count(in_file)
        seiten_nummer = st.number_input(
            f"Seitenzahl (0 bis {seiten_anzahl}):",
            min_value=0, value=0, max_value=seiten_anzahl, key=f"page_{in_file.name}"
        )
        pil_image = get_page_image(in_file, seiten_nummer)
        image_placeholder = st.empty()

        with image_placeholder:
            block_display(pil_image)


seiten_bereich = st.sidebar.text_input(
    "Seitenbereich (z.B. 0,5-10,20)", value=f"{seiten_nummer}-{seiten_nummer}"
)
ausgabe_format = st.sidebar.selectbox(
    "Ausgabeformat", ["markdown", "json", "html"], index=0
)
starte_marker = st.sidebar.button("Verarbeiten")

nutze_llm = st.sidebar.checkbox(
    "LLM verwenden", help="LLM für höhere Qualität nutzen", value=False
)
zeige_bloecke = st.sidebar.checkbox(
    "Blöcke anzeigen", help="Erkannte Blöcke anzeigen (nur bei JSON-Ausgabe)", value=False, disabled=ausgabe_format != "json"
)
erzwinge_ocr = st.sidebar.checkbox(
    "OCR erzwingen", help="OCR für alle Seiten erzwingen", value=False
)
entferne_ocr = st.sidebar.checkbox(
    "Vorhandene OCR entfernen", help="OCR-Text aus PDF entfernen und neu erkennen", value=False
)
debug = st.sidebar.checkbox(
    "Debug-Modus", help="Zeige Debug-Informationen", value=False
)

# Entferne die alten Buttons aus der Seitenleiste, falls sie dort waren.
# Der neue Mechanismus ist oben implementiert.

if not starte_marker:
    st.stop()

# Run Marker
with tempfile.TemporaryDirectory() as tmp_dir:
    temp_pdf = os.path.join(tmp_dir, 'temp.pdf')
    with open(temp_pdf, 'wb') as f:
        f.write(in_file.getvalue())
    
    cli_options.update({
        "output_format": ausgabe_format,
        "page_range": seiten_bereich,
        "force_ocr": erzwinge_ocr,
        "debug": debug,
        "output_dir": settings.DEBUG_DATA_FOLDER if debug else None,
        "use_llm": nutze_llm,
        "strip_existing_ocr": entferne_ocr
    })
    config_parser = ConfigParser(cli_options)
    rendered = convert_pdf(
        temp_pdf,
        config_parser
    )
    page_range_val = config_parser.generate_config_dict()["page_range"]
    first_page = page_range_val[0] if page_range_val else 0

text, ext, images = text_from_rendered(rendered)
with col2:
    if ausgabe_format == "markdown":
        # Erzeuge Markdown mit relativen Pfaden und sammle Bilder für ZIP
        markdown_content, images_for_zip = create_markdown_with_relative_image_paths(text, images, image_folder_name=f"{os.path.splitext(in_file.name)[0]}_images")
        
        # Zeige Markdown im GUI (hier könnten wir auch die Base64-Version für die Anzeige behalten, wenn gewünscht)
        # Für die Anzeige im GUI werden Bilder weiterhin eingebettet, damit sie direkt sichtbar sind.
        display_text_with_embedded_images = embed_images_for_display(text, images) # Neue Funktion für GUI-Anzeige
        st.markdown(display_text_with_embedded_images, unsafe_allow_html=True)

        # ZIP-Datei im Speicher erstellen
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # Markdown-Datei zum ZIP hinzufügen
            zip_file.writestr(f"{os.path.splitext(in_file.name)[0]}_marker.md", markdown_content.encode("utf-8"))
            # Bilder zum ZIP hinzufügen (im Unterordner)
            for image_path_in_zip, pil_image in images_for_zip.items():
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format=pil_image.format or settings.OUTPUT_IMAGE_FORMAT) # Format beibehalten oder Standard
                img_byte_arr = img_byte_arr.getvalue()
                zip_file.writestr(image_path_in_zip, img_byte_arr)
        
        st.download_button(
            label="Markdown + Bilder (ZIP) herunterladen",
            data=zip_buffer.getvalue(),
            file_name=f"{os.path.splitext(in_file.name)[0]}_marker_with_images.zip",
            mime="application/zip"
        )
    elif ausgabe_format == "json":
        st.json(text)
        st.download_button(
            label="JSON herunterladen",
            data=text,
            file_name=f"{in_file.name}_marker.json",
            mime="application/json"
        )
    elif ausgabe_format == "html":
        st.html(text)
        st.download_button(
            label="HTML herunterladen",
            data=text,
            file_name=f"{in_file.name}_marker.html",
            mime="text/html"
        )

if ausgabe_format == "json" and zeige_bloecke:
    with image_placeholder:
        block_display(pil_image, text)

if debug:
    with col1:
        debug_data_path = rendered.metadata.get("debug_data_path")
        if debug_data_path:
            pdf_image_path = os.path.join(debug_data_path, f"pdf_page_{first_page}.png")
            img = Image.open(pdf_image_path)
            st.image(img, caption="PDF-Debug-Bild", use_container_width=True)
            layout_image_path = os.path.join(debug_data_path, f"layout_page_{first_page}.png")
            img = Image.open(layout_image_path)
            st.image(img, caption="Layout-Debug-Bild", use_container_width=True)
        st.write("Rohdaten-Ausgabe:")
        st.code(text, language=ausgabe_format)
