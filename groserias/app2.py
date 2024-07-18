from flask import Flask, request, render_template
import re
from autocorrect import Speller

app = Flask(__name__)

# Inicializar el corrector ortográfico
spell = Speller(lang='es')

# Mapa de sustituciones de números a letras
num_to_letter = {
    '0': 'o',
    '1': 'i',
    '2': 'z',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '6': 'g',
    '7': 't',
    '8': 'b',
    '9': 'g'
}

# Lista de groserías comunes en español, incluyendo formas plurales
groserias = [
    'cabrón', 'cabrones', 'cagada', 'cagadas', 'chinga', 'chingas', 'chingada', 'chingadas',
    'coño', 'coños', 'culero', 'culeros', 'culpa', 'culpas', 'desmadre', 'desmadres',
    'estúpido', 'estúpidos', 'huevón', 'huevones', 'idiota', 'idiotas', 'jodido', 'jodidos',
    'madre', 'madres', 'mierda', 'mierdas', 'pendejo', 'pendejos', 'pendeja', 'pendejas',
    'perra', 'perras', 'pinche', 'pinches', 'puta', 'putas', 'puto', 'putos', 'verga', 'vergas'
]

groserias.sort()

def corregir_errores(texto):
    palabras = texto.split()
    palabras_corregidas = []
    for palabra in palabras:
        # Sustituir números por letras correspondientes
        palabra_sustituida = ''.join([num_to_letter.get(char, char) for char in palabra])
        # Aplicar corrección ortográfica
        palabra_corregida = spell(palabra_sustituida)
        palabras_corregidas.append(palabra_corregida)
    return " ".join(palabras_corregidas)

def analizar_groserias(texto):
    contiene_groserias = False
    groserias_detectadas = []

    for palabra in groserias:
        patron = r'\b' + re.escape(palabra) + r'\b'
        if re.search(patron, texto, re.IGNORECASE):
            contiene_groserias = True
            groserias_detectadas.append(palabra)

    return contiene_groserias, groserias_detectadas

@app.route('/', methods=['GET', 'POST'])
def index():
    texto = None
    texto_corregido = None
    mensaje_error = None
    contiene_groserias = None
    groserias_detectadas = []

    if request.method == 'POST':
        texto = request.form['texto']
        if not texto.strip():
            mensaje_error = "Por favor, ingresa un texto válido."
        else:
            texto_corregido = corregir_errores(texto)
            contiene_groserias, groserias_detectadas = analizar_groserias(texto_corregido)

    return render_template('index2.html', texto=texto, texto_corregido=texto_corregido, 
                           mensaje_error=mensaje_error, contiene_groserias=contiene_groserias, 
                           groserias_detectadas=groserias_detectadas)

if __name__ == '__main__':
    app.run(debug=True)
