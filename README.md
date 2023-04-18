# Prévision de précipitations de pluie en France de 2016-2019 (Météo France)

## Table des matières

* [À propos](#à-propos)
* [Contenu](#contenu)
* [Installation](#installation)
* [Résultats](#résultats)
* [Contact](#contact)

<br>

## À propos
Ce projet vise à construire un modèle selon une approche en séries temporelles pour prédire les précipitations journalières sur 7 jours. 

## Contenu
Ce projet contient :
- Un dossier pour les notebooks (Projet contenant les résultats de notre modèle)
- Un dossier "data" contenant les dossiers relatifs aux données
- Un dossier "scripts" avec différents modules utilisés dans le notebook
- Des fichiers env (expliqués ci-dessous)

## Installation
Pour utiliser ce projet, vous devez effectuer les commandes suivantes :
```bash
git clone https://github.com/luciegaba/MeteoFrance-Rain-Forecasting
cd MeteoFrance-Rain-Forecasting
```

Vous pouvez également créer un environnement conda (ou un équivalent) avec les packages à installer pour le projet:
```
conda env create -f environment.yml
conda activate meteofrance-prevision
