from flask import Flask, request, jsonify
import re
import spacy
from autocorrect import Speller

app = Flask(__name__)

# Cargar modelo de spacy para español
nlp = spacy.load("es_core_news_sm")

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
groserias_list = [
    'cabrón', 'cabrones', 'cagada', 'cagadas', 'chinga', 'chingas', 'chingada', 'chingadas',
    'coño', 'coños', 'culero', 'culeros', 'culpa', 'culpas', 'desmadre', 'desmadres',
    'estúpido', 'estúpidos', 'huevón', 'huevones', 'idiota', 'idiotas', 'jodido', 'jodidos',
    'madre', 'madres', 'mierda', 'mierdas', 'pendejo', 'pendejos', 'pendeja', 'pendejas',
    'perra', 'perras', 'pinche', 'pinches', 'puta', 'putas', 'puto', 'putos', 'verga', 'vergas'
]

groserias_list.sort()

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

    for palabra in groserias_list:
        patron = r'\b' + re.escape(palabra) + r'\b'
        if re.search(patron, texto, re.IGNORECASE):
            contiene_groserias = True
            groserias_detectadas.append(palabra)

    return contiene_groserias, groserias_detectadas

def extraer_habilidades(texto):
    texto_corregido = corregir_errores(texto)
    habilidades = []
    patrones = [
        (r'me gusta (.+?)(,| pero| y|\.|$)', False),
        (r'soy buena (.+?)(,| pero| y|\.|$)', False),
        (r'puedo (.+?)(,| pero| y|\.|$)', False),
        (r'no puedo (.+?)(,| pero| y|\.|$)', True),
        (r'no me gusta (.+?)(,| pero| y|\.|$)', True),
        (r'no soy buena (.+?)(,| pero| y|\.|$)', True),
    ]
    
    for patron, es_negacion in patrones:
        matches = re.findall(patron, texto_corregido)
        for match in matches:
            habilidad = match[0].strip()
            if es_negacion:
                habilidades = [h for h in habilidades if habilidad not in h]
            else:
                habilidades.append(habilidad)
    
    # Filtrar y formatear habilidades
    habilidades_formateadas = []
    for habilidad in habilidades:
        doc = nlp(habilidad)
        verbos = [token.lemma_ for token in doc if token.pos_ == 'VERB']
        objetos = [token.text for token in doc if token.dep_ == 'obj']
        
        if objetos:
            habilidad_formateada = ", ".join(verbos) + " (" + ", ".join(objetos) + ")"
        elif verbos:
            habilidad_formateada = ", ".join(verbos)
        else:
            habilidad_formateada = habilidad
        
        habilidades_formateadas.append(habilidad_formateada)
    
    return texto_corregido, habilidades_formateadas

@app.route('/habilidades', methods=['POST'])
def habilidades():
    data = request.get_json()
    texto = data.get('texto', '')
    texto_corregido, habilidades = extraer_habilidades(texto)
    return jsonify({'texto_corregido': texto_corregido, 'habilidades': habilidades})

@app.route('/groserias', methods=['POST'])
def groserias():
    data = request.get_json()
    texto = data.get('texto', '')
    texto_corregido = corregir_errores(texto)
    contiene_groserias, groserias_detectadas = analizar_groserias(texto_corregido)
    return jsonify({'texto_corregido': texto_corregido, 'contiene_groserias': contiene_groserias, 'groserias_detectadas': groserias_detectadas})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
