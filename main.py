import os
import csv
import qrcode
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

# ---------------------------------
# Fonctions Principal
# ---------------------------------

# Chemin du fichier CSV contenant les données
csv_file = ""
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
        font = ImageFont.truetype("arial.ttf", 150)
    except IOError:
        print("Police non trouvée. Assurez-vous que 'arial.ttf' est disponible.")
        exit()

def create_temp_file():
    # Fichier temporaire pour stocker les chemins des images générées
    global chemin_fichier_temp
    chemin_fichier_temp = os.path.join(output_dir, "images_a_imprimer.temp")

def make_qrcode_text(update_progress_gen, update_qr_preview):
    global output_dir
    global chemin_fichier_temp
    global csv_file

    if csv_file == "":
        messagebox.showerror("Erreur", "Aucun fichier sélectionné")
        return

    # Lire toutes les lignes pour connaître le total
    with open(csv_file, mode="r", newline="", encoding="utf-8") as fichier_csv:
        lecture = list(csv.DictReader(fichier_csv))

    total = len(lecture)
    count = 0

    with open(chemin_fichier_temp, "w", encoding="utf-8") as fichier_temp:

        for row in lecture:
            lien = row["LIEN"]
            id = row["ID"]
            code = row["CODE"]

            qr_data = f"https://{lien}"
            text_data = f"{lien}\nCode : {code}"

            # Génération QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=40,
                border=0,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            img_QRcode = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            # Rogner l'image
            bbox = img_QRcode.getbbox()
            img_QRcode = img_QRcode.crop(bbox)

            # Génération image texte
            text_width, text_height = img_QRcode.width, 300
            image_text = Image.new("RGB", (text_width, text_height), "white")
            draw = ImageDraw.Draw(image_text)

            tw, th = draw.textsize(text_data, font=font)
            text_x = (img_QRcode.width - tw) // 2
            text_y = (300 - th) // 2
            draw.text((text_x, text_y), text_data, fill="black", font=font)

            # Fusion finale
            largeur_totale = img_QRcode.width
            hauteur_totale = img_QRcode.height + image_text.height
            nouvelle_image = Image.new("RGB", (largeur_totale, hauteur_totale), "white")
            nouvelle_image.paste(img_QRcode, (0, 0))
            nouvelle_image.paste(image_text, (0, img_QRcode.height))

            # Sauvegarde
            chemin_enregistrement = os.path.join(output_dir, f"{id}_code_qrcode_et_text.png")
            nouvelle_image.save(chemin_enregistrement)

            # Ajoute au fichier temporaire
            fichier_temp.write(f"{chemin_enregistrement}\n")

            # ------------------- GUI -------------------
            # Affiche le QR généré proportionnel
            update_qr_preview(nouvelle_image)

            # Met à jour la barre de progression
            count += 1
            progress_percent = int((count / total) * 100)
            update_progress_gen(progress_percent)
            # Mettre à jour le label “QR actuel / total”
            label_count_gen.config(text=f"{count} / {total}")
            root.update_idletasks()  # Force Tkinter à rafraîchir l’affichage
    
    btn_print.config(state="normal")
    messagebox.showinfo("Terminé", "Tous les QR codes ont été générés !")

def print_send(update_progress_print, update_qr_preview):
    # Impression des images
    global chemin_fichier_temp

    with open(chemin_fichier_temp, "r", encoding="utf-8") as fichier_temp:
        lignes = fichier_temp.readlines()
    
        total = len(lignes)
        count = 0
        
        for ligne in lignes:
            chemin_image = ligne.strip()
            if not os.path.exists(chemin_image):
                messagebox.showerror("Erreur",f"Image introuvable : {chemin_image}")
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

            try:
                send(
                instructions=instructions,
                printer_identifier=printer,
                backend_identifier=backend,
                blocking=True,
                )
            except:
                messagebox.showerror("Erreur", "Impossible d'envoyer a l'imprimante")
            # Envoyer l'image à l'imprimante

             # ------------------- GUI -------------------
            # Affiche le QR généré proportionnel
            update_qr_preview(im)

            # Met à jour la barre de progression
            count += 1
            progress_percent = int((count / total) * 100)
            update_progress_print(progress_percent)
            # Mettre à jour le label “QR actuel / total”
            label_count_print.config(text=f"{count} / {total}")
            root.update_idletasks()  # Force Tkinter à rafraîchir l’affichage
        
        messagebox.showinfo("Impression", "Impression terminée !")


# ------ appelle des fonctions principale -------
create_output_dir()
check_font()
create_temp_file()
# make_qrcode_text()
# print_send()


