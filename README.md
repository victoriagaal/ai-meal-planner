# AI Budget Meal Planner for Students

## Integrantes
- Victoria Gaal


## Objetivo del proyecto
El objetivo del proyecto es desarrollar una aplicación interactiva en Python que ayude a estudiantes a generar recetas simples y económicas según los ingredientes disponibles, el presupuesto, el tiempo de preparación, la cantidad de porciones y las necesidades dietéticas.

## Usuario esperado
El programa está pensado principalmente para estudiantes o personas que quieren cocinar comidas rápidas, económicas y personalizadas.

## Descripción general
La aplicación permite al usuario ingresar ingredientes y preferencias mediante un formulario. Luego, el sistema genera una receta utilizando una API de inteligencia artificial. Si la API está temporalmente limitada o no responde correctamente, el programa genera una receta básica de respaldo para que la aplicación siga funcionando.

## Funcionalidades principales
- Ingreso de ingredientes disponibles
- Selección del tipo de comida
- Ingreso de restricciones dietéticas
- Tiempo máximo de preparación
- Cantidad de porciones
- Presupuesto máximo
- Generación de recetas mediante API
- Receta de respaldo si la API falla
- Resumen de preferencias con métricas y tabla
- Historial de recetas generadas
- Guardado de recetas durante la sesión
- Sustitución de ingredientes
- Exportación de recetas a PDF
- Manejo de errores y validación de entradas

## Fuente de datos
El programa no utiliza un dataset fijo. Trabaja con datos ingresados por el usuario y con respuestas generadas mediante una API externa de inteligencia artificial. En caso de error o límite temporal de la API, el sistema genera una receta básica de respaldo.

## Librerías utilizadas
- Streamlit
- Requests
- FPDF

## Diagramas de diseño
El repositorio incluye un diagrama de flujo llamado `diagram_flujo.jpeg`. El diagrama muestra el funcionamiento general del sistema, desde el ingreso de datos del usuario hasta la generación, guardado y exportación de recetas.

## Instrucciones para ejecutar el programa

1. Clonar o descargar el repositorio.

2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

3. Crear un archivo llamado `.streamlit/secrets.toml`.

4. Agregar la API key:

```toml
OPENROUTER_API_KEY = "your_api_key_here"
```

5. Ejecutar la aplicación:

```bash
streamlit run main.py
```

## Estructura del repositorio

```text
MEAL_PROJECT/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── diagram_flujo.jpeg
```

Nota: el archivo `.streamlit/secrets.toml` no debe subirse a GitHub porque contiene la API key.

## Funciones principales

- `get_meal_suggestions()`: realiza la llamada a la API de inteligencia artificial.
- `validate_inputs()`: valida las entradas principales del usuario.
- `build_recipe_prompt()`: construye el prompt enviado a la API.
- `create_fallback_recipe()`: genera una receta básica si la API está limitada o falla.
- `extract_recipe_title()`: extrae el título de la receta generada.
- `create_pdf()`: genera un archivo PDF con la receta guardada.
- `clean_filename()`: limpia el nombre del archivo PDF para evitar errores.

## Resultados y salidas del programa

El programa genera y muestra varias salidas:

- Receta generada en formato de texto
- Resumen de preferencias del usuario
- Métricas de tiempo, porciones y presupuesto
- Tabla resumen de entradas
- Historial de recetas
- Recetas guardadas
- Archivo PDF descargable

## Declaración de uso de IA

Se utilizó inteligencia artificial generativa durante el desarrollo del proyecto como apoyo para:

- organizar la estructura del programa
- mejorar la modularización del código
- diseñar funciones de validación
- mejorar el manejo de errores
- crear una estrategia de respaldo para errores de API
- redactar y revisar documentación

Ejemplos de prompts utilizados:

- How can I structure a Streamlit recipe planner app in modular Python functions?
- How can I validate user inputs in a Streamlit form?
- How can I handle API errors and rate limits in Python?
- How can I generate a PDF from text using Python?
- How can I document the use of AI in a programming project?

El código fue revisado, probado y adaptado por la integrante del proyecto. La autora comprende las partes principales del sistema.

## Limitaciones

- Las recetas generadas dependen de la disponibilidad de la API.
- Las recetas guardadas solo existen durante la sesión actual.
- El desglose nutricional depende de la respuesta generada y no utiliza una base de datos nutricional real.
- La receta de respaldo es básica y no tan personalizada como una respuesta generada por IA.