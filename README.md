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

Normalement, vous devriez avoir accès à un bucket S3. Sinon, la base d'origine (16G0) est à retrouver [ici](https://meteonet.umr-cnrm.fr/dataset/data/) en récupérant le contenu de "grounds_stations" dans NW et SE.
Remarque: un jeu de données intermédiaire (moins volumineux) peut ê sera à placer dans "data/intermediate" 
Normalement, vous devriez avoir accès à un bucket S3. Sinon, la base d'origine (16G0) est à retrouver [ici](https://meteonet.umr-cnrm.fr/dataset/data/) en récupérant le contenu de "grounds_stations" dans NW et SE. Les csv devront être mis dans   Sinon, un jeu de données intermédiaire (moins volumineux) sera à  récupérer dans le [Drive](https://drive.google.com/file/d/1MCbUBo39btOu9SBlVZ6jN3sLgOPxTGV-/view?usp=share_link) et devra être placé dans "data/intermediate".
