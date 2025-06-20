# Entregable Final: Proyecto de Análisis de Datos Financieros para Power BI

## Introducción

Este proyecto se centra en el manejo de datos del índice S&P 500 y la cartera de Berkshire Hathaway, procesándolos para su posterior visualización y análisis en Power BI, y vincula directamente las funcionalidades implementadas con los contenidos de cada unidad del curso.

A continuación, se detalla la implementación de los objetivos propuestos, comenzando con el primer objetivo relacionado con la validación de datos, y se explica cómo cada componente del proyecto refleja los aprendizajes de las unidades temáticas de la asignatura.

## Objetivo 1: Implementación de un Paso de Validación de Datos de Entrada (Unidad 1 - Introducción al Análisis de Datos)

### Descripción del Objetivo

El primer objetivo de este proyecto consiste en implementar un paso de validación de datos de entrada en los scripts de procesamiento de datos financieros. Este paso asegura la integridad de los datos antes de su transformación y análisis, verificando la presencia de valores faltantes o inválidos en los archivos CSV que contienen información del índice S&P 500, empresas del S&P 500 y la cartera de Berkshire Hathaway. Este proceso es fundamental para garantizar la calidad de los datos, un pilar esencial en cualquier análisis de datos.

### Implementación Técnica

- **Función `validate_input_data(df, dataset_name)`**: Esta función identifica columnas críticas para cada conjunto de datos (por ejemplo, 'Date' y 'Close' para el índice S&P 500) y realiza dos verificaciones principales:
  - Detecta valores faltantes en columnas esenciales, informando la cantidad de datos ausentes por columna.
  - Verifica que los tipos de datos sean correctos, asegurando que columnas numéricas como 'Close' contengan solo valores numéricos válidos.
- **Integración en el Flujo de Procesamiento**: La validación se ejecuta inmediatamente después de leer los datos en las funciones `process_sp500_index_data()`, `process_sp500_companies_data()` y `process_berkshire_portfolio_data()`. Si se detectan problemas, se genera un mensaje de advertencia, pero el procesamiento continúa para permitir la generación de resultados parciales.
- **Registro de Resultados**: Se implementó una función `log(message)` que registra mensajes con marca de tiempo en la consola, proporcionando trazabilidad de los problemas de calidad de datos detectados.

### Relación con la Unidad 1 - Introducción al Análisis de Datos

Este objetivo refleja los conceptos fundamentales aprendidos en la Unidad 1, específicamente:

- **Ciclo de Vida del Análisis de Datos**: La validación de datos corresponde a las etapas iniciales de recolección y limpieza de datos, asegurando que los datos sean aptos para análisis posteriores, como se presenta en las diapositivas "Análisis de Datos I - Introducción.pdf".
- **Importancia de la Calidad de Datos**: Al identificar y reportar datos faltantes o inválidos, se pone en práctica la necesidad de garantizar la integridad de los datos para obtener resultados confiables.
- **Tipos de Datos**: La verificación de tipos (cuantitativos como precios de cierre) demuestra la comprensión de cómo los diferentes tipos de datos requieren tratamientos específicos durante la limpieza y preparación.

### Ubicación en el Código

- **Validación de Datos**: Función `validate_input_data()` en las líneas correspondientes de 'powerbi_integration/powerbi_data_export.py' y 'powerbi_integration/powerbi_data_export_test.py'.
- **Integración en Procesamiento**: Llamadas a la función de validación al inicio de cada función de procesamiento en ambos scripts.

## Objetivo 2: Integración de SQLAlchemy para Almacenamiento y Consulta de Bases de Datos (Unidad 2 - SQL)

### Descripción del Objetivo

El segundo objetivo de este proyecto consiste en integrar SQLAlchemy para crear una base de datos SQLite local y almacenar los datos procesados del S&P 500 y la cartera de Berkshire Hathaway en tablas estructuradas después de su ingestión desde archivos CSV. Además, se implementan consultas básicas SELECT para filtrar datos (por ejemplo, por fecha o sector) antes de exportarlos a CSV para Power BI. Este paso demuestra habilidades avanzadas en bases de datos con un enfoque práctico y de mínima configuración.

