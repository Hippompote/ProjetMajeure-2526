import sys
import os
from PySide6.QtWidgets import QApplication, QProgressBar, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QThread, Signal, Slot, QCoreApplication, Qt
import time

# On importe la logique depuis l'autre fichier
from robot_logic import RobotCommunicator, SEQUENCES_VOIES

# --- MAPPING : QUEL TRAIN VA SUR QUELLE VOIE ? ---
# Modifie ici pour assigner tes trains aux voies A, B, C...
TRAIN_TO_TRACK = {
    "TGV InOUI -> Toulouse":    "VOIE A",
    "FRECCIAROSSA -> Paris":    "VOIE B",
    "TER AuRA -> Grenoble":     "VOIE C",
    "TER AuRA -> Valence":      "VOIE D", # Plusieurs trains peuvent utiliser la même voie
    "TER AuRA -> Clermont":     "VOIE E",
    "INTERCITES -> Nantes":     "VOIE A",
    "ICE -> Francfort":         "VOIE D"
}

# --- WORKER (CHEF D'ORCHESTRE) ---
class WorkerThread(QThread):
    progress_updated = Signal(int)
    finished = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, track_name):
        super().__init__()
        self.track_name = track_name

    def run(self):
        # 1. On récupère la séquence de la voie
        sequence = SEQUENCES_VOIES.get(self.track_name, SEQUENCES_VOIES["DEFAULT"])
        total = len(sequence)
        
        print(f"--- DÉPART SUR {self.track_name} ---")
        
        # 2. Connexion
        try:
            robot = RobotCommunicator()
        except Exception as e:
            self.error_occurred.emit(str(e))
            return

        # 3. Exécution
        for i, (cmd, val) in enumerate(sequence):
            success = robot.send_command(cmd, val)
            time.sleep(0.1)  # Petit délai entre commandes
            if not success:
                print("Erreur transmission !")
                break
            
            # Mise à jour barre
            prog = int(((i + 1) / total) * 100)
            self.progress_updated.emit(prog)

        robot.close()
        self.finished.emit()

# --- INTERFACE ---
class InterfaceManager:
    def __init__(self):
        if not os.path.exists("Interface Projet.ui"):
            print("ERREUR : Interface Projet.ui manquant")
            sys.exit(1)

        loader = QUiLoader()
        ui_file = QFile("Interface Projet.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()

        # Setup Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 2px solid #3e4147; border-radius: 5px;
            text-align: center; color: white; background-color: #2e3035; height: 20px;}
            QProgressBar::chunk { background-color: #a87eeb; }
        """)
        self.progress_bar.hide()
        self.ui.statusbar.addPermanentWidget(self.progress_bar, 1)

        # CONNEXION DES BOUTONS VIA LE TEXTE
        # Astuce : On lit le texte du bouton pour savoir quel train c'est
        self.ui.pushButton_2.clicked.connect(lambda: self.clic_train("TGV InOUI -> Toulouse"))
        self.ui.pushButton_3.clicked.connect(lambda: self.clic_train("FRECCIAROSSA -> Paris"))
        self.ui.pushButton_4.clicked.connect(lambda: self.clic_train("TER AuRA -> Grenoble"))
        self.ui.pushButton_5.clicked.connect(lambda: self.clic_train("TER AuRA -> Valence"))
        self.ui.pushButton_6.clicked.connect(lambda: self.clic_train("TER AuRA -> Clermont"))
        self.ui.pushButton_7.clicked.connect(lambda: self.clic_train("INTERCITES -> Nantes"))
        self.ui.pushButton_8.clicked.connect(lambda: self.clic_train("ICE -> Francfort"))

        self.ui.show()

    def clic_train(self, nom_train):
        # 1. Trouver la voie
        voie = TRAIN_TO_TRACK.get(nom_train, "VOIE A") # Voie A par défaut
        print(f"Train sélectionné : {nom_train} -> Affecté à {voie}")
        
        # 2. Lancer la séquence
        self.lancer_sequence(voie)

    def lancer_sequence(self, voie):
        self.ui.centralwidget.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        self.worker = WorkerThread(voie)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.fin_sequence)
        self.worker.error_occurred.connect(lambda e: QMessageBox.critical(self.ui, "Erreur", e))
        self.worker.start()

    def fin_sequence(self):
        self.ui.centralwidget.setEnabled(True)
        self.progress_bar.hide()
        print("--- Terminus ---")

if __name__ == "__main__":
    if hasattr(Qt, 'AA_ShareOpenGLContexts'):
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    manager = InterfaceManager()
    sys.exit(app.exec())