from collections import Counter
from typing import Dict, List, Optional

import pandas as pd

from app.schemas import FacturaResultado, ResultadoConciliacion, Resumen

Numero = Optional[float]
Texto = Optional[str]
Causas = List[str]

TOLERANCIA = 1.0

ESTADO_CORRECTA = "Correcta"
ESTADO_INCONSISTENTE = "Con inconsistencia"
ESTADO_CONTABILIZADA = "Contabilizada"

CAUSA_CAMPOS_VACIOS = "Campos obligatorios vacíos"
CAUSA_IVA = "IVA no coincide con base × tarifa"
CAUSA_TOTAL = "Total no coincide con base + IVA − retención"
CAUSA_DUPLICADA = "Factura duplicada"
CAUSA_SIN_REGISTRO = "Sin registro contable"
CAUSA_REGISTRO_DUPLICADO = "Registro contable duplicado"
CAUSA_NO_CONTABILIZADA = "Registro contable no contabilizado"

CAMPOS_OBLIGATORIOS = [
    "id_factura", "nit_proveedor", "fecha_factura", "concepto",
    "base_gravable", "tarifa_iva", "valor_iva", "valor_retencion", "total_factura",
]


def _valor(fila: pd.Series, campo: str):
    valor = fila[campo]
    return None if pd.isna(valor) else valor


def _redondear(valor: Numero) -> Numero:
    return None if valor is None else round(float(valor), 2)


def _difiere(reportado: Numero, esperado: Numero) -> bool:
    return reportado is not None and esperado is not None and abs(reportado - esperado) > TOLERANCIA


def _causas_campos_vacios(fila: pd.Series) -> Causas:
    vacios = [campo for campo in CAMPOS_OBLIGATORIOS if _valor(fila, campo) is None]
    return [f"{CAUSA_CAMPOS_VACIOS}: {', '.join(vacios)}"] if vacios else []


def _calcular_iva_esperado(fila: pd.Series) -> Numero:
    base = _valor(fila, "base_gravable")
    tarifa = _valor(fila, "tarifa_iva")
    return None if base is None or tarifa is None else base * tarifa


def _calcular_total_esperado(fila: pd.Series, iva_esperado: Numero) -> Numero:
    base = _valor(fila, "base_gravable")
    retencion = _valor(fila, "valor_retencion")
    if base is None or iva_esperado is None or retencion is None:
        return None
    return base + iva_esperado - retencion


def _causas_contables(id_factura: Texto, contabilidad: pd.DataFrame, conteo: Dict[str, int]) -> Causas:
    registros = contabilidad[contabilidad["id_factura"] == id_factura]
    if registros.empty:
        return [CAUSA_SIN_REGISTRO]

    causas = []
    if conteo.get(id_factura, 0) > 1:
        causas.append(CAUSA_REGISTRO_DUPLICADO)
    if (registros["estado"] != ESTADO_CONTABILIZADA).any():
        causas.append(CAUSA_NO_CONTABILIZADA)
    return causas


def _estado_contable(id_factura: Texto, contabilidad: pd.DataFrame) -> Texto:
    registros = contabilidad[contabilidad["id_factura"] == id_factura]
    return None if registros.empty else _valor(registros.iloc[0], "estado")


def conciliar(facturas: pd.DataFrame, contabilidad: pd.DataFrame) -> ResultadoConciliacion:
    facturas_duplicadas = set(facturas.loc[facturas["id_factura"].duplicated(keep=False), "id_factura"].dropna())
    conteo_contable = contabilidad["id_factura"].value_counts().to_dict()

    detalle = []
    for posicion, fila in facturas.reset_index(drop=True).iterrows():
        id_factura = _valor(fila, "id_factura")
        iva_esperado = _calcular_iva_esperado(fila)
        total_esperado = _calcular_total_esperado(fila, iva_esperado)

        causas = _causas_campos_vacios(fila)
        if id_factura in facturas_duplicadas:
            causas.append(CAUSA_DUPLICADA)
        if _difiere(_valor(fila, "valor_iva"), iva_esperado):
            causas.append(CAUSA_IVA)
        if _difiere(_valor(fila, "total_factura"), total_esperado):
            causas.append(CAUSA_TOTAL)
        causas.extend(_causas_contables(id_factura, contabilidad, conteo_contable))

        detalle.append(FacturaResultado(
            fila=posicion + 1,
            id_factura=id_factura or "(sin id)",
            nit_proveedor=_valor(fila, "nit_proveedor"),
            fecha_factura=_valor(fila, "fecha_factura"),
            concepto=_valor(fila, "concepto"),
            base_gravable=_redondear(_valor(fila, "base_gravable")),
            tarifa_iva=_valor(fila, "tarifa_iva"),
            valor_iva=_redondear(_valor(fila, "valor_iva")),
            iva_esperado=_redondear(iva_esperado),
            valor_retencion=_redondear(_valor(fila, "valor_retencion")),
            total_factura=_redondear(_valor(fila, "total_factura")),
            total_esperado=_redondear(total_esperado),
            estado_contable=_estado_contable(id_factura, contabilidad),
            estado=ESTADO_INCONSISTENTE if causas else ESTADO_CORRECTA,
            causas=causas,
        ))

    return ResultadoConciliacion(resumen=_construir_resumen(detalle), detalle=detalle)


def _construir_resumen(detalle: List[FacturaResultado]) -> Resumen:
    con_inconsistencia = sum(1 for f in detalle if f.estado == ESTADO_INCONSISTENTE)
    por_causa = Counter(causa.split(":")[0] for f in detalle for causa in f.causas)
    return Resumen(
        total_facturas=len(detalle),
        correctas=len(detalle) - con_inconsistencia,
        con_inconsistencia=con_inconsistencia,
        inconsistencias_por_causa=dict(por_causa),
    )