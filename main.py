from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
from typing import Callable


class Generos(Enum):
    """ Clase encargada de definir las opciones de género.
    """
    HOMBRE = "hombre"
    MUJER = "mujer"


class FormulasCalculoKcal(Enum):
    """Esta clase define las diferentes
    fórmulas que se pueden usar para cálcular las kcal
    """
    HARRIS_BENEDICT = "harris"
    MIFFLIN = "mifflin"
    FAO_OMS = "fao/oms"
    KRUMDIECK = "krumdieck"


class FormulasPesoIdeal(Enum):
    LORENTZ = "lorentz"
    PERRAULT = "perrault"
    BROCCA = "brocca"


Genero = str | None
Peso = float | int | None
Estatura = float | int | None
Edad = int | None
Formula = str | None
DictCalculoPesoIdeal = dict[str, float | int | str]
DictCalculoCalorias = dict[str, float | int | str]


class Calculadora(ABC):
    @abstractmethod
    def get_data_persona(self) -> dict:
        pass

    @abstractmethod
    def buscar_formula(self) -> Callable:
        pass

    @abstractmethod
    def calcular(self) -> str | float:
        pass


@dataclass
class Persona:
    """Define los datos de la persona que
    posteriormente se usaran para los cálculos
    """
    _nombre: str
    _genero: str
    _peso: int | float
    _estatura: int | float
    _edad: int

    def __post_init__(self):
        if not isinstance(self.nombre, str) or len(self.nombre) < 5:
            raise ValueError("Debes colocar una cadena de texto y asegurate de colocar 5 o mas caracteres")

        validar_data_persona(genero=self.genero, peso=self.peso,
                             estatura=self.estatura, edad=self.edad)

        self.genero = self.genero.lower()

    @property
    def nombre(self):
        return self.nombre

    @property
    def genero(self):
        return self.genero

    @property
    def peso(self):
        return self.peso

    @property
    def estatura(self):
        return self.estatura

    @property
    def edad(self):
        return self.edad

    @nombre.setter
    def nombre(self, new_value: str):
        self.nombre = new_value

    @genero.setter
    def genero(self, new_value: str):
        validar_data_persona(genero=new_value)
        self.genero = new_value

    @peso.setter
    def peso(self, new_value: int | float):
        self.peso = new_value

    @estatura.setter
    def estatura(self, new_value: int | float):
        self.estatura = new_value

    @edad.setter
    def edad(self, new_value: int):
        self.edad = new_value


# decorador
def validar_data(func):
    """Decorador encargado de validar los datos de la persona
    """

    def wrapper(*args, **kwargs):
        if any(not isinstance(arg, (int, float)) for arg in args):
            raise ValueError("Solo numeros")

        return func(*args, **kwargs)

    return wrapper


def validar_data_persona(genero: Genero = None,
                         peso: Peso = None,
                         estatura: Estatura = None,
                         edad: Edad = None,
                         ) -> None:
    """Encargada de validar la información de la persona.
    """

    generos_validos: tuple[str] = tuple(genero.value for genero in Generos)

    mensaje_error_numero: str = "Debes colocar solo números y asegurate de estar ingresando un numero positivo"

    errores: dict[str, str] = {
        "genero": f"Debes colocar una opción valida, ademas asegurate de estar ingresando una cadena de texto: {generos_validos}, error en la propiedad de 'genero'",
        "peso": mensaje_error_numero,
        "estatura": mensaje_error_numero,
        "edad": mensaje_error_numero,
    }

    genero = genero.lower() if isinstance(genero, str) else genero

    if (genero is not None and genero not in generos_validos) or (genero is not None and not isinstance(genero, str)):
        raise ValueError(errores.get("genero"))

    for (name_error, value) in [("peso", peso), ("estatura", estatura),
                                ("edad", edad)]:
        if (isinstance(value, bool)
                or (value is not None)
                and (not isinstance(value, (int, float)))
                or (value is not None) and (value <= 0)):
            raise ValueError(f"{errores.get(name_error)}, error en la propiedad de '{name_error}'")


