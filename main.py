import streamlit as st
import requests
from fpdf import FPDF  # PDF generation

# Constants
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["OPENROUTER_API_KEY"]

# Cached AI call to avoid duplicate requests
@st.cache_data(show_spinner=False)
def get_meal_suggestions(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "Recipe Meal Planner"
    }
    data = {
        "model": "qwen/qwen3-next-80b-a3b-instruct:free",
        "messages": messages,
        "max_tokens": 600
    }
    resp = requests.post(API_URL, json=data, headers=headers, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"API error {resp.status_code}: {resp.text}")
    
    result = resp.json()

    try:
        content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise Exception(f"Respuesta inesperada de la API: {result}")

    if not content:
        raise Exception(f"La API no devolvió contenido de texto. Respuesta: {result}")

    return content

    

# PDF creation of saved recipes
def create_pdf(title: str, content: str) -> bytes:
    safe_title   = title.encode("latin-1", "ignore").decode("latin-1")
    safe_content = content.encode("latin-1", "ignore").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, safe_title, ln=1, align="C")
    pdf.ln(4)

    for line in safe_content.splitlines():
        text = line.strip()
        if not text:
            pdf.ln(2)
            continue
        if text.startswith("# "):
            heading = text[2:].strip()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, heading, ln=1)
        elif text.startswith("## "):
            heading = text[3:].strip()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 8, heading, ln=1)
        elif text.startswith("### "):
            heading = text[4:].strip()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, heading, ln=1)
        else:
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 6, text)

    return pdf.output(dest="S").encode("latin-1")

def validate_inputs(ingredients, meal_type, prep_time, portion_size):
    errors = []

    if not ingredients.strip():
        errors.append("Por favor ingresa al menos un ingrediente.")

    if not meal_type.strip():
        errors.append("Por favor indica el tipo de comida.")

    if prep_time and not prep_time.isdigit():
        errors.append("El tiempo de preparación debe ser un número en minutos.")

    if portion_size and not portion_size.isdigit():
        errors.append("La cantidad de porciones debe ser un número.")

    return errors


def build_recipe_prompt(
    ingredients,
    meal_type,
    dietary_needs,
    prep_time,
    portion_size,
    budget,
    tools,
    nutritional_breakdown,
    additional_preferences
):
    prompt = (
        "Eres un asistente de planificación de comidas útil y con conocimientos, "
        "con muchos años de experiencia en varios tipos de cocina.\n\n"
        "Generarás una receta personalizada basada en las preferencias y necesidades del usuario.\n\n"
        f"Ingredientes disponibles: {ingredients}\n"
        f"Tipo de comida: {meal_type}\n"
        f"Necesidades dietéticas: {dietary_needs}\n"
        f"Presupuesto máximo: {budget}\n"
        f"Tiempo máximo de preparación: {prep_time} minutos\n"
        f"Cantidad de porciones: {portion_size}\n"
        f"Utensilios no disponibles: {tools}\n"
        f"Desglose nutricional solicitado: {nutritional_breakdown}\n"
        f"Preferencias adicionales: {additional_preferences}\n\n"
        "Usa siempre el sistema métrico: gramos, litros, mililitros, etc.\n"
        "Puedes agregar ingredientes adicionales si es necesario, pero deben aparecer claramente "
        "en una sección titulada 'Lista de compras'.\n\n"
        "Estructura la respuesta exactamente de esta manera:\n"
        "# Título de la receta\n"
        "## Tiempo de preparación\n"
        "## Ingredientes\n"
        "## Herramientas\n"
        "## Instrucciones\n"
        "## Lista de compras\n\n"
        "Al final, añade una despedida cordial como '¡Buen provecho!'."
    )

    return prompt

def create_fallback_recipe(ingredients, meal_type, prep_time, portion_size, budget):
    return f"""
# Receta económica con {ingredients}

## Tiempo de preparación
Aproximadamente {prep_time} minutos.

## Ingredientes
- Ingredientes disponibles: {ingredients}
- Sal al gusto
- Aceite o mantequilla si está disponible
- Especias básicas opcionales

## Herramientas
- Sartén u olla
- Cuchillo
- Tabla de cortar
- Cuchara

## Instrucciones
1. Lava y prepara los ingredientes disponibles.
2. Corta los ingredientes en trozos pequeños.
3. Calienta una sartén u olla con un poco de aceite.
4. Cocina primero los ingredientes que tardan más.
5. Agrega el resto de los ingredientes y mezcla bien.
6. Ajusta la sal y las especias al gusto.
7. Sirve la comida caliente.

## Lista de compras
No se requieren ingredientes adicionales obligatorios. Si el presupuesto lo permite, puedes agregar verduras frescas, queso o una fuente extra de proteína.

¡Buen provecho!
"""

