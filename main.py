import os
import csv
import qrcode
import time
from rich.console import Console
from PIL import Image
from PIL import Image, ImageDraw, ImageFont
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

# Créer le dossier codeQR-eleve s'il n'existe pas
output_dir = "codeQR_et_texte"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Chemin du fichier CSV contenant les données
csv_file = "id_place.csv"

# Configurer l'imprimante
backend = 'pyusb'  # ou 'linux_kernel' ou 'network'
model = 'QL-820NWB'
printer = 'usb://0x04f9:0x209d'

# générer d'abbord tout les qr code a partire du fichier csv 

# générer un fichier temporaire pour garder le chemin des QRcode generer
chemin_fichier_temp = f"{output_dir}/image_final.temp"

# définir le fichier CSV a lire 
csv_file = "id_place.csv"
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
                place = row['PLACE']
                id = row['ID']
                # affiche la ligne du csv sous la forme: Jean Dupont 3A 12345 {'nom': 'Jean', 'prénom': 'Dupont', 'classe': '3A', 'numéro_de_série': '12345'}
                # print(nom, prenom, classe, numero_serie,"\n", row)

                # creation des QRcode et des texts
                # mise en forme des données pour le QRcode et l'enrengistrer dans une variable : nom,prenom,classe,num série
                qr_data = f"{id}"
                text_data = f"{place}"

                # creation du qrcode et text
                # définition du format du QRcode
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)

                # définition du format de l'image du text
                # Créer une nouvelle image (largeur, hauteur) avec un fond blanc
                width, height = 600, 290
                image = Image.new('RGB', (width, height), 'white')
                 
                 # Initialiser l'objet de dessin
                draw = ImageDraw.Draw(image)

                # Charger une police (facultatif, vous pouvez utiliser une police par défaut)
                # Remplacez 'arial.ttf' par le chemin vers une police sur votre système
                font = ImageFont.truetype('arial.ttf', 140)  # Utilise une police par défaut

                # Définir la position du texte
                text_x, text_y = 50, 80  # Positionnement du texte dans l'image

                # génération du QRcode
                # choix de la couleur dans la quelle sera créer le QRcode
                img_QRcode = qr.make_image(fill_color="black", back_color="white")

                # Dessiner le texte sur l'image
                draw.text((text_x, text_y), text_data, fill='black', font=font)

                # création du QRcode et enrengistrement de l'image sous le nom et le chemin définie
                chemin_enrengistrement_QR = os.path.join(output_dir, f"{id}_qrcode.png")
                img_QRcode.save(chemin_enrengistrement_QR)

                # enrengistrment de l'image dans un répertoire définie
                # Sauvegarder l'image
                chemin_enrengistrement_texte_image = os.path.join(output_dir, f"{place}_text.png")
                image.save(chemin_enrengistrement_texte_image)

                # fusion des 2 image pour n'en former qu'une
                # Ouvre les deux images
                image_QR = Image.open(chemin_enrengistrement_QR)
                image_text = Image.open(chemin_enrengistrement_texte_image)

                # Obtiens les dimensions des images
                largeur1, hauteur1 = image_QR.size
                largeur2, hauteur2 = image_text.size

                largeur_totale = largeur1 + largeur2
                hauteur_totale = max(hauteur1, hauteur2)
                nouvelle_image = Image.new('RGB', (largeur_totale, hauteur_totale))

                # Colle les deux images dans la nouvelle image
                nouvelle_image.paste(image_QR, (0, 0))
                nouvelle_image.paste(image_text, (largeur1, 0))  # Positionne la deuxième image à droite de la première

                # Enregistre le resultat
                chemin_enrengistrement_QRcode_et_texte = os.path.join(output_dir,f"{id}_qrcode_et_text.png")
                nouvelle_image.save(chemin_enrengistrement_QRcode_et_texte)

                # enrengistrer le chemin du QRcode dans le fichier temp
                # Écrire du texte dans le fichier
                fichier.write(f"{id}_qrcode_et_text.png\n")

                # afficher un text pour confirmer la creation du code QR
                print(f"QR code généré pour {id} et enregistré sous {chemin_enrengistrement_QR}")
                # afficher un text pour confirmer la creation du text
                print(f"text généré pour {place} et enregistré sous {chemin_enrengistrement_texte_image}")

# impression du tout une fois toute les image générer

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
                label='62',  # Modifier selon votre étiquette
                rotate='0', # modifie l'orientation de l'image
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
            #print(f"{output_dir}/{ligne.strip()}")