def validar_formula_kcal(formula: str | FormulasCalculoKcal, eta: bool) -> None:
    """Encargada de validar la fórmula elegida por el usuario
    """
    formulas_validas_kcal: tuple[str] = tuple(fo.value for fo in FormulasCalculoKcal)

    formula: str = formula.lower() if isinstance(formula, str) else formula

    if not isinstance(eta, bool):
        raise ValueError("El valor de 'ETA' debe ser True o False")

    if not isinstance(formula, (str, FormulasCalculoKcal)):
        raise ValueError("Debes colocar una cadena de texto o un miembro del Enum FormulasCalculoKcal")

    if isinstance(formula, str) and formula not in formulas_validas_kcal:
        raise ValueError(
            f"Debes colocar una fórmula valida como las que se muestran a continuación: {formulas_validas_kcal}.")


def validar_formula_peso_ideal(formula: str | FormulasPesoIdeal):
    formulas_validas_peso_ideal: tuple[str] = tuple(fo.value for fo in FormulasPesoIdeal)

    formula = formula.lower() if isinstance(formula, str) else formula

    if not isinstance(formula, (str, FormulasPesoIdeal)):
        raise ValueError("Debes colocar una cadena de texto o un miembro del enum FormulasPesoIdeal")

    if isinstance(formula, str) and formula not in formulas_validas_peso_ideal:
        raise ValueError(
            f"Debes colocar una fórmula valida como las que se muestran a continuación: {formulas_validas_peso_ideal}")


def calcular_imc(peso: int | float, estatura: float | int) -> float:
    """Encargada de calcular el indice de masa corporal (IMC) en base a su peso y estatura.
    """
    validar_data_persona(peso=peso, estatura=estatura)

    estatura: float = convertir_cm_a_metros(estatura=estatura)

    return round(peso / (estatura ** 2), ndigits=2)


def peso_ideal_lorentz(genero: str, estatura: int | float,
                       edad: int) -> float:
    """Encargada de calcular el peso ideal según la fórmula de Lorentz
    y por defecto devuelve el genero de hombre
    """
    estatura: float = convertir_metros_a_cm(estatura=estatura)

    if genero == Generos.MUJER.value:
        return round(estatura - 100 - ((estatura - 150) / 4) + ((edad - 20) / (2 ** 5)), ndigits=2)

    return round(estatura - 100 - ((estatura - 150) / 4) + ((edad - 20) / 4), ndigits=2)


def peso_ideal_perrault(estatura: int | float, edad: int) -> float:
    """Encargada de cálcular el peso ideal en base a la fórmula de perrault
    """
    estatura: float = convertir_metros_a_cm(estatura=estatura)

    return float(estatura - 100 + (edad / 10) * (9 / 10))


def brocca_peso_ideal(estatura: int | float) -> float:
    """Encargada de cálcular el peso ideal de la
    persona mediante la fórmula de brocca
    """
    estatura: float = convertir_metros_a_cm(estatura=estatura)

    return float(estatura - 100)


def rango_peso_saludable(estatura: int | float) -> str:
    """Encargada de cálcular el rango de peso saludable
    de la persona en base al IMC por lo que no se puede
    tomar como una medida definitiva pero resulta útil
    como referencia.
    """
    estatura: float = estatura ** 2 if isinstance(estatura, float) and estatura < 10 else (estatura / 100) ** 2

    peso_maximo: float = round(estatura * 24.99, ndigits=2)

    peso_minimo: float = round(estatura * 18.5, ndigits=2)

    return f"peso minimo={peso_minimo}kg - maximo={peso_maximo}kg"


