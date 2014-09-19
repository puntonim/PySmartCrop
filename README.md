PySmartCrop
===========

Ottimizza le scansioni rimuovendo i bordi neri.

Requisiti
---------
Il programma è stato testato su Windows XP virtuale.
Serve Python 2.7 e le segg librerie: Numpy, Scipy, PIL, OpenCV (cv2).
Le librerie sono nell acartella libs.


Installazione su Windows
------------------------
- Installare python-2.7.6.msi
- Riavviare la macchina
- Installare numpy-1.6.2-win32-superpack-python2.7.exe
- Installare scipy-0.11.0-win32-superpack-python2.7.exe
- Installare PIL-1.1.7.win32-py2.7.exe
- Riavviare la macchina
- Copiare cv2.pyd in C:\Python27\Lib\site-packages
- Aprire una shell python e provare che tutto funzioni:
- import numpy
- import scipy
- import PIL
- import cv2


Installazione su Mac
--------------------
Questo è il risultato di un tentativo non completato.
$ mkvirtualenv /usr/bin/python2.7 smartcrop
$ pip install cython
$ pip install https://github.com/numpy/numpy/archive/master.zip
$ pip install https://github.com/scipy/scipy/archive/master.zip
If while installing scipy it says: "error: library dfftpack has Fortran sources but no Fortran compiler found"
Then install it from here:
https://gcc.gnu.org/wiki/GFortranBinaries
$ pip install pillow
$ brew tap homebrew/science
$ brew install opencv
If you cannot "import cv2" in Python:
  cd /System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/
  sudo ln -s /usr/local/Cellar/opencv/2.4.9/lib/python2.7/site-packages/cv.py .
  sudo ln -s /usr/local/Cellar/opencv/2.4.9/lib/python2.7/site-packages/cv2.so .


TODO
----
- Deskew (raddrizzamento): vedi commenti iniziali nel codice dello script
- Miglioramenti dell'immagine (contrasto, maschera di contrasto): vedi commenti iniziali nel codice dello script

Info: vedi questo cosa per ritagliare a mano un pdf, è manuale ma molto bello:
http://www.pdfscissors.com/