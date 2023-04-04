from dataclasses import dataclass, asdict
from enum import Enum


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


class FormulasPesoIdeal(str, Enum):
    LORENTZ = "lorentz"
    PERRAULT = "perrault"
    BROCCA = "brocca"


Genero = str | None
Peso = float | int | None
Estatura = float | int | None
Edad = int | None
Formula = str | None
DictCalculoPesoIdeal = dict[str, float | int | str]

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
    """Encargada de validar la información sobre la persona.
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

    if genero is not None and genero not in generos_validos:
        raise ValueError(errores.get("genero"))

    for (name_error, value) in [("peso", peso), ("estatura", estatura),
                                ("edad", edad)]:
        if (isinstance(value, bool)
                or (value is not None)
                and (not isinstance(value, (int, float)))
                or (value is not None) and (value <= 0)):
            raise ValueError(f"{errores.get(name_error)}, error en la propiedad de '{name_error}'")


def validar_formula_kcal(formula: str, eta: bool) -> None:
    """Encargada de validar la fórmula elegida por el usuario
    """
    formula = formula.lower() if isinstance(formula, str) else formula

    formulas_validas: tuple[str] = tuple(fo.value for fo in FormulasCalculoKcal)

    if not isinstance(eta, bool):
        raise ValueError("Debes colocar True o false")

    if not isinstance(formula, str):
        raise ValueError("Debes colocar una cadena de texto")

    if formula not in formulas_validas:
        raise ValueError(
            f"Debes colocar una fórmula valida como las que se muestran a continuación: {formulas_validas}.")


def calcular_imc(peso: int | float, estatura: float | int) -> float:
    """Encargada de calcular el indice de masa corporal (IMC) en base a su peso y estatura.
    """
    validar_data_persona(peso=peso, estatura=estatura)

    if isinstance(estatura, int):
        estatura: float = float(estatura / 100)

    resultado: float = round(peso / (estatura ** 2), ndigits=2)

    return resultado


def peso_ideal_lorentz(genero: str, estatura: int | float,
                       edad: int) -> float:
    """Encargada de calcular el peso ideal según la fórmula de Lorentz
    y por defecto devuelve el genero de hombre
    """
    estatura = estatura * 100 if isinstance(estatura, float) and estatura < 10 else estatura

    if genero == Generos.MUJER.value:
        return round(estatura - 100 - ((estatura - 150) / 4) + ((edad - 20) / (2 ** 5)), ndigits=2)

    return round(estatura - 100 - ((estatura - 150) / 4) + ((edad - 20) / 4), ndigits=2)


def peso_ideal_perrault(estatura: int | float, edad: int) -> float:
    """Encargada de cálcular el peso ideal en base a la fórmula de perrault
    """
    estatura = estatura * 100 if isinstance(estatura, float) and estatura < 10 else estatura

    return float(estatura - 100 + (edad / 10) * (9 / 10))


def brocca_peso_ideal(estatura: int | float) -> float:
    """Encargada de cálcular el peso ideal de la
    persona mediante la fórmula de brocca
    """
    estatura = estatura * 100 if isinstance(estatura, float) and estatura < 10 else estatura

    return float(estatura - 100)


def rango_peso_saludable(estatura: int | float) -> str:
    """Encargada de cálcular el rango de peso saludable
    de la persona en base al IMC por lo que no se puede
    tomar como una medida definitiva pero resulta útil
    como referencia.
    """
    estatura = estatura ** 2 if isinstance(estatura, float) and estatura < 10 else (estatura / 100) ** 2

    peso_maximo: float = round(estatura * 24.99, ndigits=2)

    peso_minimo: float = round(estatura * 18.5, ndigits=2)

    return f"peso minimo={peso_minimo}kg - maximo={peso_maximo}kg"


def efecto_termogenico_alimentos(kcal_base: float) -> float:
    """Encargada de calcular el denominado ETA que sera igual a
    un 10% tomando en cuenta las kcal provenientes de la fórmula a utilizar"""
    return kcal_base / 10


def calcular_kcal_totales(kcal_base: float,
                          usar_eta: bool = True) -> float:
    """Encargada de calcular el total de kcal mediante la
    fórmula elegida por el usuario, ETA, y la actividad fisíca de la persona
    """
    eta = kcal_base / 10

    if not usar_eta:
        return round(kcal_base, ndigits=2)

    return round(kcal_base + eta, ndigits=2)


def formula_kcal_harris(nombre: str, genero: str, estatura: float | int,
                        peso: float | int, edad: int, usar_eta: bool = True) -> str:
    """Encargada de calcular las kcal de la persona mediante la fórmula de harris
    """
    mensaje: str = f"De acuerdo a la fórmula de harris estimado {nombre}, las kcal que necesitas son: "

    if isinstance(estatura, float) and estatura < 10:
        estatura *= 100

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

    if isinstance(estatura, float) and estatura < 10:
        estatura *= 100

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

    if isinstance(estatura, float) and estatura < 10:
        estatura *= 100

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
    mediante la fórmula de krumdieck
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

        mensajes = {
            "bajo_peso": "Te encuentras en un bajo peso",
            "normal": "Te encuentras en un peso saludable",
            "sobrepeso": "Te encuentras en sobrepeso",
            "obesidad": "Tienes un exceso de peso, lo recomendable es acudir con un profesional de la salud"
        }

        BAJO_PESO = resultado_imc < 18.5
        NORMAL = resultado_imc >= 18.5 and resultado_imc < 25
        SOBREPESO = resultado_imc > 24.99 and resultado_imc < 30

        if BAJO_PESO:
            return mensajes.get("bajo_peso")

        elif NORMAL:
            return mensajes.get("normal")

        elif SOBREPESO:
            return mensajes.get("sobrepeso")

        return mensajes.get("obesidad")

    def gasto_energetico(self, nombre: str, genero: str, peso: float | int,
                         estatura: float | int, edad: int,
                         formula: str = "harris") -> str:
        """Encargada de mostrarle al usuario las KCAL que debería consumir
           en un día para mantener su peso actual.
        """
        pass


@dataclass
class CalculadoraDeCalorias:
    """Esta clase se encarga de calcular las calorias que necesita
    consumir una persona para mantenerse en su peso actual en base a diferentes parametros
    """
    persona: Persona
    formula: str = "mifflin"
    eta: bool = True

    def __post_init__(self):
        """Encargada de validar los datos ingresados del usuario
        """
        validar_formula_kcal(formula=self.formula, eta=self.eta)

        self.formula = self.formula.lower()

    def get_data_persona(self) -> dict[str, int | float | str]:
        """Encaragada de convertir la instancia de persona
        en un diccionario para poder desempaquetarlo en
        las funciones de cálculo de calorias
        """
        return asdict(self.persona)

    def calcular_gasto_energetico(self) -> str:
        """Encargada de usar los datos pasados por el usuario
        para calcular sus kcal en base a la fórmula elegida
        """

        persona_data: dict[str, int | float | str] = self.get_data_persona()

        if self.formula == FormulasCalculoKcal.HARRIS_BENEDICT.value:
            return formula_kcal_harris(**persona_data, usar_eta=self.eta)

        elif self.formula == FormulasCalculoKcal.MIFFLIN.value:
            return formula_kcal_mifflin(**persona_data, usar_eta=self.eta)

        elif self.formula == FormulasCalculoKcal.FAO_OMS.value:
            return formula_kcal_fao_oms(**persona_data, usar_eta=self.eta)


@dataclass
class CalculadoraPesoIdeal:
    persona: Persona | DictCalculoPesoIdeal
    formula: FormulasPesoIdeal | str = FormulasPesoIdeal.LORENTZ

    def __post_init__(self):
        if isinstance(self.persona, dict):
            claves_esperadas: set[str] = {"genero", "estatura", "edad"}

            claves_diccionario_obtenido: set[str] = set(self.persona.keys())

            if claves_diccionario_obtenido != claves_esperadas:
                raise ValueError(f"Las claves esperadas son las siguientes: {claves_esperadas}"
                                 f"\nLas claves obtenidas son: {claves_diccionario_obtenido}")

            validar_data_persona(genero=self.persona.get("genero"),
                                 estatura=self.persona.get("estatura"),
                                 edad=self.persona.get("edad"))

    def get_data_persona(self):
        if isinstance(self.persona, Persona):
            return {"genero": self.persona.genero, "estatura": self.persona.estatura,
                    "edad": self.persona.edad}

        return self.persona

    def calcular_peso_ideal(self):
        data_calculo_peso_ideal: DictCalculoPesoIdeal = self.get_data_persona()

        if self.formula == FormulasPesoIdeal.LORENTZ:
            return peso_ideal_lorentz(**data_calculo_peso_ideal)

        elif self.formula == FormulasPesoIdeal.PERRAULT:
            return peso_ideal_perrault(estatura=data_calculo_peso_ideal.get("estatura"),
                                       edad=data_calculo_peso_ideal.get("edad"))

        elif self.formula == FormulasPesoIdeal.BROCCA:
            return brocca_peso_ideal(estatura=data_calculo_peso_ideal.get("estatura"))


@validar_data
def suma(a, b, c, d) -> float:
    return float(a + b + c + d)


sumatoria: float = suma(5, 5, 10.5, 5)
print(sumatoria)

if __name__ == "__main__":
    persona1 = ValoracionNutricional(name="Kevin")
    print(persona1)

    print(persona1.diagnostico_imc(peso=75, estatura=170))
    print(persona1.gasto_energetico(nombre="kevincin",
                                    genero="hombre", edad=22, estatura=1.70, peso=75, formula="harris"))

    persona = Persona(nombre="kevin asael", genero="hombre", edad=22, estatura=170, peso=75)

    mis_kcal = CalculadoraDeCalorias(persona=persona, formula="harris", eta=True)
    print(mis_kcal)

    print(mis_kcal.calcular_gasto_energetico())

    print(peso_ideal_perrault(estatura=170, edad=22))
    print(brocca_peso_ideal(estatura=170))
    print(rango_peso_saludable(estatura=170))
    print(formula_kcal_krumdieck(peso=75, estatura=170))
    diccionario = {"genero": "hombre", "estatura": 1.70, "edad": 22}

    mi_peso_ideal = CalculadoraPesoIdeal(persona=persona, formula=FormulasPesoIdeal.LORENTZ)
    print(mi_peso_ideal.calcular_peso_ideal())

    print(peso_ideal_lorentz(genero="hombre", estatura=170, edad=22))
    print(diccionario)