def calcular_eta(kcal_base: float) -> float:
    """Encargada de calcular el efecto térmogenico de los alimentos que sera igual a
    un 10% tomando en cuenta las kcal provenientes de la fórmula a utilizar"""
    return float(kcal_base / 10)


def calcular_kcal_totales(kcal_base: float,
                          usar_eta: bool = True) -> float:
    """Encargada de calcular el total de kcal mediante la
    fórmula elegida por el usuario, ETA, y la actividad fisíca de la persona
    """

    if usar_eta:
        eta = calcular_eta(kcal_base=kcal_base)
        return round(kcal_base + eta, ndigits=2)

    return round(kcal_base, ndigits=2)


def convertir_metros_a_cm(estatura: float | int) -> float:
    if isinstance(estatura, float) and estatura < 10:
        estatura *= 100

        return float(estatura)

    return float(estatura)


def convertir_cm_a_metros(estatura: float | int) -> float:
    if isinstance(estatura, (float, int)) and estatura > 10:
        estatura /= 100

        return float(estatura)

    return float(estatura)


def buscar_formula_kcal(formula: FormulasCalculoKcal | str) -> Callable:
    obtener_formula_mediante_miembro = {
        FormulasCalculoKcal.HARRIS_BENEDICT: formula_kcal_harris,
        FormulasCalculoKcal.MIFFLIN: formula_kcal_mifflin,
        FormulasCalculoKcal.FAO_OMS: formula_kcal_fao_oms,
    }

    obtener_formula_mediante_string = {
        "harris": formula_kcal_harris,
        "mifflin": formula_kcal_mifflin,
        "fao/oms": formula_kcal_fao_oms,
    }

    if isinstance(formula, str):
        return obtener_formula_mediante_string[formula]

    return obtener_formula_mediante_miembro[formula]


def buscar_formula_peso_ideal(formula: FormulasPesoIdeal | str) -> Callable:
    obtener_formula_mediante_miembro = {
        FormulasPesoIdeal.LORENTZ: peso_ideal_lorentz,
        FormulasPesoIdeal.PERRAULT: peso_ideal_perrault,
        FormulasPesoIdeal.BROCCA: brocca_peso_ideal,
    }

    obtener_formula_mediante_string = {
        "lorentz": peso_ideal_lorentz,
        "perrault": peso_ideal_perrault,
        "brocca": brocca_peso_ideal,
    }

    if isinstance(formula, str):
        return obtener_formula_mediante_string[formula]

    return obtener_formula_mediante_miembro[formula]


def data_calculo_kcal(obj_persona: Persona | DictCalculoCalorias) -> DictCalculoCalorias:
    return asdict(obj_persona)


def data_calculo_peso_ideal(obj_persona: Persona | DictCalculoPesoIdeal,
                            formula: str | FormulasPesoIdeal) -> DictCalculoPesoIdeal:
    """Esta función retorna los datos para el cálculo del peso
    ideal dependiendo de la fórmula elegida por el usuario"""
    if isinstance(obj_persona, Persona):
        obj_persona: DictCalculoPesoIdeal = {
            "genero": obj_persona.genero,
            "estatura": obj_persona.estatura,
            "edad": obj_persona.edad,
        }

    data_formula_lorentz: dict[str, float | int | str] = {"genero": obj_persona.get("genero"),
                                                          "estatura": obj_persona.get("estatura"),
                                                          "edad": obj_persona.get("edad")}

    data_formula_perrault: dict[str, float | int] = {"estatura": obj_persona.get("estatura"),
                                                     "edad": obj_persona.get("edad")}

    data_formula_brocca: dict[str, float | int] = {"estatura": obj_persona.get("estatura")}

    buscar_data_mediante_miembro: dict[FormulasPesoIdeal, dict[str | float | int]] = {
        FormulasPesoIdeal.LORENTZ: data_formula_lorentz,

        FormulasPesoIdeal.PERRAULT: data_formula_perrault,

        FormulasPesoIdeal.BROCCA: data_formula_brocca,
    }

    buscar_data_mediante_string: dict[str, dict[str | float | int]] = {
        "lorentz": data_formula_lorentz,

        "perrault": data_formula_perrault,

        "brocca": data_formula_brocca,

    }

    if isinstance(formula, str):
        return buscar_data_mediante_string.get(formula)

    return buscar_data_mediante_miembro.get(formula)


