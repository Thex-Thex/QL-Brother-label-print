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
