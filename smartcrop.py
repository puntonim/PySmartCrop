import os
import sys
import numpy
import cv2 as cv
from PIL import Image, ImageOps, ImageDraw
from scipy.ndimage import morphology
from scipy.ndimage.measurements import label
from scipy.misc import imsave

"""
Creare le cartelle:
C:\\workspace\\smartcrop\\test\\grigenew
C:\\workspace\\smartcrop\\test\\finenew
Mettere le immagini (gia convertite in scala di grigi) in grigenew

TODO: si potrebbe aggoingere il deskew (raddrizzamente) in fase di preprocessing,
Non so bene come farlo in Python (bisogna usare opencv)
L'ho cercato in internet e l'unica cosa che ho trovato sono qs link in C++:
http://felix.abecassis.me/2011/09/opencv-detect-skew-angle/
http://felix.abecassis.me/2011/10/opencv-rotation-deskewing/
L'avevo fatto in Java così: vedi cartella TODO Come fare il deskew in Java

TODO: si potrebbero implementare dei miglioramenti sull'immagine come aumento del contrasto e maschera di contrasto) anche
Si possono fare ste cose con Python e OpenCV qui, ma non so bene come
Oppure si puo usare Imagemagick, vedi: Imagemagick.txt nella cartella FOTOEDITING, VIDEOEDITING 
"""

PROJECT_FOLDER = os.path.abspath(os.path.dirname("C:\\workspace\\smartcrop\\test\\").decode("utf-8"))
GRAY_FOLDER = os.path.join(PROJECT_FOLDER, 'grigenew')
END_FOLDER = os.path.join(PROJECT_FOLDER, 'finenew')

SAVE_INTERMEDIATE_STEPS = False
DO_NOT_CROP_BUT_BOUND = False

def smart_crop(in_path, out_path):
    img_orig = Image.open(in_path)
    img = ImageOps.grayscale(img_orig)
    im = numpy.array(img, dtype=numpy.uint8)
    
    # Preprocessing the image
    im = pre_process_image(img, in_path)
    #im = pre_process_image(im)
    
    # Statistical analysis
    col_sum = numpy.sum(im, axis=0)
    row_sum = numpy.sum(im, axis=1)
    col_mean, col_std = col_sum.mean(), col_sum.std()
    row_mean, row_std = row_sum.mean(), row_sum.std()
    
    row_standard = (row_sum - row_mean) / row_std
    col_standard = (col_sum - col_mean) / col_std
    
    def end_points(s, std_below_mean=-1.5):
        i, j = 0, len(s) - 1
        for i, rs in enumerate(s):
            if rs > std_below_mean:
                break
        for j in xrange(len(s) - 1, i, -1):
            if s[j] > std_below_mean:
                break
        return (i, j)
    
    # Bounding rectangle
    x1, x2 = end_points(col_standard)
    y1, y2 = end_points(row_standard)
    
    if not DO_NOT_CROP_BUT_BOUND:
        # Crop
        result = img.crop((x1, y1, x2, y2))
    else:
        # Bound
        result = img.convert('RGB')
        draw = ImageDraw.Draw(result)
        draw.line((x1, y1, x2, y1, x2, y2, x1, y2, x1, y1),
                fill=(0, 255, 255), width=15)
    
    # Save the final image
    result.save(out_path)