def formula_kcal_harris(nombre: str, genero: str, estatura: float | int,
                        peso: float | int, edad: int, usar_eta: bool = True) -> str:
    """Encargada de calcular las kcal de la persona mediante la fórmula de
    harris la cual requiere la estatura en cm
    """
    mensaje: str = f"De acuerdo a la fórmula de harris estimado {nombre}, las kcal que necesitas son: "

    # if isinstance(estatura, float) and estatura < 10:
    # estatura *= 100
    estatura: float = convertir_metros_a_cm(estatura=estatura)

    if genero == Generos.MUJER.value:
        formula_mujer: float = (655.1
                                + (9.563 * peso)
                                + (1.85 * estatura)
                                - (4.676 * edad)
                                )
        kcal_totales: float = calcular_kcal_totales(kcal_base=formula_mujer,
                                                    usar_eta=usar_eta)
        return f"{mensaje}{kcal_totales}"

    formula_hombre: float = (66.5
                             + (13.75 * peso)
                             + (5.003 * estatura)
                             - (6.775 * edad)
                             )
    kcal_totales: float = calcular_kcal_totales(kcal_base=formula_hombre,
                                                usar_eta=usar_eta)
    return f"{mensaje}{kcal_totales}"


def formula_kcal_mifflin(nombre: str, genero: str, estatura: float | int,
                         peso: float | int, edad: int, usar_eta: bool = True) -> str:
    """Encargada de cálcular las kcal en base a la fórmula de mifflin
    """
    mensaje: str = f"De acuerdo a la fórmula de mifflin estimado {nombre}, las kcal que necesitas son: "

    estatura: float = convertir_metros_a_cm(estatura=estatura)

    if genero == Generos.MUJER.value:
        formula_mujer: float = ((10 * peso)
                                + (6.25 * estatura)
                                - (5 * edad)
                                - 161)

        kcal_totales: float = calcular_kcal_totales(kcal_base=formula_mujer,
                                                    usar_eta=usar_eta)

        return f"{mensaje}{kcal_totales}"

    formula_hombre: float = ((10 * peso)
                             + (6.25 * estatura)
                             - (5 * edad)
                             + 5)

    kcal_totales = calcular_kcal_totales(kcal_base=formula_hombre,
                                         usar_eta=usar_eta)

    return f"{mensaje}{kcal_totales}"


def formula_kcal_fao_oms(nombre: str, genero: str, estatura: float | int,
                         peso: float | int, edad: int, usar_eta: bool = True):
    """Encargada de calcular las kcal en base a la fórmula de la fao/oms
    """
    mensaje: str = f"De acuerdo a la fórmula de fao/oms estimado {nombre}, las kcal que necesitas son: "

    estatura: float = convertir_metros_a_cm(estatura=estatura)

    if genero == Generos.MUJER.value:
        formula_mujer: float = (447.593
                                + (9.247 * peso)
                                + (3.098 * estatura)
                                - (4.330 * edad))

        kcal_totales: float = calcular_kcal_totales(kcal_base=formula_mujer,
                                                    usar_eta=usar_eta)

        return f"{mensaje}{kcal_totales}"

    formula_hombre: float = (88.362
                             + (13.397 * peso)
                             + (4.799 * estatura)
                             - (5.677 * edad))

    kcal_totales: float = calcular_kcal_totales(kcal_base=formula_hombre,
                                                usar_eta=usar_eta)

    return f"{mensaje}{kcal_totales}"


