from serial import Serial
import time

PORTCOM = 'COM14'  # Change as needed for your system
BAUDRATE = 115200

# DEFINITION DES COMMANDES
COMMANDES = {
    "START": (1, 1),
    "STOP": (1, 0),
    "VITESSE": (7, None),  # Valeur à fournir par l'utilisateur
    "SENS": (2, None), # Valeur à fournir par l'utilisateur
    "FREQ": (4, None) # Valeur à fournir par l'utilisateur
}

try:
    ser = Serial(PORTCOM, BAUDRATE, timeout=1)
    print(f"Connected to {PORTCOM} at {BAUDRATE} baud.")
    time.sleep(2)  # Wait for the connection to establish
    ser.reset_input_buffer()
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

print(f"CONSOLE SERIAL - PORT: {PORTCOM} - BAUDRATE: {BAUDRATE}")
print("Utilisez le format suivant : CMD VALEUR\n")
print("Liste des commandes disponibles :")
for cmd in COMMANDES.keys():
    print(f" - {cmd}\n")
print("Exemples de commandes : STARTSTOP 0")
print("Pressez 'CTRL + C' pour quitter\n")

try:
    while True:
        cmd_input = input("Entrez la commande > ").strip().upper()

        if cmd_input == 'Q':
            print("Exiting program.")
            break

        cmd_id = -1
        val_int = -1
        parts = cmd_input.split()
        first_part = parts[0]

        try:
            if first_part in COMMANDES:

                cmd_id, cmd_val = COMMANDES[first_part]

                if cmd_val is None:
                    # Cas Variable
                    if len(parts) < 2:
                        print(f"Valeur requise pour la commande {first_part}.")
                        continue
                    cmd = cmd_id
                    val = int(parts[1])
                else:
                    cmd = cmd_id
                    val = cmd_val
            
            elif first_part.isdigit() and len(parts) == 2:
                cmd = int(parts[0])
                val = int(parts[1])
            else:
                print("Commande inconnue.")
                continue

            if cmd > 15 or val > 127:
                print("Valeur de commande ou de valeur hors limites.")
                continue

            byte_cmd = 0x80 | cmd
            byte_val = val

            print(f"Envoi de la commande: CMD={cmd} (0x{byte_cmd:02X}), VAL={val} (0x{byte_val:02X})")
            ser.write(bytearray([byte_cmd, byte_val]))

            ack = ser.read(1)
            if ack == b'\x06':
                print("Commande ACK reçue.")
            elif ack:
                print(f"NACK reçu: 0x{ack[0]:02X}")
            else:
                print("Aucune réponse reçue.")

        except ValueError:
            print("Erreur de format de la commande ou de la valeur.")
except KeyboardInterrupt:
    print("\nProgram terminated by user.")

finally:
    ser.close()
    print("Serial port closed.")
                       