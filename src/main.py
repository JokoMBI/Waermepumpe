import gc
import time
import neopixel
import colour
from machine import Pin

# LED channels and properties
np = neopixel.NeoPixel(Pin(15), 80)
np.ORDER = (1, 0, 2, 3)

def highlight(ledGroup, led):
    hl = ledGroup[led]
    diff = 255 - max(hl)
    hl = (hl[0] + diff, hl[1] + diff, hl[2] + diff)
    ledGroup[led] = hl

def dimmAll(ledGroup, dimmfactor):
    ''' uses scale factor for dimming '''
    for i in range(ledGroup.n):
        ledGroup[i] = (int(ledGroup[i][0] * dimmfactor), int(ledGroup[i][1] * dimmfactor), int(ledGroup[i][2] * dimmfactor))

def makeGrad(start_color, end_color, n):
    colorMap = [() for i in range(n)]
    if n > 1:
        step = (int((end_color[0] - start_color[0])/(n - 1)), int((end_color[1] - start_color[1])/(n - 1)), int((end_color[2] - start_color[2])/(n - 1)))
    else: step = (0, 0, 0)
    for i in range(n):
        colorMap[i] = ((start_color[0] + i*step[0], start_color[1] + i*step[1], start_color[2] + i*step[2]))
    return colorMap

def simloop(Param, CP=30, CE=30, D=1000):
    T1 = Param[0]
    T2 = Param[1]
    T3 = Param[2]
    T4 = Param[3]
    T5 = Param[4]
    T6 = Param[5]
    T7 = Param[6]
    T8 = Param[7]
    T9 = Param[8]
    TR = Param[9]
    Param[1] = T2 + (T1 - T2)/D + (T3 - T2)/(4*D)
    Param[2] = T3 + ((T4 + T5)/2 - T3)/D + (T2 - T3)/D
    Param[3] = T7 - CE
    Param[4] = T5 + ((T2 + T3)/2 - T5)/D + (T4 - T5)/D
    Param[5] = T5 + CP
    Param[6] = T7 + ((T8 + T9)/2 - T7)/D + (T6 -T7)/D
    Param[7] = T8 + (T9 - T8)/D + (TR -T8)/(2*D)
    Param[8] = T9 + ((T6 + T7)/2 - T9)/D
    Param[9] = TR + (T9 - TR)/(2*D)
    return Param

def main():
    ledData = [()]*np.n
    seg1 = [()]*25
    seg2 = [()]*30
    seg3 = [()]*24
    # Quelltemp-Position
    posT1 = 0
    # Kreis 1
    posT2 = 0
    posT3 = 4
    # Kreis 2
    posT4 = 0
    posT5 = 5
    posT6 = 15
    posT7 = 20
    # Kreis 3
    posT8 = 0
    posT9 = 5
    # Starttemp Erdkreis
    T1 = 10
    T2 = 5
    T3 = 5
    # Starttemp Zwischenkreis
    T5 = 5
    T6 = T5 + 30
    T7 = T6
    T4 = T7 - 30
    # Starttemp Heizkreis
    T8 = 10
    T9 = 10
    # Startwert Raumtemp
    TR = 10
    # init highlight LED
    h1 = 1
    h2 = len(seg1) + 0
    h3 = len(seg1) + len(seg2) + 0
    tempPoints = [T1, T2, T3, T4, T5, T6, T7, T8, T9, TR]
    while True:
        tempPoints = simloop(tempPoints)
        print(tempPoints)
        for data in tempPoints:
            if data < min(colour.TEMP_TO_COLOR):
                data = min(colour.TEMP_TO_COLOR)
            if data > max(colour.TEMP_TO_COLOR):
                data = max(colour.TEMP_TO_COLOR)
        # Erdkreis
        seg1[posT1] = colour.TEMP_TO_COLOR[round(tempPoints[0])]
        seg1[posT2 : posT3] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[1])], colour.TEMP_TO_COLOR[round(tempPoints[2])], posT3 - posT2)
        seg1[posT3:] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[2])], colour.TEMP_TO_COLOR[round(tempPoints[1])], len(seg1) - posT3)
        # Zwischenkreis
        seg2[posT4 : posT5] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[3])], colour.TEMP_TO_COLOR[round(tempPoints[4])], posT5 - posT4)
        seg2[posT5 : posT6] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[4])], colour.TEMP_TO_COLOR[round(tempPoints[5])], posT6 - posT5)
        seg2[posT6 : posT7] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[5])], colour.TEMP_TO_COLOR[round(tempPoints[6])], posT7 - posT6)
        seg2[posT7:] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[6])], colour.TEMP_TO_COLOR[round(tempPoints[3])], len(seg2) - posT7)
        # Heizkreis
        seg3[posT8 : posT9] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[7])], colour.TEMP_TO_COLOR[round(tempPoints[8])], posT9 - posT8)
        seg3[posT9:] = makeGrad(colour.TEMP_TO_COLOR[round(tempPoints[8])], colour.TEMP_TO_COLOR[round(tempPoints[9])], len(seg3) - posT9)        
        # fill LED data array
        gc.collect()
        ledData[:len(seg1)] = seg1
        ledData[len(seg1) : (len(seg1) + len(seg2))] = seg2
        ledData[(len(seg1) + len(seg2)) : (len(seg1) + len(seg2) + len(seg3))] = seg3
        ledData[-1] = colour.TEMP_TO_COLOR[round(tempPoints[-1])]
        for i in range(np.n):
            np[i] = ledData[i]
        dimmAll(np, 0.5)
        if h1 < len(seg1):
            h1 += 1
        else: h1 = 1
        if h2 < len(seg1) + len(seg2):
            h2 += 1
        else: h2 = len(seg1)
        if h3 < len(seg1) + len(seg2) + len(seg3)-1:
            h3 += 1
        else: h3 = len(seg1) + len(seg2)
        highlight(np, h1)
        highlight(np, h2)
        highlight(np, h3)
        np.write()
        time.sleep(0.05)
