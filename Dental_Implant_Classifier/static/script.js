let cropper;

// Função para exibir a imagem e inicializar o cropper
function displayImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('preview');
        preview.src = e.target.result;
        preview.style.display = 'block';

        // Destrói o cropper anterior se existir
        if (cropper) {
            cropper.destroy();
        }

        // Inicializa o cropper com a nova imagem
        cropper = new Cropper(preview, {
            aspectRatio: NaN, // Permite cortar a imagem sem proporção fixa
            viewMode: 1, // Configura o modo de visualização para manter a imagem dentro da área visível
        });

        // Exibe o botão para recortar e identificar a imagem
        document.getElementById('cropAndPredictBtn').style.display = 'block';
    };
    reader.readAsDataURL(file); // Lê o arquivo como URL de dados
}

// Evento para o input de arquivo
document.getElementById('uploadImage').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        displayImage(file); // Exibe a imagem selecionada
    }
});

// Função para o drag and drop
const dropZone = document.getElementById('dropZone');

// Previne o comportamento padrão e adiciona estilo ao arrastar sobre a área
dropZone.addEventListener('dragover', function(event) {
    event.preventDefault();
    dropZone.classList.add('dragover');
});

// Remove o estilo ao sair da área de arrastar
dropZone.addEventListener('dragleave', function(event) {
    dropZone.classList.remove('dragover');
});

// Processa o arquivo ao soltar na área de arrastar
dropZone.addEventListener('drop', function(event) {
    event.preventDefault();
    dropZone.classList.remove('dragover');

    const file = event.dataTransfer.files[0];
    if (file) {
        displayImage(file); // Exibe a imagem solta
    }
});

// Abre o input de arquivo ao clicar na área de arrastar e soltar
dropZone.addEventListener('click', function() {
    document.getElementById('uploadImage').click();
});

// Evento para o botão de recortar e identificar
document.getElementById('cropAndPredictBtn').addEventListener('click', function() {
    if (cropper) {
        // Obtém o canvas da imagem cortada
        const canvas = cropper.getCroppedCanvas();
        canvas.toBlob(function(blob) {
            const formData = new FormData();
            formData.append('file', blob, 'recorte.png');

            // Envia a imagem cortada para o servidor
            fetch('/predict', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                // Limpa a tabela antes de adicionar novos resultados
                const resultBody = document.getElementById('resultBody');
                resultBody.innerHTML = '';

                // Adiciona os resultados na tabela
                for (const key in data) {
                    const row = document.createElement('tr');
                    const cellKey = document.createElement('td');
                    const cellValue = document.createElement('td');
                    cellKey.textContent = key;
                    cellValue.textContent = data[key];
                    row.appendChild(cellKey);
                    row.appendChild(cellValue);
                    resultBody.appendChild(row);
                }

                // Exibe a tabela de resultados
                document.getElementById('resultTable').style.display = 'table';
            })
            .catch(error => console.error('Erro:', error));
        });
    }
});