def pre_process_image(img, path=None):
    if path: file_name, file_ext = os.path.splitext(os.path.basename(path))

    # MORPHOLOGY CLOSING
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.grey_closing.html#scipy.ndimage.morphology.grey_closing
    # http://en.wikipedia.org/wiki/Mathematical_morphology
    #
    # Cancellare ogni lettera e imperfezione
    # Parametri: qui uso il metodo nella sua forma base dove il secondo parametro e' un rettangolo (altezza, larghezza)
    # Secondo me teoricamente dovrei matchare la dimesnione media di una parola (una lettera e' troppo piccolo, una riga e' troppo grande)
    #
    #orig#im = morphology.grey_closing(img, (1, 101))
    im = morphology.grey_closing(img, (15, 105)) #odd numbers are better
    if path and SAVE_INTERMEDIATE_STEPS: imsave(os.path.join(END_FOLDER, '%s_step1%s' % (file_name, file_ext)), im)

    # OTSU THRESHOLDING (statistically optimal)
    # http://docs.opencv.org/modules/imgproc/doc/miscellaneous_transformations.html#threshold
    # http://en.wikipedia.org/wiki/Otsu%27s_Method
    #
    # Trasformare l'immagine in due colori: nero per lo sfondo, bianco per il primo piano
    # Parametri: 0, 1 (valore per sfondo e primo piano) in produzione
    # 0, 255 se volgio vedere l'immagine in bianco e nero per debug
    #
    #orig#t, im = cv.threshold(im, 0, 1, cv.THRESH_OTSU)
    t, im = cv.threshold(im, 0, 255, cv.THRESH_OTSU)
    if path and SAVE_INTERMEDIATE_STEPS: imsave(os.path.join(END_FOLDER, '%s_step2%s' % (file_name, file_ext)), im)
    
    # MORPHOLOGY OPENING
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.grey_opening.html#scipy.ndimage.morphology.grey_opening
    # http://en.wikipedia.org/wiki/Mathematical_morphology
    #
    # Cancellare i sottili bordi bianchi 
    # Parametri: qui uso il metodo nella sua forma base dove il secondo parametro e' un rettangolo (altezza, larghezza)
    # Le dimensioni del rettangolo sono un quadrato di lato = dimesnione minima delpiu grosso extra bordo bianco
    #
    #origl# im = morphology.grey_opening(im, (51, 51))
    im = morphology.grey_opening(im, (51, 51)) #odd numbers are better
    if path and SAVE_INTERMEDIATE_STEPS: imsave(os.path.join(END_FOLDER, '%s_step3%s' % (file_name, file_ext)), im)
    
    # CONNECTED-COMPONENT LABELING
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.measurements.label.html#scipy.ndimage.measurements.label
    # http://en.wikipedia.org/wiki/Connected-component_labeling
    #
    # Divido l'immagine (che ora e' teoricamente pulita di tutto il testo) in sotto immagini
    # Mantengo solo la sotto immagine piu grossa perche' dovrebbe essere la pagina (il resto lo coloro di nero)
    #
    # Il risultato puo essere:
    #  1 sotto img: caso perfetto, la sotto immagine e' il foglio (il resto e' lo sfondo che non conta, cioe' il bordo nero)
    #  2, 3, 4, 5 img: probabilmente c'e' un extra bordo bianco di disturbo su 1,2,3 o 4 lati
    #  6+ img: la pagina contiene delle immagini grosso che sono state suddivise
    #
    # Label divide l'immagine in sottoimmagini e assegna un numero ad ogni pixel (0 e' lo sfondo)
    # Tutti i pixel che hanno lo stesso numero fanno parte della stessa sotto immagine
    #
    # Restituisce:
    #  una matrice di dimensione uguale all'immagine sorgente dove ogni pixel ha un label
    #  il numero di sotto immagini identificate
    #
    lbl, ncc = label(im)
    # Identifico la sotto immagine piu grossa
    largest = 0, 0
    for i in range(1, ncc + 1):
        size = len(numpy.where(lbl == i)[0]) #counts how many times the value i is present in the lbl array
        if size > largest[1]:
            largest = i, size
    # Imposto il colore 0 a tutte le sottoimmagini tranne quell apiu grossa
    for i in range(1, ncc + 1):
        if i == largest[0]:
            continue
        im[lbl == i] = 0
        #Se volessi colorare le sotto immagini in scala di grigi
        #import math##
        #im[lbl == i] = math.floor(255/ncc-1)*ncc
    if path and SAVE_INTERMEDIATE_STEPS: imsave(os.path.join(END_FOLDER, '%s_step4%s' % (file_name, file_ext)), im)###################
    return im


if __name__ == "__main__":
    #Creating the END_FOLDER
    os.chdir(PROJECT_FOLDER)
    if not os.path.exists(END_FOLDER): os.makedirs(END_FOLDER)
        
    folder = os.listdir(GRAY_FOLDER)
    for file in folder:
        print "Processando %s..." % file,
        if not os.path.isfile(os.path.join(GRAY_FOLDER, file)):
            continue
        filein = os.path.join(GRAY_FOLDER, file)
        fileout = os.path.join(END_FOLDER, file)
        smart_crop(filein, fileout)
        print "fine."