### Implementación Técnica

- **Configuración de SQLAlchemy**: Se configuró un motor de base de datos SQLite en `powerbi_data_export.py` utilizando SQLAlchemy, creando una base de datos local en `powerbi_integration/output/financial_data.db`.
- **Definición de Esquema**: Se definieron tres tablas (`sp500_index`, `sp500_companies`, `berkshire_portfolio`) con columnas específicas para cada conjunto de datos, como `Date`, `Close`, `Sector`, etc., asegurando una estructura relacional adecuada.
- **Almacenamiento de Datos**: Cada función de procesamiento (`process_sp500_index_data()`, `process_sp500_companies_data()`, `process_berkshire_portfolio_data()`) fue modificada para limpiar los datos existentes en la base de datos y almacenar los datos procesados mediante operaciones de inserción masiva con SQLAlchemy.
- **Consultas Básicas**: Se implementaron consultas SELECT de ejemplo, como filtrar datos del índice S&P 500 por el último año, obtener sectores distintos de empresas del S&P 500, y seleccionar las principales participaciones de Berkshire Hathaway por valor, demostrando capacidades de filtrado y ordenamiento.
- **Registro de Operaciones**: Se utilizó un sistema de logging para registrar operaciones de base de datos, proporcionando trazabilidad de inserciones y consultas en la consola.
- **Pruebas Funcionales**: Se creó un archivo de pruebas `powerbi_data_export_db_test.py` para validar la conexión a la base de datos, la creación de esquemas, el almacenamiento de datos y las capacidades de consulta, asegurando la integridad de la integración.

### Relación con la Unidad 2 - SQL

Este objetivo refleja los conceptos fundamentales aprendidos en la Unidad 2, específicamente:

- **Conceptos Básicos de SQL**: La definición de tablas y el uso de consultas SELECT para filtrar datos (por ejemplo, por año o sector) aplican directamente los conocimientos de declaraciones SELECT, filtrado con WHERE y operaciones de ordenamiento, como se presenta en "Unidad 2 - SQL.pdf".
- **Gestión de Bases de Datos Relacionales**: El uso de SQLAlchemy para crear y gestionar una base de datos SQLite demuestra habilidades prácticas en el diseño de esquemas y almacenamiento estructurado de datos.
- **Integración con Python**: La combinación de SQLAlchemy con Python refleja cómo las operaciones de base de datos pueden integrarse en flujos de trabajo de análisis de datos, un aspecto clave para proyectos de datos a mayor escala.

### Ubicación en el Código

- **Configuración de Base de Datos**: Configuración de SQLAlchemy y definición de tablas en las líneas iniciales de `powerbi_integration/powerbi_data_export.py`.
- **Almacenamiento y Consulta de Datos**: Secciones de almacenamiento y consulta dentro de las funciones de procesamiento en `powerbi_integration/powerbi_data_export.py`.
- **Pruebas**: Archivo de pruebas funcionales en `powerbi_integration/powerbi_data_export_db_test.py`.

## Conexión con Otras Unidades del Curso

Aunque los Objetivos 1 y 2 se centran en las Unidades 1 y 2, el proyecto en su conjunto está diseñado para abarcar todas las unidades del curso "Análisis de Datos 1", y se describen a continuación cómo las funcionalidades actuales y planificadas del código se relacionan con cada unidad:

