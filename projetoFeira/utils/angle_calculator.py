import numpy as np

def calculate_angle(a, b, c):
    """
    Calcula o ângulo em graus entre três pontos (a, b, c),
    com 'b' sendo o vértice do ângulo.
    """
    a = np.array(a) # Ombro
    b = np.array(b) # Cotovelo
    c = np.array(c) # Punho

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))

    if angle > 180.0:
        angle = 360 - angle

    return angle