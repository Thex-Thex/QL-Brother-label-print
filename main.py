import os
import csv
import qrcode
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster


# Chemin du fichier CSV contenant les données
csv_file = "dataQR.csv"
# Configuration de l'imprimante Brother QL
backend = "pyusb"  # 'pyusb', 'Linux_kernel', ou 'network'
model = "QL-820NWB"
printer = "usb://0x04f9:0x209d"  # Changez ce paramètre pour votre imprimante

def create_output_dir():
    # Créer le dossier de sortie s'il n'existe pas
    global output_dir
    output_dir = "codeQR_et_texte_voiture"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def check_font():
    # Configuration de la police pour le texte
    try:
        # Remplacez par le chemin exact de votre police si nécessaire
        global font
        font = ImageFont.truetype("arial.ttf", 110)
    except IOError:
        print("Police non trouvée. Assurez-vous que 'arial.ttf' est disponible.")
        exit()

def create_temp_file():
    # Fichier temporaire pour stocker les chemins des images générées
    global chemin_fichier_temp
    chemin_fichier_temp = os.path.join(output_dir, "images_a_imprimer.temp")

def make_qrcode_text():
    # Génération des QR Codes et des images
    global output_dir
    global chemin_fichier_temp
    global console
    console = Console()

    with open(csv_file, mode="r", newline="", encoding="utf-8") as fichier_csv:
        # Lire les données du CSV
        lecture = csv.DictReader(fichier_csv)

        with console.status(
            "[bold green]Génération des QR Codes et des images en cours..."
        ):
            with open(chemin_fichier_temp, "w", encoding="utf-8") as fichier_temp:
                for row in lecture:
                    # Récupérer les données depuis le CSV
                    lien = row["LIEN"]
                    id = row["ID"]
                    code = row["CODE"]

                    qr_data = f"https://{lien}"
                    text_data = f"{lien}\nCode : {code}"

                    # Générer le QR Code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=40,  # Taille du QR Code
                        border=2,  # Bordure réduite
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)

                    img_QRcode = qr.make_image(
                        fill_color="black", back_color="white"
                    ).convert("RGB")

                    # Rogner les bords blancs du QR Code
                    bbox = img_QRcode.getbbox()
                    img_QRcode = img_QRcode.crop(bbox)

                    # Générer l'image contenant le texte
                    text_width, text_height = img_QRcode.width, 300  # Largeur identique au QR Code
                    image_text = Image.new("RGB", (text_width, text_height), "white")
                    draw = ImageDraw.Draw(image_text)

                    # Calculer la position pour centrer le texte
                    text_width, text_height = draw.textsize(text_data, font=font)
                    text_x = (img_QRcode.width - text_width) // 2  # Centrer horizontalement
                    text_y = (300 - text_height) // 2  # Centrer verticalement
                    draw.text((text_x, text_y), text_data, fill="black", font=font)

                    # Fusionner QR Code et texte dans une seule image
                    largeur_totale = img_QRcode.width
                    hauteur_totale = img_QRcode.height + image_text.height
                    nouvelle_image = Image.new(
                        "RGB", (largeur_totale, hauteur_totale), "white"
                    )
                    nouvelle_image.paste(img_QRcode, (0, 0))  # QR Code à gauche
                    nouvelle_image.paste(
                        image_text, (0, img_QRcode.height)
                    )  # Texte en dessous

                    # Enregistrer l'image finale
                    chemin_enregistrement = os.path.join(
                        output_dir, f"{id}_code_qrcode_et_text.png"
                    )
                    nouvelle_image.save(chemin_enregistrement)

                    # Ajouter le chemin de l'image au fichier temporaire
                    fichier_temp.write(f"{chemin_enregistrement}\n")

                    console.print(
                        f"[bold green]Image générée pour {id} : {chemin_enregistrement}"
                    )

def print():
    # Impression des images
    global console
    global chemin_fichier_temp
    console.print("[bold blue]Démarrage de l'impression des images générées...")

    with open(chemin_fichier_temp, "r", encoding="utf-8") as fichier_temp:
        lignes = fichier_temp.readlines()

        with console.status("[bold purple]Impression en cours..."):
            for ligne in lignes:
                chemin_image = ligne.strip()
                if not os.path.exists(chemin_image):
                    console.print(f"[bold red]Image introuvable : {chemin_image}")
                    continue

                # Charger l'image
                im = Image.open(chemin_image)

                # Configurer l'imprimante Brother
                qlr = BrotherQLRaster(model)
                qlr.exception_on_warning = True

                # Convertir l'image pour l'impression
                instructions = convert(
                    qlr=qlr,
                    images=[im],
                    label="29",  # Remplacez par votre type d'étiquette (ex : 62 pour 62 mm)
                    rotate="90",  # Orientation de l'image
                    threshold=50.0,
                    dither=True,
                    compress=False,
                    red=False,
                    dpi_600=False,
                    hq=True,
                    cut=True,
                )

                # Envoyer l'image à l'imprimante
                send(
                    instructions=instructions,
                    printer_identifier=printer,
                    backend_identifier=backend,
                    blocking=True,
                )
                console.print(f"[bold green]Image imprimée : {chemin_image}")
