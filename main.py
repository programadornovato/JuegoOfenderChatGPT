# IMPORTAMOS LOS MÓDULOS NECESARIOS
from flask import Flask, render_template, request, session, jsonify
import pandas as pd
import random
import openai

# INICIAMOS LA APLICACIÓN FLASK
app = Flask(__name__)

# CONFIGURAMOS LA LLAVE SECRETA PARA LA SESIÓN
app.config['SECRET_KEY'] = 'tusecretkey'

# CARGAMOS LAS PREGUNTAS Y RESPUESTAS DEL ARCHIVO CSV AL INICIO DEL PROGRAMA
df = pd.read_csv('preguntas.csv')
preguntas = df['pregunta'].tolist()
respuestas = df['respuesta'].tolist()

# RUTA PARA OBTENER LA PREGUNTA
@app.route('/pregunta', methods=['GET'])
def pregunta():
    # SI NO HAY UNA PREGUNTA Y UNA RESPUESTA ACTUAL EN LA SESIÓN, SELECCIONA UNA ALEATORIAMENTE Y LA ELIMINA DE LA LISTA DE PREGUNTAS Y RESPUESTAS
    if 'pregunta_actual' not in session or 'respuesta_actual' not in session:
        idx = random.choice(range(len(preguntas)))
        pregunta_seleccionada = preguntas[idx]
        respuesta_seleccionada = respuestas[idx]
        preguntas.pop(idx)
        respuestas.pop(idx)
        session['pregunta_actual'] = pregunta_seleccionada
        session['respuesta_actual'] = respuesta_seleccionada
    # DEVUELVE LA PREGUNTA ACTUAL
    return jsonify(pregunta=session['pregunta_actual'])

# RUTA PARA PROCESAR LA RESPUESTA
@app.route('/respuesta', methods=['POST'])
def respuesta():
    # OBTIENE LA RESPUESTA ENVIADA POR EL USUARIO
    respuesta_usuario = request.form.get('respuesta_txt')
    openai.api_key = "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"
    model_engine = "gpt-3.5-turbo"
    # CONFIGURAMOS LA INTERACCIÓN CON EL MODELO DE OPENAI
    sistema = f'Soy un modelo de evaluación. Vas a hacer esta pregunta "{session["pregunta_actual"]}" y esta es la respuesta correcta "{session["respuesta_actual"]}". Comparando la respuesta del usuario con la correcta, solo debes decir "bien" si la respuesta del usuario es correcta o "mal" si no lo es.'
    
    # CREAMOS LA CONVERSACIÓN CON EL MODELO DE OPENAI
    response = openai.ChatCompletion.create(
    model=model_engine,
    messages=[
            {"role": "system", "content": sistema},
            {"role": "user", "content": "Respuesta del usuario: "+respuesta_usuario},
        ]
    )

    respuesta_modelo = ""
    # OBTENEMOS LA RESPUESTA DEL MODELO
    for message in response['choices'][0]['message']['content']:
        respuesta_modelo += message

    # REEMPLAZAMOS CIERTOS CARACTERES
    respuesta_modelo = respuesta_modelo.replace("\\n", "\n")
    respuesta_modelo = respuesta_modelo.replace("\\", "")

    # ELIMINAMOS LA PREGUNTA Y RESPUESTA ACTUAL DE LA SESIÓN
    session.pop('pregunta_actual', None)
    session.pop('respuesta_actual', None)

    # DEVOLVEMOS LA RESPUESTA DEL MODELO
    return jsonify(respuesta=respuesta_modelo)

# RUTA DE INICIO
@app.route('/')
def home():
    # RENDERIZAMOS LA PÁGINA DE INICIO
    return render_template('home.html')

# EJECUTAMOS LA APLICACIÓN
if __name__ == '__main__':
    app.run(debug=True)