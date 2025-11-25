# Prosodicz BY CHIHAB EL OIDI

Application Python desktop pour l'analyse prosodique de la parole.

## Installation

### 1. Cloner ou télécharger le projet

### 2. Installer les dépendances

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Lancer l'application

\`\`\`bash
python prosodicz_main.py
\`\`\`

## Fonctionnalités

### Enregistrement
- **4 modes d'enregistrement** : Déclarative, Interrogative, Exclamative, Impérative
- Enregistrement vocal de 5 secondes
- Import de fichiers audio (MP3, OGG, WAV, FLAC)

### Affichage
- **Signal Audio** : Visualisation du signal avec amplitude vs temps
- **Fréquence Fondamentale (F0)** : Analyse de F0 avec moyenne
- **Spectrogramme** : Vue fréquentielle du signal
- **Vue Complète** : Tous les graphiques ensemble

### Menu
- **Menu Enregistrer** : Accès rapide aux 4 modes
- **Menu Affichage** : Affichage des signaux enregistrés + comparaison

### Gestion des fichiers
- Les enregistrements sont sauvegardés dans le dossier `recordings/`
- Format : `{Mode}_{Timestamp}.wav`
- Dernier enregistrement : `{Mode}_latest.wav`

## Utilisation

1. Sélectionnez un mode d'enregistrement (Déclarative, Interrogative, etc.)
2. Cliquez sur "Enregistrer" ou utilisez le menu
3. Parlez pendant 5 secondes
4. Cliquez sur "Afficher Signal", "Afficher F0" ou autre visualisation
5. Utilisez "Sauvegarder" pour conserver l'enregistrement

## Structure

\`\`\`
.
├── prosodicz_main.py       # Fichier principal
├── requirements.txt         # Dépendances Python
├── README.md               # Documentation
└── recordings/             # Dossier des enregistrements (créé automatiquement)
\`\`\`

## Système d'exploitation

- Windows, macOS, Linux (tous supportés grâce à tkinter et librosa)