# ---------------------------------
# Fonctions GUI
# ---------------------------------

def select_files():
    global csv_file
    csv_file = filedialog.askopenfilename(
        title="CSV QRcode",
        filetypes=[('DataQR', '.csv')]
    )

    if csv_file:
        label_files.config(text=csv_file)
        btn_generate.config(state="normal")

def update_progress_gen(percent):
    progress_gen["value"] = percent
    root.update_idletasks()

def update_progress_print(percent):
    progress_print["value"] = percent
    root.update_idletasks()

def update_qr_preview(img):
    img_resize = img.resize((200, 200))
    tk_img = ImageTk.PhotoImage(img_resize)
    label_qr.config(image=tk_img)
    label_qr.image = tk_img  # éviter le garbage collector

# def print_list():
#     if not generated_qrs:
#         messagebox.showerror("Erreur", "Aucun QR généré")
#         return

#     progress_print["value"] = 0
#     total = len(generated_qrs)

#     for i, img in enumerate(generated_qrs):
#         show_qr_image(img)
#         time.sleep(0.2)

#         progress = int((i + 1) / total * 100)
#         progress_print["value"] = progress
#         root.update_idletasks()

#     messagebox.showinfo("Impression", "Impression terminée !")

def show_qr_image(img):
    global tk_qr
    max_size = 200  # taille du cadre

    # Récupère la taille originale
    w, h = img.size
    ratio = min(max_size / w, max_size / h)  # ratio pour ne pas dépasser 200x200
    new_w = int(w * ratio)
    new_h = int(h * ratio)

    # Redimensionne l'image avec le ratio
    img_resized = img.resize((new_w, new_h), Image.ANTIALIAS)

    # Crée un fond blanc carré de 200x200
    canvas = Image.new("RGB", (max_size, max_size), "white")

    # Centre l'image redimensionnée dans le carré
    x = (max_size - new_w) // 2
    y = (max_size - new_h) // 2
    canvas.paste(img_resized, (x, y))

    # Convertir en PhotoImage pour Tkinter
    tk_qr = ImageTk.PhotoImage(canvas)
    label_qr.config(image=tk_qr)
    label_qr.image = tk_qr  # éviter le garbage collector

# ---------------------------------------
# GUI
# ---------------------------------------

root = tk.Tk()
root.title("QL-Brother-label-print")
frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

# Bouton sélection fichiers
btn_select = tk.Button(frame, text="Sélectionner fichiers", command=select_files)
btn_select.grid(row=0, column=0, pady=10, sticky="w")

# Label nombre fichiers
label_files = tk.Label(frame, text="pas de fichier CSV")
label_files.grid(row=0, column=1, padx=10)

# Bouton générer
btn_generate = tk.Button(
    frame,
    text="Générer QR Codes",
    command=lambda: make_qrcode_text(update_progress_gen, update_qr_preview)
)
btn_generate.grid(row=1, column=0, pady=10)

# Bouton imprimer
btn_print = tk.Button(
    frame,
    text="Imprimer la liste",
    command=lambda: print_send(update_progress_print, update_qr_preview),
    state="disabled"
    )
btn_print.grid(row=1, column=1, pady=10)

# Progression génération
tk.Label(frame, text="Progression Génération :").grid(row=2, column=0, sticky="w")
progress_gen = ttk.Progressbar(frame, length=250)
progress_gen.grid(row=2, column=1, pady=10)

# Label QR actuel / total à côté de la barre de progression
label_count_gen = tk.Label(frame, text="0 / 0")
label_count_gen.grid(row=2, column=2, padx=10, sticky="w")  # même row que la barre, à droite

# Progression impression
tk.Label(frame, text="Progression Impression :").grid(row=3, column=0, sticky="w")
progress_print = ttk.Progressbar(frame, length=250)
progress_print.grid(row=3, column=1, pady=10)

# Label QR actuel / total à côté de la barre d'impression
label_count_print = tk.Label(frame, text="0 / 0")
label_count_print.grid(row=3, column=2, padx=10, sticky="w")  # même row que la barre, à droite


# Zone image QR
label_qr = tk.Label(frame)
label_qr.grid(row=4, column=0, columnspan=2, pady=20)

# Image décorative
decorate_img = Image.open("img.png")  # Mets ton image ici
decorate_img = decorate_img.resize((150, 150))
decorate_photo = ImageTk.PhotoImage(decorate_img)
tk.Label(frame, image=decorate_photo).grid(row=0, column=3, rowspan=3, padx=20)

root.mainloop()
