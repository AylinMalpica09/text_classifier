from flask import Flask, request, render_template
import re
import spacy

# Inicializar la aplicación Flask
app = Flask(__name__)

# Cargar modelo de spacy para español
nlp = spacy.load("es_core_news_sm")

# Función para extraer habilidades
def extraer_habilidades(texto):
    habilidades = []
    negaciones = ['no', 'nunca', 'tampoco']
    patrones = [
        (r'me gusta (.+?)(,| pero| y|\.|$)', False),
        (r'soy buena (.+?)(,| pero| y|\.|$)', False),
        (r'no me gusta (.+?)(,| pero| y|\.|$)', True),
        (r'no soy buena (.+?)(,| pero| y|\.|$)', True),
    ]
    
    for patron, es_negacion in patrones:
        matches = re.findall(patron, texto)
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
    
    return habilidades_formateadas

# Definir la ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    texto = None
    mensaje_error = None
    habilidades = None
    
    if request.method == 'POST':
        texto = request.form['texto']
        if not texto.strip():
            mensaje_error = "Por favor, ingresa un texto válido."
        else:
            habilidades = extraer_habilidades(texto)
    
    return render_template('index2.html', texto=texto, mensaje_error=mensaje_error, habilidades=habilidades)

if __name__ == '__main__':
    app.run(debug=True)