def formula_kcal_krumdieck(peso: int | float, estatura: int | float) -> float:
    """Encargada de cálcular las kcal de la persona
    mediante la fórmula de krumdieck en la cual se
    }necesita la estatura en metros
    """
    estatura = estatura if isinstance(estatura, float) and estatura < 10 else (estatura / 100)

    return float((30 * peso) + (40 * estatura))


@dataclass
class Persona:
    """Define los datos de la persona que
    posteriormente se usaran para los cálculos
    """
    nombre: str
    genero: str
    peso: int | float
    estatura: int | float
    edad: int

    def __post_init__(self):
        if not isinstance(self.nombre, str) or len(self.nombre) < 5:
            raise ValueError("Debes colocar una cadena de texto y asegurate de colocar 5 o mas caracteres")

        validar_data_persona(genero=self.genero, peso=self.peso,
                             estatura=self.estatura, edad=self.edad)

        self.genero = self.genero.lower()


@dataclass
class ValoracionNutricional:
    """Clase encargada de mostrarle a la persona su estado nutricio.
    """
    name: str = "User"

    def __post_init__(self):
        if not isinstance(self.name, str) or len(self.name) < 5:
            raise ValueError("El nombre debe ser una cadena de texto y tener al menos 5 caracteres")

    def calcular_imc(self, peso: float | int, estatura: float | int) -> float:
        """Encargada de calcular el IMC en base a su peso y estatura.
        """
        validar_data_persona(peso=peso, estatura=estatura)

        if isinstance(estatura, int):
            estatura = float(estatura / 100)

        resultado = round(peso / (estatura ** 2), ndigits=2)

        print(f"Hola {self.name} este es tu imc: {resultado=}")

        return resultado

    def diagnostico_imc(self, peso: float | int,
                        estatura: float | int) -> str:
        """De acuerdo al calculo del IMC se encarga de mostrarle al usuario su estado actual.
        """
        validar_data_persona(estatura=estatura, peso=peso)

        resultado_imc = self.calcular_imc(peso=peso, estatura=estatura)

        mensajes_diagnostico = {
            "bajo_peso": "Te encuentras en un bajo peso",
            "normal": "Te encuentras en un peso saludable",
            "sobrepeso": "Te encuentras en sobrepeso",
            "obesidad": "Te encuentras en obesidad"
        }

        bajo_peso: bool = resultado_imc < 18.5
        peso_normal: bool = 18.5 <= resultado_imc < 25
        sobrepeso: bool = 24.99 < resultado_imc < 30
        obesidad: bool = 29.99 < resultado_imc < 35

        resultados_comprobacion_imc: list[bool] = [bajo_peso, peso_normal, sobrepeso, obesidad]

        resultado: list[str] | list = [mensaje_diagnostico for mensaje_diagnostico, comprobacion_imc in zip(
            mensajes_diagnostico, resultados_comprobacion_imc) if comprobacion_imc]

        if resultado:
            return mensajes_diagnostico[resultado[0]]

        return "No te encuentras en ninguno de los resultados, verifica bien los datos que ingresados"

    def gasto_energetico(self, nombre: str, genero: str, peso: float | int,
                         estatura: float | int, edad: int,
                         formula: str = "harris") -> str:
        """Encargada de mostrarle al usuario las KCAL que debería consumir
           en un día para mantener su peso actual.
        """
        pass


