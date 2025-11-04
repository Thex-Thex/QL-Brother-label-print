import qrcode
from PIL import Image

# Informations pour le QR code
classe = "Classe A"
numero_serie = "123456"
nom_eleve = "Jean Dupont"

# Combiner les informations dans une seule chaîne de texte
qr_data = f"Classe: {classe}\nNuméro de série: {numero_serie}\nNom de l'élève: {nom_eleve}"

# Créer l'objet QR code
qr = qrcode.QRCode(
    version=1,  # Taille du QR code (1 est la plus petite, peut être augmenté pour plus de données)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Niveau de correction d'erreur
    box_size=10,  # Taille des "cases" dans le QR code
    border=4,  # Taille de la bordure autour du QR code
)

# Ajouter les données au QR code
qr.add_data(qr_data)
qr.make(fit=True)

# Générer l'image du QR code
img = qr.make_image(fill_color="black", back_color="white")

# Enregistrer l'image en PNG
img.save("qrcode_temp.png")

print("QR code généré et enregistré sous 'qrcode_temp.png'")

from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
import os.path

script_dir = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(script_dir, 'qrcode_temp.png'))
# test du chemin de l'image
print("file-path = " + os.path.join(script_dir, 'img.png'))

# resize de l'image pour eviter gaspillage de ruban en cas de mauvaise
# dimension de l'image source si format portrait au lieu de paysage p.ex
# pas obligatoire
# im = im.resize((696, 60)) # pour rouleaux de 62mm 
# pour la hauteur possible d'utiliser 40 (min), 60, 80, etc...
# im = im.resize((566, 165)) # pour rouleaux de 54mm
# im = im.resize((413, 100))  # pour rouleaux de 38mm 

# backend = 'network'
backend = 'pyusb'    # 'pyusb', 'linux_kernal', 'network'
# model = 'QL-720NW'  # your printer model. (QL-720NW)
model = 'QL-820NWB'  # your printer model. (QL-820NWB)
# name of the printer on the network : BRN0080775EB896

# si imprimante connectée en USB
# Get these values from the Windows usb driver filter.
# Linux/Raspberry Pi uses '/dev/usb/lp0'.
# bus-0/\\.\libusb0-0001--0x04f9-0x209d     04F9/209D
printer = 'usb://0x04f9:0x209d'

#printer = 'tcp://10.12.1.118'  
#printer = 'tcp://192.168.1.107' 

qlr = BrotherQLRaster(model)
qlr.exception_on_warning = True

instructions = convert(
    qlr=qlr,
    images=[im],  # Takes a list of file names or PIL objects.
    # label='38',  
    # label='54',
    # label='62', 
    label='29', 
    rotate='0',  # 'Auto', '0', '90', '270'
    threshold=50.0,  # Black and white threshold in percent.
    dither=True,  # True = niveaux de gris, false = n/b
    compress=False,
    red=False,  # Only True if using Red/Black 62 mm label tape.
    dpi_600=False,  # moin bonne qualite pour les codes barres si true
    hq=True,  # False for low quality.
    cut=True
)

send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)
