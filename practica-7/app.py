
import gradio as gr
import torch
import time
from transformers import AutoImageProcessor, AutoModelForImageClassification

# Cargar modelo y procesador
modelo_id = "google/mobilenet_v2_1.0_224"

procesador = AutoImageProcessor.from_pretrained(modelo_id)
modelo = AutoModelForImageClassification.from_pretrained(modelo_id)
modelo.eval()


def clasificar(imagen):
    if imagen is None:
        return {}, "0.00 segundos"

    inicio = time.perf_counter()

    # Procesar la imagen
    entradas = procesador(images=imagen, return_tensors="pt")

    # Realizar predicción
    with torch.no_grad():
        salidas = modelo(**entradas)

    # Convertir resultados a probabilidades
    probabilidades = torch.softmax(salidas.logits, dim=-1)[0]

    # Obtener las 3 clases más probables
    valores, indices = torch.topk(probabilidades, 3)

    resultados = {}

    for valor, indice in zip(valores, indices):
        etiqueta = modelo.config.id2label[indice.item()]
        resultados[etiqueta] = valor.item()

    tiempo = time.perf_counter() - inicio
    return resultados, f"{tiempo:.2f} segundos"


# Crear interfaz con Gradio
app = gr.Interface(
    fn=clasificar,
    inputs=gr.Image(type="pil", label="Sube una imagen"),
    outputs=[
        gr.Label(num_top_classes=3, label="Predicciones"),
        gr.Textbox(label="Tiempo de procesamiento", interactive=False),
    ],
    title="¿Qué hay en la foto?",
    description="Esta aplicación usa el modelo google/mobilenet_v2_1.0_224.",
    examples=[
        "ejemplos/carro.jpg",
        "ejemplos/mi-foto.jpg",
    ]
)

if __name__ == "__main__":
    app.launch()