def extract_recipe_title(recipe_text):
    for line in recipe_text.splitlines():
        clean_line = line.strip()

        if clean_line:
            return clean_line.strip("# ").strip()

    return "Receta sin título"

def clean_filename(filename):
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
    cleaned = "".join(char for char in filename if char in allowed_chars)
    return cleaned.strip().replace(" ", "_") or "receta"


# Session state init
defaults = {
    "history": [],
    "saved": [],
    "latest_recipe": "",
    "latest_prompt": "",
    "latest_title": "",
    "messages": [],
    "substitute_mode": False,
    "ingredient_to_sub": "",
    "latest_inputs": {}
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# UI Setup
st.set_page_config(page_title="🍽️ Planificador de comidas para estudiantes", layout="wide")
st.title("👩‍🍳 Planificador de comidas para estudiantes")
st.subheader("Usa las pestañas para generar o ver recetas guardadas.")

# Sidebar: recipe history titles
st.sidebar.title("📜 Historia de Recetas")
if st.session_state.history:
    for i, title in enumerate(reversed(st.session_state.history)):
        st.sidebar.markdown(f"**{len(st.session_state.history) - i}.** {title}")
else:
    st.sidebar.info("Aún no hay recetas.")

# Two tabs: Generator & Saved
tab1, tab2 = st.tabs(["Generador de recetas", "Recetas guardadas"])

with tab1:
    st.subheader("Generar una nueva receta")
    with st.form("meal_form"):
        # Basic inputs
        ingredients = st.text_input("Ingredientes disponibles, separados por comas:")
        meal_type = st.text_input("Tipo de comida, por ejemplo cena, almuerzo o snack:")
        dietary_needs = st.text_input("Necesidades dietéticas, por ejemplo vegano o sin gluten:")
        prep_time = st.text_input("Tiempo máximo de preparación en minutos:")
        portion_size = st.text_input("Cantidad de porciones:")
        budget = st.text_input("Presupuesto máximo:")

        # Advanced options in an expander
        with st.expander("Opciones avanzadas"):
            tools = st.text_input("Utensilios de cocina que no tienes disponibles:")
            nutritional_breakdown = st.text_input("¿Quieres un desglose nutricional? Responde sí o no:")
            additional_preferences = st.text_input("Preferencias adicionales, por ejemplo bajo en grasas o alto en proteínas:")
        
        submitted = st.form_submit_button("Generar receta")

    if submitted:
        errors = validate_inputs(ingredients, meal_type, prep_time, portion_size)

        if errors:
            for error in errors:
                st.warning(error)
            st.stop()
        
        st.session_state.latest_inputs = {
            "Ingredientes": ingredients,
            "Tipo de comida": meal_type,
            "Necesidades dietéticas": dietary_needs if dietary_needs else "No indicado",
            "Tiempo máximo": prep_time if prep_time else "No indicado",
            "Porciones": portion_size if portion_size else "No indicado",
            "Presupuesto": budget if budget else "No indicado",
            "Preferencias adicionales": additional_preferences if additional_preferences else "No indicado"
        }
    
        user_prompt = build_recipe_prompt(
            ingredients,
            meal_type,
            dietary_needs,
            prep_time,
            portion_size,
            budget,
            tools,
            nutritional_breakdown,
            additional_preferences
        )

        messages = [{"role": "user", "content": user_prompt}]

        with st.spinner("🍳 Creando ideas..."):
            try:
                response = get_meal_suggestions(messages)
                st.session_state.latest_recipe = response

                # extract title
                title = extract_recipe_title(response)
                
                st.session_state.latest_title = title
                
                # store context & history
                st.session_state.latest_prompt = user_prompt
                st.session_state.messages      = [
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": response}
                ]
                st.session_state.history.append(title)

            except Exception as e:
                error_message = str(e)

                if "429" in error_message:
                    st.warning("La API está temporalmente limitada. Se generó una receta básica de respaldo.")

                    response = create_fallback_recipe(
                    ingredients,
                    meal_type,
                    prep_time,
                    portion_size,
                    budget
                    )

                    st.session_state.latest_recipe = response
                    title = extract_recipe_title(response)
                    st.session_state.latest_title = title
                    st.session_state.latest_prompt = user_prompt
                    st.session_state.messages = [
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": response}
                    ]
                    st.session_state.history.append(title)

                elif "402" in error_message:
                    st.error("La cuenta de la API no tiene créditos disponibles.")
                elif "404" in error_message:
                    st.error("El modelo seleccionado no está disponible. Revisa el nombre del modelo en el código.")
                else:
                    st.error(f"Error inesperado: {e}")

    # Display the generated recipe
    if st.session_state.latest_recipe:
        if st.session_state.latest_inputs:
            st.markdown("### 📌 Resumen de preferencias")

            col1, col2, col3 = st.columns(3)
            col1.metric("Tiempo máximo", st.session_state.latest_inputs.get("Tiempo máximo", "No indicado"))
            col2.metric("Porciones", st.session_state.latest_inputs.get("Porciones", "No indicado"))
            col3.metric("Presupuesto", st.session_state.latest_inputs.get("Presupuesto", "No indicado"))

            st.table({
                "Criterio": list(st.session_state.latest_inputs.keys()),
                "Valor": list(st.session_state.latest_inputs.values())
            })

        st.markdown("### 🍽️ Su sugerencia de comida")
        st.write(st.session_state.latest_recipe)

        # Substitution block
        with st.expander("🔁 Sustitución de ingredientes"):
            st.session_state.substitute_mode = st.checkbox("Quiero sustituir un ingrediente")
            if st.session_state.substitute_mode:
                st.session_state.ingredient_to_sub = st.text_input("¿Qué ingrediente le gustaría sustituir?")
                if st.button("Sugiera alternativas") and st.session_state.ingredient_to_sub:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"Me gustaría sustituir '{st.session_state.ingredient_to_sub}'. "
                                   "¿Puedes sugerir 2 o 3 alternativas y explicar por qué?"
                    })
                    try:
                        sub_resp = get_meal_suggestions(st.session_state.messages)
                        st.session_state.messages.append({"role": "assistant", "content": sub_resp})
                        st.markdown(f"### 🔄 Sustitución por '{st.session_state.ingredient_to_sub}'")
                        st.write(sub_resp)
                    except Exception as e:
                        st.error(f"Error durante la sustitución: {e}")

        # Save button
        if st.button("💾 Guardar esta receta"):
            st.session_state.saved.append({
                "title": st.session_state.latest_title,
                "content": st.session_state.latest_recipe
            })
            st.success("¡Receta guardada en tu biblioteca!")

        # Regenerate button
        if st.button("🔄 Generar otra receta"):
            st.session_state.messages.append({
                "role": "user",
                "content": "No me gustó la receta anterior. Por favor genera una nueva receta diferente manteniendo las preferencias del usuario."
            })

            with st.spinner("🌀 Generando una nueva receta..."):
                try:
                    new_resp = get_meal_suggestions(st.session_state.messages)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": new_resp
                    })

                    st.session_state.latest_recipe = new_resp

                    new_title = extract_recipe_title(new_resp)

                    st.session_state.latest_title = new_title
                    st.session_state.history.append(new_title)

                except Exception as e:
                    st.error(f"Error al regenerar la receta: {e}")

with tab2:
    st.subheader("📚 Tus recetas guardadas")
    if not st.session_state.saved:
        st.info("Aún no has guardado ninguna receta.")
    else:
        for idx, rec in enumerate(st.session_state.saved, 1):
            st.markdown(f"#### {idx}. {rec['title']}")
            st.write(rec["content"])
            pdf_bytes = create_pdf(rec["title"], rec["content"])
            st.download_button(
                label="📄 Descargar como PDF",
                data=pdf_bytes,
                file_name=f"{clean_filename(rec['title'])}.pdf",
                mime="application/pdf",
                key=f"pdf_{idx}"
            )
