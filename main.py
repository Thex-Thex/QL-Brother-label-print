from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
import os.path

script_dir = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(script_dir, 'img.png'))
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
backend = 'pyusb'    # 'pyusb', 'linux_kernel', 'network'
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
    dpi_600=False,  # moins bonne qualite pour les codes barres si true
    hq=True,  # False for low quality.
    cut=True
)

send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)
