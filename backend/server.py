from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(MONGO_URL)
db = client.casm83

# Pydantic models
class TestSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sex: str
    responses: List[Dict] = []
    created_at: str
    completed: bool = False
    completed_at: Optional[str] = None

class StartTestRequest(BaseModel):
    sex: str

class SaveResponseRequest(BaseModel):
    session_id: str
    question_number: int
    response: List[str]  # Can be ['A'], ['B'], ['A', 'B'], or []

class CompleteTestRequest(BaseModel):
    session_id: str

# Questions data - CASM-83 R2014
QUESTIONS = [
    {"number": 1, "block": 1, "optionA": "Le gusta resolver problemas de matemáticas", "optionB": "Prefiere diseñar el modelo de casas, edificios, parques, etc."},
    {"number": 2, "block": 1, "optionA": "Le agrada observar la conducta de las personas y opinar sobre su personalidad", "optionB": "Prefiere expresar un fenómeno concreto en una ecuación matemática"},
    {"number": 3, "block": 1, "optionA": "Le gusta caminar por los cerros buscando piedras raras", "optionB": "Prefiere diseñar viviendas de una Urbanización"},
    {"number": 4, "block": 1, "optionA": "Le gusta escribir artículos deportivos para un diario", "optionB": "Prefiere determinar la resistencia de los materiales para una construcción"},
    {"number": 5, "block": 1, "optionA": "Le gusta hacer tallado en madera", "optionB": "Prefiere calcular la cantidad de materiales para una construcción"},
    {"number": 6, "block": 1, "optionA": "Le gusta ordenar y archivar documentos", "optionB": "Prefiere proyectar el sistema eléctrico para una construcción"},
    {"number": 7, "block": 2, "optionA": "Le agrada dedicar su tiempo en el estudio de teorías económicas", "optionB": "Prefiere dedicar su tiempo en la lectura de revistas sobre mecánica"},
    {"number": 8, "block": 2, "optionA": "Le gusta mucho la vida militar", "optionB": "Prefiere diseñar: máquinas, motores, etc, de alto rendimiento"},
    {"number": 9, "block": 2, "optionA": "Le gusta estudiar acerca de cómo formar una cooperativa", "optionB": "Prefiere estudiar el lenguaje de computación IBM"},
    {"number": 10, "block": 2, "optionA": "Le agrada estudiar la gramática", "optionB": "Prefiere estudiar las matemáticas"},
    {"number": 11, "block": 2, "optionA": "Le interesa mucho ser abogado", "optionB": "Preferiría dedicarse a escribir un tratado de física-matemática"},
    {"number": 12, "block": 2, "optionA": "Le cuenta a su madre y a su padre todas sus cosas", "optionB": "Prefiere ocultar algunas cosas para Ud. solo (a)"},
    {"number": 13, "block": 2, "optionA": "Le agrada estudiar la estructura atómica de los cuerpos", "optionB": "Prefiere asumir la defensa legal de alguna persona acusada por algún delito"},
    {"number": 14, "block": 2, "optionA": "Le interesa mucho estudiar como funciona un computador", "optionB": "Prefiere el estudio de las leyes y principios de la conducta psicológica"},
    {"number": 15, "block": 2, "optionA": "Le agrada analizar la forma como se organiza un pueblo", "optionB": "Prefiere el estudio de las leyes y principios de la conducta psicológica"},
    {"number": 16, "block": 2, "optionA": "Le gusta analizar las rocas, piedras, tierra para averiguar su composición mineral", "optionB": "Prefiere el estudio de las organizaciones sean: campesinas, educativas, laborales, políticas, económicas o religiosas"},
    {"number": 17, "block": 2, "optionA": "Le gusta escribir artículos culturales para un diario", "optionB": "Prefiere pensar largamente acerca de la forma como el hombre podría mejorar su existencia"},
    {"number": 18, "block": 2, "optionA": "Le agrada diseñar: muebles, puertas, ventanas, etc", "optionB": "Prefiere dedicar su tiempo a conocer las costumbres y tradiciones de los pueblos"},
    {"number": 19, "block": 2, "optionA": "Le gusta mucho conocer el trámite documentario de un ministerio público", "optionB": "Prefiere el estudio de las religiones"},
    {"number": 20, "block": 2, "optionA": "Le interesa mucho conocer los mecanismos de la economía nacional", "optionB": "Prefiere ser guía espiritual de las personas"},
    {"number": 21, "block": 2, "optionA": "Le interesa mucho tener bajo su mando a un grupo de soldados", "optionB": "Prefiere enseñar lo que sabe a un grupo de compañeros"},
    {"number": 22, "block": 2, "optionA": "Le gusta ser parte de la administración de una cooperativa", "optionB": "Prefiere el estudio de las formas más efectivas para la enseñanza de jóvenes y niños"},
    {"number": 23, "block": 3, "optionA": "Le interesa mucho estudiar la raíz gramatical de las palabras de su idioma", "optionB": "Prefiere dedicar su tiempo en la búsqueda de huacos y ruinas"},
    {"number": 24, "block": 3, "optionA": "Le agrada mucho estudiar el código del derecho civil", "optionB": "Prefiere el estudio de las culturas peruanas y de otras naciones"},
    {"number": 25, "block": 3, "optionA": "Le agrada que sus hermanos o familiares lo vigilen constantemente", "optionB": "Prefiere que confíen en su buen criterio"},
    {"number": 26, "block": 3, "optionA": "Le gustaría escribir un tratado acerca de la historia del Perú", "optionB": "Prefiere asumir la defensa legal de un acusado por narcotráfico"},
    {"number": 27, "block": 3, "optionA": "Le gusta proyectar las redes de agua y desagüe de una ciudad", "optionB": "Prefiere estudiar acerca de las enfermedades de la dentadura"},
    {"number": 28, "block": 3, "optionA": "Le gusta visitar museos arqueológicos y conocer la vivienda y otros utensilios de nuestros antepasados", "optionB": "Prefiere hacer moldes para una dentadura postiza"},
    {"number": 29, "block": 3, "optionA": "Le gusta recolectar plantas y clasificarlas por especies", "optionB": "Prefiere leer sobre el origen y funcionamiento de las plantas y animales"},
    {"number": 30, "block": 3, "optionA": "Le gusta saber como se organiza una editorial periodística", "optionB": "Prefiere conocer las características de los órganos humanos y como funcionan"},
    {"number": 31, "block": 3, "optionA": "Le agrada construir; muebles, puertas, ventanas, etc.", "optionB": "Prefiere estudiar acerca de las enfermedades de las personas"},
    {"number": 32, "block": 3, "optionA": "Le agradaría trabajar en la recepción y trámite documentario de una oficina pública", "optionB": "Prefiere experimentar con las plantas para obtener nuevas especies"},
    {"number": 33, "block": 3, "optionA": "Le gusta proyectar los mecanismos de inversión económica de una empresa", "optionB": "Prefiere analizar las tierras para obtener mayor producción agropecuaria"},
    {"number": 34, "block": 3, "optionA": "Le agrada recibir y ejecutar órdenes de un superior", "optionB": "Prefiere el estudio de los órganos de los animales y su funcionamiento"},
    {"number": 35, "block": 3, "optionA": "Le gusta saber mucho sobre los principios económicos de una cooperativa", "optionB": "Prefiere conocer las enfermedades que aquejan, sea: el ganado, aves, perros, etc."},
    {"number": 36, "block": 3, "optionA": "Le agrada estudiar los fenómenos (sonidos verbales) de su idioma, o de otros", "optionB": "Prefiere dedicar mucho de su tiempo en el estudio de la química"},
    {"number": 37, "block": 3, "optionA": "Le agrada defender pleitos judiciales de recuperación de tierras", "optionB": "Prefiere hacer mezclas de sustancias químicas para obtener derivados con fines productivos"},
    {"number": 38, "block": 4, "optionA": "Sus amigos saben todo de usted, para ellos no tiene secretos", "optionB": "Prefiere reservar algo para usted solo (a) algunos secretos"},
    {"number": 39, "block": 4, "optionA": "Le gusta investigar acerca de los recursos naturales de nuestro país (su fauna, su flora y suelo)", "optionB": "Prefiere estudiar derecho internacional"},
    {"number": 40, "block": 4, "optionA": "Le gusta desarrollar programas de computación para proveer de información rápida y eficiente: a una empresa, institución, etc.", "optionB": "Prefiere obtener fotografías que hagan noticia"},
    {"number": 41, "block": 4, "optionA": "Le gusta mucho conocer el problema de las personas y tramitar su solución", "optionB": "Prefiere dedicar su tiempo a la búsqueda de personajes que hacen noticia"},
    {"number": 42, "block": 4, "optionA": "Le gusta estudiar las características territoriales de los continentes", "optionB": "Prefiere entrevistar a políticos con el propósito de establecer su posición frente a un problema"},
    {"number": 43, "block": 4, "optionA": "Le gusta conocer el funcionamiento de las máquinas impresoras de periódicos", "optionB": "Prefiere trabajar en el montaje fotográfico de un diario o revista"},
    {"number": 44, "block": 4, "optionA": "Le gusta proyectar el tipo de muebles, cortinas y adornos sea para una oficina o para un hogar", "optionB": "Prefiere trabajar como redactor en un diario o revista"},
    {"number": 45, "block": 4, "optionA": "Le gusta redactar cartas comerciales, al igual que oficios y solicitudes", "optionB": "Prefiere averiguar lo que opina el público respecto a un producto"},
    {"number": 46, "block": 4, "optionA": "Le gusta estudiar las leyes de la oferta y la demanda", "optionB": "Prefiere redactar el tema para un anuncio publicitario"},
    {"number": 47, "block": 4, "optionA": "Le gusta organizar el servicio de inteligencia de un cuartel", "optionB": "Prefiere trabajar en una agencia de publicidad"},
    {"number": 48, "block": 4, "optionA": "Le gusta trabajar buscando casas de alquiler para ofrecerlas al público", "optionB": "Prefiere estudiar las características psicológicas para lograr un buen impacto publicitario"},
    {"number": 49, "block": 4, "optionA": "Le interesa investigar acerca de cómo se originaron los idiomas", "optionB": "Prefiere preparar y ejecutar encuestas para conocer la opinión de las personas"},
    {"number": 50, "block": 4, "optionA": "Le agrada hacer los trámites legales de un juicio de divorcio", "optionB": "Prefiere trabajar estableciendo contactos entre una empresa y otra"},
    {"number": 51, "block": 5, "optionA": "Cuando está dando un examen y tiene la oportunidad de verificar una respuesta, nunca lo hace", "optionB": "Prefiere aprovechar la seguridad que la ocasión le confiere"},
    {"number": 52, "block": 5, "optionA": "Le interesa investigar sobre los problemas del lenguaje en la comunicación masiva", "optionB": "Prefiere redactar documentos legales para contratos internacionales"},
    {"number": 53, "block": 5, "optionA": "Le gusta trabajar haciendo instalaciones eléctricas", "optionB": "Prefiere dedicar su tiempo en la lectura de las novedades en la decoración de ambientes"},
    {"number": 54, "block": 5, "optionA": "Le agrada mucho visitar el hogar de los trabajadores con el fin de verificar su verdadera situación social y económica", "optionB": "Prefiere trabajar en el decorado de tiendas y vitrinas"},
    {"number": 55, "block": 5, "optionA": "Le gusta estudiar los recursos geográficos", "optionB": "Prefiere observar el comportamiento de las personas e imitarlas"},
    {"number": 56, "block": 5, "optionA": "Le gustaría dedicar su tiempo a la organización de eventos deportivos entre dos o mas centros laborales", "optionB": "Preferiría dedicarse al estudio de la vida y obra de los grandes actores del cine y del teatro"},
    {"number": 57, "block": 5, "optionA": "Le gustaría estudiar escultura en la escuela de bellas artes", "optionB": "Preferiría ser parte de un elenco de teatro"},
    {"number": 58, "block": 5, "optionA": "Le gusta trabajar de mecanógrafo (a)", "optionB": "Le gusta más dar forma a objetos moldeables; sea: plastilina, migas, arcilla, piedras, etc."},
    {"number": 59, "block": 5, "optionA": "Le agrada mucho estudiar los fundamentos por los que una moneda se devalúa", "optionB": "Prefiere la lectura acerca de la vida y obra de grandes escultores como Miguel Angel, Leonardo de Vinci, etc."},
    {"number": 60, "block": 5, "optionA": "Le agrada mucho la vida del marinero", "optionB": "Prefiere combinar colores para expresar con naturalidad y belleza un paisaje"},
    {"number": 61, "block": 5, "optionA": "Le gustaría trabajar tramitando la compra-venta de inmuebles", "optionB": "Prefiere utilizar las líneas y colores para expresar un sentimiento"},
    {"number": 62, "block": 5, "optionA": "Le gusta estudiar las lenguas y dialectos aborígenes", "optionB": "Prefiere combinar sonidos para obtener una nueva melodía"},
    {"number": 63, "block": 5, "optionA": "Le agrada tramitar judicialmente el reconocimiento de sus hijos", "optionB": "Le agrada más aprender a tocar algún instrumento musical"},
    {"number": 64, "block": 6, "optionA": "Si pasa por un cine y descubre que no hay vigilancia, no se aprovecha de la situación", "optionB": "Prefiere aprovechar la ocasión para entrar sin pagar su boleto"},
    {"number": 65, "block": 6, "optionA": "Le interesa más diseñar y/o confeccionar artículos de cuero", "optionB": "Prefiere asumir la defensa legal en la demarcación de fronteras territoriales"},
    {"number": 66, "block": 6, "optionA": "Prefiere estudiar acerca de cómo la energía se transforma en imágenes de radio, tv, etc.", "optionB": "Le gusta tomar apuntes textuales o didácticos de otras personas"},
    {"number": 67, "block": 6, "optionA": "Le gusta leer sobre la vida y obra de los santos religiosos", "optionB": "Prefiere hacer catálogos o listados de los libros de una biblioteca"},
    {"number": 68, "block": 6, "optionA": "Le gusta dedicar mucho de su tiempo en la lectura de la astronomía", "optionB": "Prefiere trabajar clasificando los libros por autores"},
    {"number": 69, "block": 6, "optionA": "Le gusta trabajar defendiendo el prestigio de su centro laboral", "optionB": "Prefiere trabajar recibiendo y entregando documentos valorados como: cheques, giros, libretas de ahorro, etc."},
    {"number": 70, "block": 6, "optionA": "Le interesa mucho leer sobre la vida y obra de músicos famosos", "optionB": "Prefiere el tipo de trabajo de un empleado bancario"},
    {"number": 71, "block": 6, "optionA": "Le interesa mucho conseguir un trabajo en un banco comercial", "optionB": "Prefiere dedicarse a clasificar libros por especialidades"},
    {"number": 72, "block": 6, "optionA": "Le gusta dedicar su tiempo en el conocimiento del por qué ocurre la inflación económica", "optionB": "Prefiere dedicarse al estudio de cómo se organiza una biblioteca"},
    {"number": 73, "block": 6, "optionA": "Le interesa mucho el conocimiento de la organización de un buque de guerra", "optionB": "Prefiere dedicarse a la recepción y comunicación de mensajes sean verbales o por escrito"},
    {"number": 74, "block": 6, "optionA": "Le gusta trabajar tramitando la compra-venta de vehículos motorizados", "optionB": "Prefiere transcribir los documentos de la administración pública"},
    {"number": 75, "block": 6, "optionA": "Le gusta dedicar gran parte de su tiempo al estudio de las normas y reglas para el uso adecuado del lenguaje", "optionB": "Prefiere trabajar como secretario adjunto al jefe"},
    {"number": 76, "block": 6, "optionA": "Le gusta dedicar su tiempo planteando la defensa de un juicio de alquiler", "optionB": "Prefiere asesorar y aconsejar en torno a tramites documentarios"},
    {"number": 77, "block": 7, "optionA": "Si en la calle se encuentra dinero, sin documento alguno acude a la radio, TV para buscar al infortunado", "optionB": "Preferiría quedarse con el dinero, pues no se conoce al dueño"},
    {"number": 78, "block": 7, "optionA": "Le interesa trabajar en la implementación de bibliotecas distritales", "optionB": "Prefiere asumir la responsabilidad legal para que un fugitivo, con residencia en otro país, sea devuelto a su país"},
    {"number": 79, "block": 7, "optionA": "Le gusta estudiar acerca de cómo la energía se transforma en movimiento", "optionB": "Preferiría hacer una tesis sobre manejo económico para el país"},
    {"number": 80, "block": 7, "optionA": "Le agrada leer sobre la vida y obra de grandes personajes de educación, sean: profesores, filósofos, psicólogos", "optionB": "Prefiere estudiar acerca de las bases económicas de un país"},
    {"number": 81, "block": 7, "optionA": "Le gusta estudiar los astros; sus características, origen y evolución", "optionB": "Prefiere establecer comparaciones entre los sistemas y modelos económicos del mundo"},
    {"number": 82, "block": 7, "optionA": "Le gustaría trabajar exclusivamente promocionando la imagen de su centro laboral", "optionB": "Prefiere estudiar las grandes corrientes ideológicas del mundo"},
    {"number": 83, "block": 7, "optionA": "Le gusta y practica el baile como expresión artística", "optionB": "Prefiere estudiar las bases de la organización política del Tahuantinsuyo"},
    {"number": 84, "block": 7, "optionA": "Le gusta mucho saber sobre el manejo de los archivos públicos", "optionB": "Prefiere establecer diferencias entre los distintos modelos políticos"},
    {"number": 85, "block": 7, "optionA": "Le gusta investigar sobre las características de los regímenes totalitarios, democráticos, republicanos, etc.", "optionB": "Prefiere ser el representante de su país en el extranjero"},
    {"number": 86, "block": 7, "optionA": "Le gusta ser capitán de un buque de guerra", "optionB": "Le interesa más formar y conducir grupos con fines políticos"},
    {"number": 87, "block": 7, "optionA": "Le agrada ser visitador médico", "optionB": "Prefiere dedicar su tiempo en la lectura de la vida y obra de los grandes políticos"},
    {"number": 88, "block": 7, "optionA": "Siente placer buscando en el diccionario el significado de palabras nuevas", "optionB": "Prefiere dedicar todo su tiempo en aras de la paz entre las naciones"},
    {"number": 89, "block": 7, "optionA": "Le interesa mucho estudiar el código penal", "optionB": "Prefiere estudiar los sistemas políticos de otros países"},
    {"number": 90, "block": 8, "optionA": "Le agradan que le dejen muchas tareas para su casa", "optionB": "Prefiere que estas sean lo necesario para aprender"},
    {"number": 91, "block": 8, "optionA": "Le agrada ser miembro activo de una agrupación política", "optionB": "Prefiere escuchar acusaciones y defensas para sancionar de acuerdo a lo que la ley señala"},
    {"number": 92, "block": 8, "optionA": "Le gusta hacer los cálculos para el diseño de telas a gran escala", "optionB": "Le interesa más la mecánica de los barcos y submarinos"},
    {"number": 93, "block": 8, "optionA": "Le agrada observar y evaluar como se desarrolla la inteligencia y personalidad", "optionB": "Prefiere ser aviador"},
    {"number": 94, "block": 8, "optionA": "Le gustaría dedicar su tiempo en el descubrimiento de nuevos medicamentos", "optionB": "Prefiere dedicarse a la lectura acerca de la vida y obra de reconocidos militares, que han aportado en la organización de su institución"},
    {"number": 95, "block": 8, "optionA": "Le gusta la aventura cuando está dirigida a descubrir algo que haga noticia", "optionB": "Prefiere conocer el mecanismo de los aviones de guerra"},
    {"number": 96, "block": 8, "optionA": "Le gusta ser parte de una agrupación de baile y danzas", "optionB": "Preferiría pertenecer a la Fuerza Aérea"},
    {"number": 97, "block": 8, "optionA": "Le gusta el trabajo de llevar mensajes de una dependencia a otra", "optionB": "Prefiere ser miembro de la Policía"},
    {"number": 98, "block": 8, "optionA": "Le gustaría trabajar estableciendo vínculos culturales con otros países", "optionB": "Prefiere el trabajo en la detección y comprobación del delito"},
    {"number": 99, "block": 8, "optionA": "Le gusta trabajar custodiando el orden público", "optionB": "Prefiere ser vigilante receloso de nuestras fronteras"},
    {"number": 100, "block": 8, "optionA": "Le gusta persuadir a los boticarios en la compra de nuevos medicamentos", "optionB": "Prefiere trabajar vigilando a los presos en las prisiones"},
    {"number": 101, "block": 8, "optionA": "Le apasiona leer de escritores serios y famosos", "optionB": "Prefiere organizar el servicio de inteligencia en la destrucción del narcotráfico"},
    {"number": 102, "block": 8, "optionA": "Le gusta asumir la defensa legal de una persona acusada de robo", "optionB": "Prefiere conocer el mecanismo de las armas de fuego"},
    {"number": 103, "block": 9, "optionA": "Se aleja Ud. cuando sus amistades cuentan 'chistes colorados'", "optionB": "Prefiere quedarse gozando de la ocasión"},
    {"number": 104, "block": 9, "optionA": "Le interesa mucho saber cómo se organiza un ejercito", "optionB": "Prefiere participar como jurado de un juicio"},
    {"number": 105, "block": 9, "optionA": "Le gusta proyectar la extracción de metales de una mina", "optionB": "Prefiere estudiar el nombre de los medicamentos y su ventaja comercial"},
    {"number": 106, "block": 9, "optionA": "Le gusta descifrar los diseños gráficos y escritos de culturas muy antiguas", "optionB": "Prefiere persuadir a la gente para que compre un producto"},
    {"number": 107, "block": 9, "optionA": "Le agrada el estudio de los mecanismos de la visión y de sus enfermedades", "optionB": "Prefiere vender cosas"},
    {"number": 108, "block": 9, "optionA": "Le gustaría ganarse la vida escribiendo para un diario o revista", "optionB": "Prefiere estudiar el mercado y descubrir el producto de mayor demanda"},
    {"number": 109, "block": 9, "optionA": "Le gusta actuar, representando a distintos personajes", "optionB": "Le agrada más tener su propio negocio"},
    {"number": 110, "block": 9, "optionA": "Le gusta sentirse importante sabiendo que de usted depende la rapidez o la lentitud de una solicitud", "optionB": "Prefiere trabajar en un bazar"},
    {"number": 111, "block": 9, "optionA": "Le gusta planificar sea para una empresa local o a nivel nacional", "optionB": "Prefiere el negocio de una bodega o tienda de abarrotes"},
    {"number": 112, "block": 9, "optionA": "Le interesa mucho utilizar sus conocimientos en la construcción de armamentos", "optionB": "Prefiere organizar empresas de finanzas y comercio"},
    {"number": 113, "block": 9, "optionA": "Le agrada llevar la contabilidad de una empresa o negocio", "optionB": "Prefiere hacer las planillas de pago para los trabajadores de una empresa o institución"},
    {"number": 114, "block": 9, "optionA": "Le agrada escribir cartas y luego hacer tantas correcciones como sean necesarias", "optionB": "Prefiere ser incorporado como miembros de la corporación nacional de comercio"},
    {"number": 115, "block": 9, "optionA": "Le gusta asumir la defensa legal de una persona acusada de asesinato", "optionB": "Prefiere ser incorporado como miembro de la corporación nacional de comercio"},
    {"number": 116, "block": 10, "optionA": "Le agrada vestir todos los días muy formalmente (con terno y corbata por ejemplo)", "optionB": "Prefiere reservar esa vestimenta para ciertas ocasiones"},
    {"number": 117, "block": 10, "optionA": "Le gusta evaluar la producción laboral de un grupo de trabajadores", "optionB": "Prefiere plantear, previa investigación, la acusación de un sujeto que ha actuado en contra de la ley"},
    {"number": 118, "block": 10, "optionA": "Le gusta estudiar acerca de los reactores atómicos", "optionB": "Prefiere el estudio de las distintas formas literarias"},
    {"number": 119, "block": 10, "optionA": "Le agrada estudiar en torno de la problemática social del Perú", "optionB": "Prefiere escribir cuidando mucho ser comprendido al tiempo que sus escritos resulten agradables al lector"},
    {"number": 120, "block": 10, "optionA": "Le gustaría escribir un tratado sobre anatomía humana", "optionB": "Prefiere recitar sus propios poemas"},
    {"number": 121, "block": 10, "optionA": "Le gustaría incorporarse al colegio de periodistas del Perú", "optionB": "Prefiere aprender otro idioma"},
    {"number": 122, "block": 10, "optionA": "Le gusta diseñar y/o confeccionar: adornos, utensilios, etc., en cerámica, vidrio; etc.", "optionB": "Prefiere traducir textos escritos en otros idiomas"},
    {"number": 123, "block": 10, "optionA": "Le gustaría desarrollar técnicas de mayor eficiencia en el trámite documentario de un ministerio público", "optionB": "Prefiere escribir en otro idioma"},
    {"number": 124, "block": 10, "optionA": "Le agradaría mucho ser secretario general de una central sindical", "optionB": "Prefiere dedicar su tiempo al estudio de lenguas extintas (muertas)"},
    {"number": 125, "block": 10, "optionA": "Le gustaría dedicarse al estudio de normas de alta peligrosidad", "optionB": "Prefiere trabajar como traductor"},
    {"number": 126, "block": 10, "optionA": "Le gusta llevar la estadística de ingresos y egresos mensuales de una empresa o tal vez de una nación", "optionB": "Prefiere los cursos de idiomas: Inglés, Francés, Italiano, etc."},
    {"number": 127, "block": 10, "optionA": "Le gustaría ser incorporado como miembro de la Real Academia de la Lengua Española", "optionB": "Prefiere ser incorporado al Instituto Nacional del Idioma"},
    {"number": 128, "block": 10, "optionA": "Le interesaría ser el asesor legal de un ministro de estado", "optionB": "Prefiere aquellas situaciones que le inspiran a escribir"},
    {"number": 129, "block": 11, "optionA": "Nunca ha bebido licor, aún en ciertas ocasiones lo ha rechazado", "optionB": "Por lo contrario se ha adecuado a las circunstancias"},
    {"number": 130, "block": 11, "optionA": "Le agrada dedicar mucho de su tiempo en la escritura de poemas, cuentos, etc.", "optionB": "Prefiere sentirse importante al saber que de su defensa legal depende la libertad de una persona"},
    {"number": 131, "block": 11, "optionA": "Le agrada estudiar la estructura atómica de los cuerpos", "optionB": "Prefiere asumir la defensa legal de una persona acusada por algún delito"},
    {"number": 132, "block": 11, "optionA": "Le gustaría escribir un tratado acerca de la historia del Perú", "optionB": "Prefiere asumir la defensa legal de un acusado por narcotráfico"},
    {"number": 133, "block": 11, "optionA": "Le gusta investigar de los recursos naturales de nuestro país (su fauna, su flora, su suelo)", "optionB": "Prefiere estudiar el derecho internacional"},
    {"number": 134, "block": 11, "optionA": "Le interesa investigar sobre los problemas del lenguaje en la comunicación masiva", "optionB": "Prefiere redactar documentos legales para contratos internacionales"},
    {"number": 135, "block": 11, "optionA": "Le interesa diseñar y/o confeccionar artículos de cuero", "optionB": "Prefiere asumir la defensa legal en la demarcación de fronteras territoriales"},
    {"number": 136, "block": 11, "optionA": "Le interesa trabajar en la implementación de bibliotecas distritales", "optionB": "Prefiere asumir la responsabilidad legal para que un fugitivo con residencia en otro país sea devuelto a su país"},
    {"number": 137, "block": 11, "optionA": "Le agrada ser miembro activo de una agrupación política", "optionB": "Prefiere escuchar acusaciones y defensas para sancionar de acuerdo a lo que la ley señala"},
    {"number": 138, "block": 11, "optionA": "Le interesa mucho saber como se organiza un ejército", "optionB": "Prefiere participar como jurado en un juicio"},
    {"number": 139, "block": 11, "optionA": "Le gusta evaluar la producción laboral de un grupo de trabajadores", "optionB": "Prefiere plantear previa investigación la acusación de un sujeto que ha ido en contra de la ley"},
    {"number": 140, "block": 11, "optionA": "Le gusta dedicar mucho de su tiempo en la escritura de poemas, cuentos", "optionB": "Prefiere sentirse importante al saber que de su defensa legal depende la libertad de una persona"},
    {"number": 141, "block": 11, "optionA": "Le gustaría dedicarse a la legalización de documentos (contratos, cartas, partidas, títulos, etc.)", "optionB": "Prefiere ser incorporado en una comisión para redactar un proyecto de ley"},
    {"number": 142, "block": 11, "optionA": "Le agrada viajar en un microbús repleto de gente aún cuando no tiene ningún apuro", "optionB": "Prefiere esperar otro vehículo"},
    {"number": 143, "block": 11, "optionA": "Le gusta resolver problemas matemáticos", "optionB": "Prefiere diseñar el modelo de casas, edificios, parques, etc."}
]

