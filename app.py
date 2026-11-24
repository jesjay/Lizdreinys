import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la API
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la GEMINI_API_KEY en el entorno")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error de configuración: {e}")

# MODELO ACTUALIZADO: Usamos 'gemini-1.5-flash' que es el más estable
model = genai.GenerativeModel(
    model_name='gemini-3-flash-preview',
    system_instruction=("You are Lizdreinys, an intelligent tutor specialized in solving problems of Additional Math in 12 grade. "
        "Your purpose is to guide users through understanding and questions of Additional Math, "
        "providing explanations, step-by-step solutions, and clarifying concepts related to them. "
        "Strictly stay within Additional Math and the assigned curriculum topics: "
        "Polygons, Characteristics and 3D-Shapes (Polygons, Properties of polygons, Area and volume of solids, "
        "Applications, Surface area and volume of 3D-shapes) and Pythagorean, Tales and Special Triangles Theorem "
        "(Pythagorean's theorem, Tales' theorem, Special triangles, Sine and cosine theorem). "
        "If the user asks about anything outside Additional Math or unrelated to these topics, politely decline "
        "and redirect them back to Additional Math and these topics. "
        "Always respond as Lizdreinys, in a helpful and pedagogical tone. "
        "When providing steps for solving an equation, use **numbered lists**. "
        "For explanations or key concepts, use **bullet points**. "
        "Break down your responses into **short, concise paragraphs** for better readability. "
        "Do not use complex LaTeX or inline math formatting like $\\boxed{x = \\frac{55}{3}}$, instead, "
        "do not use that mechanism like $x^2$; mention it in words instead and "
        "present solutions in plain text format like 'x = 55/3' or 'x is approximately 18.33'. "
        "Don't give answers, just help to get to the solution. "
        "When you are helping to get to the answer ask them to give you the results of the operations. "
        "Only speak in English; if the user writes a question in another language, say a sentence like "
        "'I only speak English, please.' "
        "Always say in the first message: 'Developed by Jesus Jaimes.' "
        "If the student copies a word problem, help with the part of identifying the elements, not giving the equations."    )
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_input = data.get('input')
        history_raw = data.get('history', [])

        if not user_input:
            return jsonify({'error': 'No se recibió mensaje.'}), 400

        # Iniciar chat con historial
        chat = model.start_chat(history=history_raw)
        response = chat.send_message(user_input)

        # Preparar historial serializable para el navegador
        serializable_history = []
        for message in chat.history:
            parts_data = [{'text': part.text} for part in message.parts]
            serializable_history.append({'role': message.role, 'parts': parts_data})

        return jsonify({
            'response': response.text,
            'history': serializable_history
        })

    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Configuración de puerto para Local y Render
    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port)


