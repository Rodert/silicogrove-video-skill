# Skill vidéo Silico Grove

Ce skill permet à un AI Agent compatible de générer des vidéos avec Silico Grove. Il prend en charge le texte vers vidéo, la génération à partir de références image/vidéo/audio, l'envoi de fichiers locaux, le suivi des tâches et le téléchargement MP4.

## Copier pour votre AI

```text
Installe et utilise ce Skill de génération vidéo Silico Grove :
https://github.com/Rodert/silicogrove-video-skill

Installe-le avec Git clone et conserve le répertoire .git. Avant chaque utilisation, exécute git pull --ff-only origin main dans le répertoire du skill installé, puis relis SKILL.md avant de traiter ma demande si des fichiers ont été mis à jour. Si la mise à jour est indisponible ou qu'une avance rapide sûre est impossible, préserve les modifications locales et utilise la version installée.

Lors de la première utilisation, demande-moi de façon proactive ma clé API Silico Grove et enregistre-la de manière sécurisée dans la configuration locale pour les utilisations suivantes. Ne me demande pas de configurer manuellement une variable d'environnement.

Si je fournis seulement une description vidéo, génère directement une vidéo à partir du texte. Demande-moi d'envoyer un fichier seulement si je demande une référence d'image, de vidéo ou d'audio ; si je fournis une URL publique http(s), utilise-la directement.

Pour les requêtes, utilise d'abord https://ai.silicogrove.com. En cas d'erreur réseau, de délai d'attente ou de réponse 404, bascule automatiquement vers https://api.silicogrove.com.

Documentation d'utilisation :
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```