@app.get("/")
async def root():
    return {"message": "CASM-83 R2014 API"}

@app.post("/api/start-test")
async def start_test(request: StartTestRequest):
    """Start a new test session"""
    try:
        session = TestSession(
            sex=request.sex,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        session_dict = session.dict()
        await db.test_sessions.insert_one(session_dict)
        
        return {"session_id": session.id, "sex": session.sex}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/questions")
async def get_questions():
    """Get all questions"""
    return {"questions": QUESTIONS, "total": len(QUESTIONS)}

@app.post("/api/save-response")
async def save_response(request: SaveResponseRequest):
    """Save a response for a question"""
    try:
        # Find the session
        session = await db.test_sessions.find_one({"id": request.session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update or add response
        responses = session.get("responses", [])
        
        # Remove existing response for this question if any
        responses = [r for r in responses if r["question_number"] != request.question_number]
        
        # Add new response
        responses.append({
            "question_number": request.question_number,
            "response": request.response
        })
        
        # Update session
        await db.test_sessions.update_one(
            {"id": request.session_id},
            {"$set": {"responses": responses}}
        )
        
        return {"success": True, "total_responses": len(responses)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/complete-test")
async def complete_test(request: CompleteTestRequest):
    """Mark test as completed"""
    try:
        session = await db.test_sessions.find_one({"id": request.session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await db.test_sessions.update_one(
            {"id": request.session_id},
            {"$set": {
                "completed": True,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {"success": True, "message": "Test completed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-session/{session_id}")
async def get_test_session(session_id: str):
    """Get test session details"""
    try:
        session = await db.test_sessions.find_one({"id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Remove MongoDB _id field
        session.pop("_id", None)
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/all-sessions")
async def get_all_sessions():
    """Get all test sessions (for data export)"""
    try:
        sessions = await db.test_sessions.find().to_list(length=None)
        # Remove MongoDB _id field
        for session in sessions:
            session.pop("_id", None)
        return {"sessions": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))