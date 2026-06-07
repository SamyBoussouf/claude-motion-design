---
name: project-psychovius
description: TikTok/YouTube Shorts content creation pipeline — psychology phenomenon animation in @psychovius neon style
metadata:
  type: project
---

Pipeline de création de contenu automatisé pour des shorts de psychologie dans le style neon-sketch de @psychovius.

**Why:** Reproduire le style exact de la référence ref_001.mp4 (Wild Horse Effect) de façon scalable.

**How to apply:** Quand l'utilisateur fournit une description de phénomène psychologique, générer script + scène Manim + audio + composition finale.

## Stack validée
- Animation: Manim Community v0.20.1 (Python 3.12, .venv)
- Glow: OpenCV gaussian blur screen-blend
- TTS: ElevenLabs (5 comptes free, 50k chars/mois)
- Composition: FFmpeg
- Format: 1080x1920 @ 30fps

## État Phase 1 (complété)
- config/style.py — constantes visuelles calibrées sur ref_001
- scenes/base.py — classe NeonScene avec helpers (draw_in, flash_impact, word_label, title_text)
- pipeline/glow.py — post-process OpenCV
- pipeline/tts.py — ElevenLabs TTS + word timestamps
- pipeline/composer.py — FFmpeg assembly
- pipeline/run.py — orchestrateur
- Test rendu validé visuellement (preview frames OK)

## Ce qu'il manque pour produire une vraie vidéo
- Fichier .env avec ELEVENLABS_API_KEY (l'utilisateur doit le créer)
- Phase 2: script_generator.py (input phénomène → script + scènes)
- Phase 3: génération automatique code Manim depuis description scène

## Input attendu de l'utilisateur
Un message dans le chat avec la description du phénomène psychologique. Pas de format imposé.
