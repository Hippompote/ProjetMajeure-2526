import matplotlib.pyplot as plt
import numpy as np
from rplidar import RPLidar

# --- CONFIGURATION ---
PORT_NAME = 'COM17'
BAUDRATE = 115200
ANGLE_CONE = 40  # Ton angle de surveillance (40°)

def run_visual_calibration():
    # Connexion robuste
    lidar = RPLidar(PORT_NAME, baudrate=BAUDRATE, timeout=3)

    # --- SETUP GRAPHIQUE ---
    plt.ion() # Mode interactif
    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection='polar')
    
    # Configuration pour que 0° soit en HAUT (Nord) et que ça tourne dans le sens horaire
    ax.set_theta_zero_location("N") 
    ax.set_theta_direction(1) 
    
    print(f"Connexion au LIDAR sur {PORT_NAME}...")
    print("La flèche BLEUE indique l'avant théorique du robot.")
    print("La zone ROUGE indique ton cône de détection.")
    
    lidar.start_motor()
    
    # Buffers pour stocker un tour complet
    scan_angles = []
    scan_distances = []

    try:
        for new_scan, quality, angle, distance in lidar.iter_measurments():
            
            # Si on commence un nouveau tour, on rafraichit l'écran avec les données du tour précédent
            if new_scan:
                ax.clear()
                
                # 1. Dessiner les points détectés (Convertir deg -> rad)
                # On filtre les 0 et les distances trop grandes (>3m) pour la lisibilité
                valid_idxs = [i for i, d in enumerate(scan_distances) if 0 < d < 3000]
                rad_angles = [np.radians(360 - scan_angles[i]) for i in valid_idxs]
                dists = [scan_distances[i] for i in valid_idxs]
                
                ax.scatter(rad_angles, dists, s=5, c='black', alpha=0.7)
                
                # 2. Dessiner le CÔNE DE SÉCURITÉ (Zone Rouge)
                # Limites du cône en radians
                left_limit = np.radians(360 - (ANGLE_CONE / 2))
                right_limit = np.radians(ANGLE_CONE / 2)
                
                # On trace deux lignes rouges pour délimiter le cône
                ax.plot([0, left_limit], [0, 2000], color='red', linewidth=2, linestyle='--')
                ax.plot([0, right_limit], [0, 2000], color='red', linewidth=2, linestyle='--')
                
                # On colorie légèrement la zone dangereuse
                # Note: fill_between sur polaire est un peu tricky, on utilise des barres ou juste les lignes
                # Ici on laisse les lignes pour la clarté
                
                # 3. Dessiner la Flèche "AVANT" (Nord / 0°)
                ax.arrow(0, 0, 0, 1800, alpha=1, width=0.05, edgecolor='blue', facecolor='blue', lw=2)
                ax.text(0, 2200, "AVANT ROBOT", ha='center', color='blue', fontweight='bold')
                
                # Paramètres d'échelle fixes (pour éviter le zoom auto désagréable)
                ax.set_rmax(2500) # Vue max à 2.5 mètres
                ax.grid(True)
                
                plt.draw()
                plt.pause(0.01) # Pause nécessaire pour que la fenêtre ne fige pas
                
                # Reset des buffers pour le nouveau tour
                scan_angles = []
                scan_distances = []
            
            # Stockage des données courantes
            if distance > 0:
                scan_angles.append(angle)
                scan_distances.append(distance)

    except KeyboardInterrupt:
        print("Arrêt utilisateur")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()

if __name__ == '__main__':
    run_visual_calibration()