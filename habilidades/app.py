from flask import Flask, request, render_template
import re
import spacy
from autocorrect import Speller

# Inicializar la aplicación Flask
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

# Función para corregir errores ortográficos
def corregir_errores(texto):
    texto_sustituido = ''.join([num_to_letter.get(char, char) for char in texto])
    palabras = texto_sustituido.split()
    palabras_corregidas = [spell(palabra) for palabra in palabras]
    return " ".join(palabras_corregidas)

# Función para extraer habilidades
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

# Definir la ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    texto = None
    texto_corregido = None
    mensaje_error = None
    habilidades = None
    
    if request.method == 'POST':
        texto = request.form['texto']
        if not texto.strip():
            mensaje_error = "Por favor, ingresa un texto válido."
        else:
            texto_corregido, habilidades = extraer_habilidades(texto)
    
    return render_template('index3.html', texto=texto, texto_corregido=texto_corregido, mensaje_error=mensaje_error, habilidades=habilidades)

if __name__ == '__main__':
    app.run(debug=True)
