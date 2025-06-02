# config/settings.py
TARGET_ARM = 'right' # ou 'left'

# Ângulo padrão para braço flexionado (topo do movimento do bíceps curl)
# Buscar uma contração forte do bíceps, geralmente entre 30-50 graus.
FLEXED_ANGLE_THRESHOLD_DEFAULT = 45 # Ajustado para um ângulo mais flexionado

# Ângulo padrão para braço estendido (base do movimento do bíceps curl)
# Buscar extensão completa sem travar o cotovelo, geralmente entre 160-175 graus.
EXTENDED_ANGLE_THRESHOLD_DEFAULT = 170 # Ajustado para um ângulo mais estendido

CALIBRATION_REPS = 3 # Número de repetições para a calibração