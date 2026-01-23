# 📂 Dossier Technique : PCB1 - Asservissement Moteurs BLDC

Ce répertoire contient les fichiers de conception électronique pour la carte **PCB1**, dédiée au pilotage et à l'asservissement des moteurs Brushless (BLDC) de notre projet.

## 🏫 Contexte
* **École :** CPE Lyon
* **Projet :** Projet de majeure 5ESE - CPE Lyon
* **Responsabilité :** Conception Carte de Puissance / Asservissement

## 📦 Contenu de l'archive
Le fichier `Equipe1_PCB1_dossier-technique.zip` contient l'intégralité du projet KiCad. Une fois décompressé, vous y trouverez :

* **Schémas électroniques** (`Cde_Brushless.kicad_sch`) : Architecture de commande et de puissance.
* **Routage PCB** (`PCB1_final.kicad_pcb`) : Placement des composants et tracé des pistes.
* **Librairies locales** : Symboles et empreintes spécifiques au projet.
* **(Optionnel)** Fichiers de fabrication (Gerbers/BOM) pour la production.

## 🛠 Caractéristiques de la carte (PCB1)
Cette carte a pour fonction principale de contrôler les moteurs BLDC.
* **Contrôleur principal :** STM32
* **Drivers Pont :** IR2101
* **Alimentation :** Batterie 36V

## ⚙️ Comment ouvrir le projet ?
1.  **Télécharger** le fichier `Equipe1_PCB1_dossier-technique.zip`.
2.  **Extraire** l'archive sur votre machine locale.
3.  **Lancer KiCad** (Version recommandée : **9.0** ou supérieure).
4.  Ouvrir le fichier projet `Cde_Brushless.kicad_pro` situé dans le dossier extrait.

---
**Auteur :** Thomas SANDIER
**Date de mise à jour :** 23 Janvier 2026
