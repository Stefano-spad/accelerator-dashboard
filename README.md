# Base Accelerator — dashboard

Dashboard interactivo sobre los freelancers inscriptos al programa **Accelerator**
de Workana entre el 05/04/2023 y el 27/06/2023 (111 inscriptos, 17 países,
8 especialidades).

Responde cuántos se inscriben, de qué países, con qué especialidad, qué edad
tienen y cuánta antigüedad traían en la plataforma al anotarse. Todos los
gráficos, indicadores e insights se recalculan con los filtros de la barra
lateral.

## Contenido

| Archivo | Qué es |
|---|---|
| `app_accelerator.py` | La aplicación completa (Streamlit + Plotly). |
| `base_accelerator.csv` | Datos de origen: 111 filas, 7 columnas. |
| `workana_logo.svg` | Isotipo que se muestra arriba a la derecha. |
| `cooper_light.woff2` | Tipografía Cooper Light BT usada en títulos y KPIs. |
| `.streamlit/config.toml` | Tema de los controles de Streamlit. |
| `requirements.txt` | Dependencias. |

## Correr en la PC

```bash
pip install -r requirements.txt
streamlit run app_accelerator.py
```

## Columnas calculadas

Cuatro columnas no vienen en el CSV y se construyen al cargar los datos; el
criterio también está explicado dentro del dashboard:

- **País** — traduce el código ISO de 2 letras al nombre del país.
- **Días en Workana** — `fecha de inscripción` − `fecha de registro en Workana`.
- **Antigüedad** — Recién llegado (0 a 30 días), Nuevo (31 a 90),
  Con experiencia (91 a 365), Veterano (más de 365) y Revisar fecha
  (valores negativos).
- **Rango de edad** — tramos de 20 a 24, 25 a 29, 30 a 34 y 35 a 40 años.

## Diseño

Azul `#002D72` (PANTONE 288 C) de fondo, paneles en crema `#E8E8CA`
(PANTONE 7527 C) y lila `#DCB0E7` (PANTONE 243 C) como secundario. Las series
y los KPIs usan la paleta `#69DAB9`, `#FF699D`, `#5A85FF`, `#FFEB90` y
`#FF9655`. Tipografías: Cooper Light para títulos, Poppins para el resto.
El interruptor **Modo día** de la barra lateral invierte el par de fondos:
página crema con paneles blancos.
