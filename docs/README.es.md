# Skill de video de Silico Grove

Este skill permite que un AI Agent compatible genere videos mediante Silico Grove. Admite texto a video, generación con referencias de imagen/video/audio, carga de archivos locales, consulta de tareas y descarga de MP4.

## Copiar para tu AI

```text
Instala y utiliza este Skill de generación de video de Silico Grove:
https://github.com/Rodert/silicogrove-video-skill

Instálalo con Git clone y conserva el directorio .git. Antes del primer uso de cada día, ejecuta `python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"` y vuelve a leer `SKILL.md` solo si devuelve `updated`. Una actualización disponible restablece por la fuerza los archivos de Skill rastreados a `origin/main` y descarta los cambios locales rastreados; si no se puede actualizar, usa la versión actual.

En el primer uso, pídeme de forma proactiva mi API Key de Silico Grove y guárdala de forma segura en la configuración local para usos futuros. No me pidas configurar manualmente una variable de entorno.

Si solo proporciono una descripción de video, genera el video desde texto directamente. Pídeme subir un archivo solo cuando solicite usar una referencia de imagen, video o audio; si proporciono una URL pública http(s), úsala directamente.

Para las solicitudes, usa primero https://ai.silicogrove.com. Si hay un error de red, un tiempo de espera o una respuesta 404, cambia automáticamente a https://api.silicogrove.com.

Documentación de uso:
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```
