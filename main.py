import os
import csv
import qrcode
import time
from rich.console import Console
from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

# Créer le dossier codeQR-eleve s'il n'existe pas
output_dir = "codeQR-eleves"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Chemin du fichier CSV contenant les données
csv_file = "eleves.csv"

# Configurer l'imprimante
backend = 'pyusb'  # ou 'linux_kernel' ou 'network'
model = 'QL-820NWB'
printer = 'usb://0x04f9:0x209d'

# générer d'abbord tout les qr code a partire du fichier csv 

# générer un fichier temporaire pour garder le chemin des QRcode generer
chemin_fichier_temp = "codeQR-eleves/QRcode.temp"

# définir le fichier CSV a lire 
csv_file = "eleves.csv"
# lire le fichier CSV définie avec l'encodage utf-8
with open(csv_file, mode='r', newline='', encoding='utf-8') as fichier_csv:
    # utiliser le csv.DictReader https://docs.python.org/fr/3.10/library/csv.html 
    lecture = csv.DictReader(fichier_csv)

    # ajout d'une animation pendant le chargment
    console = Console()
    with console.status("[bold green]Génération des QRcode en cours...") as status:

        # Ouvrir le fichier en mode écriture ('w' écrase l'ancien fichier ou le crée s'il n'existe pas)
        with open(chemin_fichier_temp, 'w') as fichier:
            # lecture des ligne 
            for row in lecture:
                nom = row['nom']
                prenom = row['prénom']
                classe = row['classe']
                numero_serie = row['numéro_de_série']
                # affiche la ligne du csv sous la forme: Jean Dupont 3A 12345 {'nom': 'Jean', 'prénom': 'Dupont', 'classe': '3A', 'numéro_de_série': '12345'}
                # print(nom, prenom, classe, numero_serie,"\n", row)

                # creation des QRcode
                # mise en forme des données pour le QRcode et l'enrengistrer dans une variable : nom,prenom,classe,num série
                qr_data = f"Nom: {nom}\nPrénom: {prenom}\nClasse: {classe}\nNuméro de série: {numero_serie}"

                # creation du qrcode
                # définition du format du QRcode
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)

                # génération du QRcode
                # choix de la couleur dans la quelle sera créer le QRcode
                img_QRcode = qr.make_image(fill_color="black", back_color="white")

                # création du QRcode et enrengistrement de l'image sous le nom et le chemin définie
                chemin_enrengistrement = os.path.join(output_dir, f"{nom}_{prenom}_{classe}_{numero_serie}_qrcode.png")
                img_QRcode.save(chemin_enrengistrement)

                #enrengistrer le chemin du QRcode dans le fichier temp
                # Écrire du texte dans le fichier
                fichier.write(f"{nom}_{prenom}_{classe}_{numero_serie}_qrcode.png\n")

                # afficher un text pour confirmer la creation  
                print(f"QR code généré pour {nom} {prenom} {classe} {numero_serie} et enregistré sous {chemin_enrengistrement}")

# impression des QRcode une fois tous générer

# Lecture du fichier et stockage des lignes dans une variable

# Chemin du fichier texte
chemin_fichier = chemin_fichier_temp

# Lecture du fichier et stockage des lignes dans une variable
with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
    lignes = fichier.readlines()

    # ajout d'une animation pendant le chargment
    console = Console()
    with console.status("[bold purple]impression en cours...") as status:
        # Boucle pour imprimer chaque limage de chaque ligne
        for ligne in lignes:

            # print(ligne.strip())  # Utilise strip() pour enlever les espaces et les retours à la ligne cette ligne sert a afficher 

            # Ouvrir l'image et préparer pour l'impression
            im = Image.open(f"{output_dir}/{ligne.strip()}")

            qlr = BrotherQLRaster(model)
            qlr.exception_on_warning = True

            # Convertir l'image pour l'impression
            instructions = convert(
                qlr=qlr,
                images=[im],
                label='29',  # Modifier selon votre étiquette
                rotate='0',
                threshold=50.0,
                dither=True,
                compress=False,
                red=False,
                dpi_600=False,
                hq=True,
                cut=True
            )

            # Envoyer l'impression
            send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)
