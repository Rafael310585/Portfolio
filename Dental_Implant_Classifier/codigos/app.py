from flask_ngrok import run_with_ngrok
from flask import Flask, request, jsonify, send_from_directory
from pyngrok import ngrok  # Importação correta para usar set_auth_token e connect
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import pandas as pd
import numpy as np
import os

# Inicializa o Flask e o ngrok
app = Flask(__name__, static_folder='/content/drive/MyDrive/APP_IMP_1/static')

# Configure o token ngrok (substitua pelo seu token se necessário)
ngrok.set_auth_token('2l4Pi70RSdh97qV0CXKqTHPjqmB_22xYVdXom4ndmR2RSht5B')
run_with_ngrok(app)  # Inicializa o ngrok quando o app Flask for executado

# Caminhos dos arquivos
CSV_FILE = '/content/drive/MyDrive/APP_IMP_1/imagens_implantes.csv'
MODEL_PATH = '/content/drive/MyDrive/APP_IMP_1/modelo_implante.pth'
FEEDBACK_FILE = '/content/drive/MyDrive/APP_IMP_1/feedback_implantes.csv'

# Carregar dados do CSV
df = pd.read_csv(CSV_FILE)
class_to_idx = {marca: idx for idx, marca in enumerate(df['marca'].unique())}
idx_to_class = {idx: marca for marca, idx in class_to_idx.items()}
class_info = {row['marca']: {'modelo': row['modelo'], 'sistema': row['sistema'], 'compatibilidade': row['compatibilidade']} for _, row in df.iterrows()}

# Função para obter o modelo
def get_model(num_classes):
    model = models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, num_classes)
    return model

# Carregar o modelo treinado
def load_model(model_path):
    model = get_model(num_classes=len(class_to_idx))
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    model_state_dict = checkpoint.get('model_state_dict', checkpoint)
    model_dict = model.state_dict()
    state_dict = {k: v for k, v in model_state_dict.items() if k in model_dict}
    model_dict.update(state_dict)
    model.load_state_dict(model_dict)
    return model

model = load_model(MODEL_PATH)
model.eval()

# Transformações para a imagem
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Função para carregar e processar a imagem
def load_image(image_file):
    image = Image.open(image_file).convert('RGB')
    image = transform(image).unsqueeze(0)
    return image

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo fornecido'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    try:
        image = load_image(file)
        with torch.no_grad():
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
            predicted_class = idx_to_class.get(predicted.item(), 'Desconhecido')
            info = class_info.get(predicted_class, {})
            return jsonify({
                'implante_identificado': predicted_class,
                'modelo': info.get('modelo', 'Desconhecido'),
                'sistema': info.get('sistema', 'Desconhecido'),
                'compatibilidade': info.get('compatibilidade', 'Desconhecido')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicia o túnel ngrok
    public_url = ngrok.connect(5000, proto='http')
    print(f"URL pública do Flask: {public_url}")
    app.run()  # Correção: Remova os argumentos 'host' e 'port'
