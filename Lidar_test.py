from rplidar import RPLidar
import serial
import time
import sys

# --- CONFIGURATION DES PORTS ---
# Sur Raspberry Pi, les ports USB sont souvent /dev/ttyUSB0 ou /dev/ttyACM0
# Branche tes périphériques et tape 'ls /dev/tty*' dans le terminal pour trouver les bons noms.
LIDAR_PORT_NAME = '/dev/ttyUSB0'  
STM32_PORT_NAME = '/dev/ttyS0'  

BAUDRATE_LIDAR = 115200
BAUDRATE_STM32 = 115200

# --- PARAMETRES DE SECURITE (en mm) ---
DIST_STOP_MM = 800      # 80 cm
DIST_SLOW_MM = 1200     # 1m20
ANGLE_CONE_AVANT = 40   # Cône de vision total (20° à gauche, 20° à droite)

def run_lidar():
    # 1. Initialisation de la connexion STM32
    stm_ser = None
    try:
        stm_ser = serial.Serial(STM32_PORT_NAME, BAUDRATE_STM32, timeout=1)
        print(f"STM32 connecté sur {STM32_PORT_NAME}")
    except Exception as e:
        print(f"Impossible de connecter la STM32 sur {STM32_PORT_NAME} : {e}")
        print("Le script va continuer mais ne pourra pas envoyer d'ordres.")

    # 2. Initialisation du LIDAR
    lidar = None
    try:
        lidar = RPLidar(LIDAR_PORT_NAME, baudrate=BAUDRATE_LIDAR, timeout=3)
        print(f"LIDAR connecté sur {LIDAR_PORT_NAME}")
    except Exception as e:
        print(f"Erreur critique LIDAR : {e}")
        return

    print("--- SURVEILLANCE ACTIVE ---")
    print("Logique : Envoi d'ordre uniquement sur CHANGEMENT d'état (Anti-Flood).")
    print("Ctrl+C pour arrêter.")

    lidar.start_motor()
    time.sleep(1)

    # Variables de fonctionnement
    min_distance_cycle = 10000 # Distance min vue sur le tour en cours
    last_sent_state = None     # Pour se souvenir du dernier ordre envoyé ('S', 'L', 'F')

    try:
        # Boucle de lecture des points
        for new_scan, quality, angle, distance in lidar.iter_measurments():
            
            # --- A. LOGIQUE DE FIN DE TOUR (PRISE DE DÉCISION) ---
            if new_scan:
                # 1. On détermine l'état actuel basé sur le tour qu'on vient de finir
                current_state = 'F' # Par défaut : Free (Voie libre)

                if min_distance_cycle < DIST_STOP_MM:
                    current_state = 'S' # STOP
                elif min_distance_cycle < DIST_SLOW_MM:
                    current_state = 'L' # LOW SPEED / SLOW
                else:
                    current_state = 'F' # FREE / FULL SPEED

                # 2. FILTRE ANTI-FLOOD : On parle à la STM32 seulement si l'état change
                if current_state != last_sent_state:
                    
                    if stm_ser and stm_ser.is_open:
                        try:
                            stm_ser.write(current_state.encode())
                            print(f"--> ENVOI STM32 : '{current_state}' (Obstacle à {int(min_distance_cycle)}mm)")
                        except Exception as e:
                            print(f"Erreur d'écriture Série : {e}")
                    else:
                        # Mode debug sans STM32
                        print(f"[SIMULATION] Changement d'état : {current_state} (Dist: {int(min_distance_cycle)}mm)")

                    # On met à jour la mémoire pour ne pas répéter le message au prochain tour
                    last_sent_state = current_state

                # 3. Reset pour le nouveau tour qui commence
                min_distance_cycle = 10000

            # --- B. ANALYSE DU POINT COURANT ---
            if distance > 0 and quality > 0:
                # Vérifie si le point est dans le cône avant
                # Le cône est centré sur 0° (donc de 340° à 360° et de 0° à 20°)
                half_cone = ANGLE_CONE_AVANT / 2
                
                if (angle < half_cone) or (angle > (360 - half_cone)):
                    # On ne garde que la distance la plus courte vue dans le cône
                    if distance < min_distance_cycle:
                        min_distance_cycle = distance

    except KeyboardInterrupt:
        print("\nArrêt utilisateur demandé.")
    except Exception as e:
        print(f"\nErreur en cours d'exécution : {e}")
    finally:
        print("Arrêt propre des périphériques...")
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        if stm_ser:
            stm_ser.close()
        print("Terminé.")

if __name__ == '__main__':
    run_lidar()