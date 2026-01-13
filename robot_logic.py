import serial
import time

# --- CONFIGURATION ---
PORT_COM = 'COM14'       # À modifier selon ton PC
BAUDRATE = 115200
SIMULATION_MODE = False   # Mettre False quand le robot est branché

# --- PROTOCOLE ---
CMD_IDS = {
    "START": 1,   "STOP": 1,
    "SENS": 2,    "FREQ": 4,
    "VITESSE": 7, "PAUSE": 99
}

# --- DEFINITION DES VOIES ET SEQUENCES ---
# Chaque voie (A, B, C...) a sa propre "partition" de mouvements.
# Format : (COMMANDE, VALEUR)
# PAUSE est en secondes.

SEQUENCES_VOIES = {
    "VOIE A": [
        ("SENS", 1), ("VITESSE", 50), ("START", 1), # Avance moyen
        ("PAUSE", 2.0),
        ("VITESSE", 20), ("PAUSE", 1.0),            # Ralentit arrivée
        ("STOP", 0)
    ],
    "VOIE B": [
        ("SENS", 1), ("VITESSE", 80), ("START", 1), # Avance vite
        ("PAUSE", 3.0),                             # Trajet plus long
        ("STOP", 0)
    ],
    "VOIE C": [
        ("SENS", 0), ("VITESSE", 40), ("START", 1), # Recule (exemple)
        ("PAUSE", 4.0),
        ("STOP", 0)
    ],
    "VOIE D": [
        ("SENS", 0), ("VITESSE", 25), ("START", 1), # Avance moyen
        ("PAUSE", 2.5),
        ("VITESSE", 10), ("PAUSE", 1.0),            # Ralentit arrivée
        ("STOP", 0)
    ],
    "VOIE E": [
        ("SENS", 1), ("VITESSE", 60), ("START", 1), # Avance rapide
        ("PAUSE", 2.0),
        ("VITESSE", 30), ("PAUSE", 1.0),            # Ralentit arrivée
        ("STOP", 0)
    ], 
    # Tu peux ajouter d'autres voies ici (D, E, F...)
    "DEFAULT": [
        ("VITESSE", 30), ("START", 1), ("PAUSE", 1.0), ("STOP", 0)
    ]
}

class RobotCommunicator:
    def __init__(self):
        self.ser = None
        if not SIMULATION_MODE:
            try:
                self.ser = serial.Serial(PORT_COM, BAUDRATE, timeout=1.0)
                time.sleep(2) # Init
                self.ser.reset_input_buffer()
                print(f"[LOGIC] Connecté au port {PORT_COM}")
            except Exception as e:
                print(f"[LOGIC] Erreur Port Série : {e}")
                raise e
        else:
            print("[LOGIC] Mode SIMULATION activé.")

    def send_command(self, cmd_name, val):
        """Envoie la commande et attend l'ACK"""
        if cmd_name == "PAUSE":
            time.sleep(val)
            return True

        if cmd_name not in CMD_IDS: return False

        cmd_id = CMD_IDS[cmd_name]
        if cmd_name == "STOP": val = 0 # Force 0 pour STOP
            
        byte_cmd = 0x80 | cmd_id
        byte_val = int(val)

        print(f" -> ORDRE ROBOT: {cmd_name} ({val})")

        if not SIMULATION_MODE and self.ser:
            try:
                self.ser.write(bytearray([byte_cmd, byte_val]))
                ack = self.ser.read(1)
                return ack == b'\x06'
            except:
                return False
        else:
            time.sleep(0.1) # Simule le temps de transmission
            return True

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()