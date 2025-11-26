import re
from pathlib import Path
import argparse

# Definiere die Video-Dateierweiterungen
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'}

# Regex zum Extrahieren des Basenamens nach der letzten ']'
BASE_NAME_REGEX = re.compile(r'.*\]([^.]*)', re.IGNORECASE)

# Liste der ausgeschlossenen Release-Gruppen
EXCLUDED_GROUPS = {"yts.mx", "yts.lt"}

def extract_base_name(filename: str) -> str:
    """
    Extrahiert den Basenamen einer Datei basierend auf dem Regex.
    """
    match = BASE_NAME_REGEX.search(filename)
    if match:
        base = match.group(0)
        if base:
            return base.lower()
    else:
        return None

def find_files(root: Path, extensions: set) -> list:
    """
    Findet alle Dateien mit den angegebenen Erweiterungen rekursiv im Verzeichnis.
    """
    return [file for file in root.rglob('*') if file.is_file() and file.suffix.lower() in extensions]

def validate_srt(srt_filename: str, basename: str) -> bool:
    """
    Überprüft, ob die .srt-Datei gültig ist:
    - Der Dateiname muss exakt mit dem Basenamen beginnen.
    - Sprachendungen wie `.en.srt` oder `.en.hi.srt` werden berücksichtigt.
    """
    if not basename:
        return True

    # Normalisiere Basename und SRT-Name
    srt_filename = srt_filename.lower()

    # Überprüfen, ob der Release-Group-Teil in den Ausschlüssen enthalten ist
    if any(group in srt_filename for group in EXCLUDED_GROUPS):
        return True

    # Dynamischer Regex für Basename mit optionaler Sprachkennung
    pattern = re.compile(rf'{re.escape(basename)}(\.[a-zA-Z]{{2}}(\.hi)?)?\.srt$', re.IGNORECASE)

    if srt_filename == f"{basename}.srt":
        return False
    elif srt_filename == f"{basename}.hi.srt":
        return False

    return bool(pattern.search(srt_filename))

def main():
    parser = argparse.ArgumentParser(description="Verwalte .srt-Dateien basierend auf Videodateien.")
    parser.add_argument('directory', type=str, help="Pfad zum Zielverzeichnis")
    parser.add_argument('--remove-invalid', action='store_true', help="Entfernt ungültige .srt-Dateien")
    parser.add_argument('--remove-orphan', action='store_true', help="Entfernt verwaiste .srt-Dateien")
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.is_dir():
        print(f"Der angegebene Pfad ist kein Verzeichnis: {root}")
        return

    print(f"Durchsuche Verzeichnis: {root}")

    # Finde alle Videodateien und extrahiere ihre Basenamen
    video_files = find_files(root, VIDEO_EXTENSIONS)
    print(f"Gefundene Videodateien: {len(video_files)}")
    video_basenames = set()
    for video in video_files:
        base = extract_base_name(video.name)
        if base:
            video_basenames.add(base)

    # Finde alle .srt-Dateien
    srt_files = find_files(root, {'.srt'})
    print(f"Gefundene .srt-Dateien: {len(srt_files)}")

    # Listen für ungültige und verwaiste .srt-Dateien
    invalid_srt_files = []
    orphan_srt_files = []

    for srt in srt_files:
        base = extract_base_name(srt.name)
        if not validate_srt(srt.name, base):
            invalid_srt_files.append(srt)
        elif base and base not in video_basenames:
            orphan_srt_files.append(srt)

    if invalid_srt_files:
        print("\nListe der ungültigen .srt-Dateien:")
        for invalid_file in invalid_srt_files:
            print(invalid_file)
        print(f"{len(invalid_srt_files)} ungültige .srt-Dateien gefunden.")
    else:
        print("\nKeine ungültigen .srt-Dateien gefunden.")

    if orphan_srt_files:
        print("\nListe der verwaisten .srt-Dateien:")
        for orphan_file in orphan_srt_files:
            print(orphan_file)
        print(f"{len(orphan_srt_files)} verwaiste .srt-Dateien gefunden.")
    else:
        print("\nKeine verwaisten .srt-Dateien gefunden.")

    # Entferne ungültige .srt-Dateien, wenn Flag gesetzt ist
    if args.remove_invalid and invalid_srt_files:
        print("\nEntferne ungültige .srt-Dateien...")
        for srt in invalid_srt_files:
            try:
                srt.unlink()
                print(f"Entfernt: {srt}")
            except Exception as e:
                print(f"Fehler beim Entfernen von {srt}: {e}")

    # Entferne verwaiste .srt-Dateien, wenn Flag gesetzt ist
    if args.remove_orphan and orphan_srt_files:
        print("\nEntferne verwaiste .srt-Dateien...")
        for srt in orphan_srt_files:
            try:
                srt.unlink()
                print(f"Entfernt: {srt}")
            except Exception as e:
                print(f"Fehler beim Entfernen von {srt}: {e}")

    print("\nVorgang abgeschlossen.")

if __name__ == "__main__":
    main()
