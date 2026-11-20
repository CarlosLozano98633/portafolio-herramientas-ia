
import gradio as gr
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

# Cargar modelo y procesador
modelo_id = "google/mobilenet_v2_1.0_224"

procesador = AutoImageProcessor.from_pretrained(modelo_id)
modelo = AutoModelForImageClassification.from_pretrained(modelo_id)
modelo.eval()


def clasificar(imagen):
    if imagen is None:
        return {}

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

    return resultados


# Crear interfaz con Gradio
app = gr.Interface(
    fn=clasificar,
    inputs=gr.Image(type="pil", label="Sube una imagen"),
    outputs=gr.Label(num_top_classes=3, label="Predicciones"),
    title="Clasificador de imágenes con MobileNetV2",
    description="Sube una imagen para conocer las 3 clases más probables."
)

if __name__ == "__main__":
    app.launch()
