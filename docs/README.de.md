# Silico Grove Video-Skill

Dieses Skill ermöglicht einem kompatiblen AI Agent die Videogenerierung über Silico Grove. Es unterstützt Text-zu-Video, Generierung mit Bild-/Video-/Audio-Referenzen, das Hochladen lokaler Dateien, Aufgabenabfrage und MP4-Download.

## Für deine AI kopieren

```text
Installiere und verwende diesen Silico Grove Video-Generierungs-Skill:
https://github.com/Rodert/silicogrove-video-skill

Installiere ihn per Git clone und behalte das Verzeichnis .git bei. Führe vor der ersten Nutzung des Tages `python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"` aus und lies `SKILL.md` nur bei `updated` erneut. Ein verfügbares Update setzt nachverfolgte Skill-Dateien zwangsweise auf `origin/main` zurück und verwirft lokale nachverfolgte Änderungen; ist kein Update möglich, verwende die aktuelle Version.

Bitte frage mich bei der ersten Nutzung aktiv nach meinem Silico Grove API Key und speichere ihn sicher in der lokalen Konfiguration für spätere Verwendung. Fordere mich nicht dazu auf, eine Umgebungsvariable manuell zu konfigurieren.

Wenn ich nur eine Videobeschreibung angebe, erstelle das Text-zu-Video direkt. Bitte fordere nur dann einen Datei-Upload an, wenn ich eine Bild-, Video- oder Audio-Referenz verwenden möchte; eine öffentliche http(s)-URL soll direkt verwendet werden.

Verwende für Anfragen zuerst https://ai.silicogrove.com. Bei einem Netzwerkfehler, Timeout oder einer 404-Antwort wechsle automatisch zu https://api.silicogrove.com.

Nutzungsdokumentation:
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```