@dataclass
class CalculadoraDeCalorias(Calculadora):
    """Esta clase se encarga de calcular las calorias que necesita
    consumir una persona para mantenerse en su peso actual en base a diferentes parametros
    """
    persona: Persona
    formula: FormulasCalculoKcal | str = FormulasCalculoKcal.MIFFLIN
    eta: bool = True

    def __post_init__(self):
        """Encargada de validar los datos ingresados del usuario
        """
        validar_formula_kcal(formula=self.formula, eta=self.eta)

        if isinstance(self.formula, str):
            self.formula = self.formula.lower()

    def get_data_persona(self) -> DictCalculoCalorias:
        """Encaragada de convertir la instancia de persona
        en un diccionario para poder desempaquetarlo en
        las funciones de cálculo de calorias
        """
        return data_calculo_kcal(obj_persona=self.persona)

    def buscar_formula(self) -> Callable:
        return buscar_formula_kcal(self.formula)

    def calcular(self) -> str:
        """Encargada de usar los datos pasados por el usuario
        para calcular sus kcal en base a la fórmula elegida
        """

        persona_data: DictCalculoCalorias = self.get_data_persona()

        formula_kcal_a_usar: Callable = self.buscar_formula()

        return formula_kcal_a_usar(**persona_data, usar_eta=self.eta)


@dataclass
class CalculadoraPesoIdeal(Calculadora):
    """Clase encargadad de calcular el
    peso ideal de las personas mediante distintas fórmulas
    """
    persona: Persona | DictCalculoPesoIdeal
    formula: FormulasPesoIdeal | str = FormulasPesoIdeal.LORENTZ

    def __post_init__(self) -> None:
        if isinstance(self.persona, dict):
            claves_esperadas: set[str] = {"genero", "estatura", "edad"}

            claves_diccionario_obtenido: set[str] = set(self.persona.keys())

            if claves_diccionario_obtenido != claves_esperadas:
                raise ValueError(f"Las claves esperadas son las siguientes: {claves_esperadas}"
                                 f"\nLas claves obtenidas son: {claves_diccionario_obtenido}")

            validar_data_persona(genero=self.persona.get("genero"),
                                 estatura=self.persona.get("estatura"),
                                 edad=self.persona.get("edad"))

        validar_formula_peso_ideal(formula=self.formula)

    def get_data_persona(self) -> DictCalculoPesoIdeal:
        """Encargada de devolver un diccionario con los
        datos necesarios para el cálculo del peso ideal
        """
        return data_calculo_peso_ideal(obj_persona=self.persona, formula=self.formula)

    def buscar_formula(self) -> Callable:
        return buscar_formula_peso_ideal(formula=self.formula)

    def calcular(self) -> float:
        """Encargada de devolver el resultado del
        peso ideal en base a la fórmula elegida
        """
        data_calculo: DictCalculoPesoIdeal = self.get_data_persona()

        formula_peso_ideal: Callable = self.buscar_formula()

        return formula_peso_ideal(**data_calculo)


@validar_data
def suma(a, b, c, d) -> float:
    return float(a + b + c + d)


sumatoria: float = suma(5, 5, 10.5, 5)
print(sumatoria)

if __name__ == "__main__":
    persona = Persona(nombre="kevin dueñas", genero="hombre", edad=22, estatura=1.70, peso=75)

    mis_kcal = CalculadoraDeCalorias(persona=persona, formula=FormulasCalculoKcal.HARRIS_BENEDICT, eta=True)
    print(mis_kcal)

    print(mis_kcal.calcular())

    print(peso_ideal_perrault(estatura=170, edad=22))
    print(brocca_peso_ideal(estatura=170))
    print(rango_peso_saludable(estatura=170))
    print(formula_kcal_krumdieck(peso=75, estatura=170))
    diccionario = {"genero": "hombre", "estatura": 1.70, "edad": 22}

    mi_peso_ideal = CalculadoraPesoIdeal(persona=diccionario, formula=FormulasPesoIdeal.PERRAULT)
    print(mi_peso_ideal.calcular())

    print(peso_ideal_lorentz(genero="hombre", estatura=170, edad=22))
    print(diccionario)

    mi_imc = ValoracionNutricional(name="kevin asael")
    print(mi_imc.diagnostico_imc(estatura=1.70, peso=75))
    print(persona.nombre)
    persona.nombre = "perr"
    print(persona)
    persona.genero = "hom"
    print(persona)