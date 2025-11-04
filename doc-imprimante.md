# Documentation sur le fonctionnement du script de l'imprimante
## Description 
ce script permet d'imprimer une image sur une imprimante Brother modèle ```QL-820NWB``` connecter en USB sur un pc windows

### matériel utiliser
- imprimante ```QL-820NWB```
- rouleau autocollant de type ```DK-22210``` ou ```DK-22205```
- cable USB-B vers USB-A
- pc windows 11 (nuc + clavier + souris + écran)

### utilisation 
1. installer python `3.9` cocher add to PATH
2. cliquer sur disable PATH length limit 
3. installer les [drivers brother](https://support.brother.com/g/b/downloadend.aspx?c=ch&lang=fr&prod=lpql820nwbeuk&os=10069&dlid=dlfp101277_000&flang=185&type3=347) de l'imprimante
4. ouvrer l’installateur et ch
5. oisissez l'imprimante ici ``ql-820NWB``
6. sélectionner connection USB 
7. installer [libusb-win32-devel-filter](https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.7.3/)
8. executer le 
9. trouver l'imprimante ici `ql-820NWB`
10. cliquer dessus puis → détails → chemin d'accès au périphérique
11. ouvrer libusb puis install a device filter
12. trouver l'imprimante et install ![alt text](libusb.png)
13. aller sur le [dépôt github](https://github.com/Thex-Thex/QL-Brother-label-print/tree/img_print) et télécharger la branches `img_print`
14. installer les dépendances `pip install -R requirements.txt`
15. lancer le script
16. les données contenue dans id_place.csv seront imprimer sous la forme d'un QRcode suivie d'un text