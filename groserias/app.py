from flask import Flask, request, render_template
import re
import spacy

app = Flask(__name__)
nlp = spacy.load("es_core_news_sm")

# Lista de groserías comunes en español, incluyendo formas plurales
groserias = [
    'cabrón', 'cabrones', 'cagada', 'cagadas', 'chinga', 'chingas', 'chingada', 'chingadas',
    'coño', 'coños', 'culero', 'culeros', 'culpa', 'culpas', 'desmadre', 'desmadres',
    'estúpido', 'estúpidos', 'huevón', 'huevones', 'idiota', 'idiotas', 'jodido', 'jodidos',
    'madre', 'madres', 'mierda', 'mierdas', 'pendejo', 'pendejos', 'pendeja', 'pendejas',
    'perra', 'perras', 'pinche', 'pinches', 'puta', 'putas', 'puto', 'putos', 'verga', 'vergas'
]

groserias.sort()

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
    mensaje_error = None
    contiene_groserias = None
    groserias_detectadas = []

    if request.method == 'POST':
        texto = request.form['texto']
        if not texto.strip():
            mensaje_error = "Por favor, ingresa un texto válido."
        else:
            contiene_groserias, groserias_detectadas = analizar_groserias(texto)

    return render_template('index.html', texto=texto, mensaje_error=mensaje_error, 
                           contiene_groserias=contiene_groserias, groserias_detectadas=groserias_detectadas)

if __name__ == '__main__':
    app.run(debug=True)