- **Unidad 2 - SQL**: Se ha implementado el uso de SQLAlchemy para almacenar datos procesados en una base de datos SQLite y realizar consultas SELECT para filtrar datos antes de exportarlos a Power BI. Esto demuestra habilidades en la gestión de bases de datos relacionales y consultas estructuradas, como se detalla en el Objetivo 2.
- **Unidad 3 - Python y Datos**: Los scripts están desarrollados en Python, utilizando bibliotecas como Pandas para la manipulación de datos (por ejemplo, cálculo de medias móviles y retornos en `process_sp500_index_data()`). Esto refleja el uso de estructuras de datos, funciones y control de flujo aprendidos en ejercicios como "📚_01_Ejercicios_Basico.ipynb".
- **Unidad 4 - Ingeniería de Datos**: El flujo de procesamiento en los scripts representa un pipeline ETL básico (Extracción de CSV, Transformación mediante cálculos, Carga a nuevos CSV). Se planea expandir esto con un pipeline más formal para ingerir datos en una base de datos, aplicando conceptos de "ETL_Pandas.ipynb".
- **Unidad 5 - Análisis Exploratorio de Datos (EDA)**: Actualmente, se calculan métricas como retornos diarios y anualizados en el índice S&P 500, lo cual es una forma básica de EDA. Se prevé añadir funciones para estadísticas descriptivas (media, mediana, desviación estándar) en el script de depuración, siguiendo ejemplos de "EDA_Titanic.ipynb".
- **Unidad 6 - Visualización de Datos**: El propósito final de los scripts es preparar datos para visualización en Power BI, generando archivos CSV optimizados para importar y crear dashboards interactivos. Esto se alinea con los objetivos de storytelling de datos y modelado en Power BI discutidos en "007_Data_Storytelling.pdf".

## Consideraciones Futuras para el Objetivo 1

Para mejorar la validación de datos implementada, se podrían incorporar umbrales configurables que definan un porcentaje aceptable de datos faltantes antes de considerar un conjunto de datos como no válido, así como verificaciones de valores atípicos que podrían distorsionar análisis posteriores. Estas mejoras reforzarían aún más los principios de limpieza de datos aprendidos en la Unidad 1.

## Consideraciones Futuras para el Objetivo 2

Para mejorar la integración de la base de datos, se podrían implementar consultas más avanzadas con JOIN para combinar datos de múltiples tablas (por ejemplo, relacionar datos de empresas del S&P 500 con el índice) y agregar índices a columnas frecuentemente consultadas para mejorar el rendimiento. Además, se podría explorar la migración a una base de datos más robusta como PostgreSQL para proyectos a mayor escala, aplicando conceptos avanzados de SQL.

## Conclusión

Este entregable demuestra la aplicación práctica de los conceptos de las Unidades 1 y 2 mediante la implementación de un paso de validación de datos y la integración de una base de datos con SQLAlchemy en un proyecto de procesamiento de datos financieros. A medida que se avancen los objetivos adicionales, se continuará documentando cómo cada unidad del curso se refleja en el desarrollo del proyecto, asegurando una cobertura integral de los aprendizajes adquiridos. Los scripts desarrollados no solo cumplen con los requisitos técnicos, sino que también sirven como una herramienta para conectar teoría y práctica, preparando datos de manera efectiva para análisis y visualización en Power BI.

## Referencias a Material del Curso

- Unidad 1: "Análisis de Datos I - Introducción.pdf" - Conceptos de ciclo de vida del análisis de datos y calidad de datos.
- Unidades 2-6: Materiales respectivos como "Unidad 2 - SQL.pdf", ejercicios de Python, notebooks de ETL y EDA, y documentos de visualización como "007_Data_Storytelling.pdf", que guían las implementaciones actuales y futuras.

## Descargo de Responsabilidad sobre Archivos No Relevantes

Los archivos y directorios fuera de la carpeta "powerbi_integration" y sus dependencias directas (como el directorio "data" para archivos CSV de entrada) no son considerados en el enfoque actual del proyecto, ya que no contribuyen directamente a los objetivos educativos establecidos. Esto incluye componentes como aplicaciones Streamlit, cuadernos de EDA independientes y otros directorios no relacionados.

Atentamente,  
[Nombre del Estudiante o Grupo]  
Curso: Análisis de Datos 1
