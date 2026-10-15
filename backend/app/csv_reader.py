import io
from typing import List

import pandas as pd
from fastapi import HTTPException

COLUMNAS_FACTURAS = [
    "id_factura", "nit_proveedor", "fecha_factura", "concepto", "base_gravable",
    "tarifa_iva", "valor_iva", "tarifa_retencion", "valor_retencion", "total_factura",
]
NUMERICAS_FACTURAS = [
    "base_gravable", "tarifa_iva", "valor_iva", "tarifa_retencion", "valor_retencion", "total_factura",
]

COLUMNAS_CONTABILIDAD = [
    "id_factura", "fecha_contabilizacion", "cuenta_contable", "centro_costo",
    "valor_debito", "valor_credito", "estado",
]
NUMERICAS_CONTABILIDAD = ["valor_debito", "valor_credito"]


def _decodificar(contenido: bytes, nombre: str) -> str:
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return contenido.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise HTTPException(status_code=400, detail=f"No se pudo leer la codificación de '{nombre}'.")


def leer_csv(contenido: bytes, nombre: str, columnas: List[str], numericas: List[str]) -> pd.DataFrame:
    if not nombre or not nombre.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail=f"El archivo '{nombre}' no es un CSV.")

    if not contenido or not contenido.strip():
        raise HTTPException(status_code=400, detail=f"El archivo '{nombre}' está vacío.")

    texto = _decodificar(contenido, nombre)

    try:
        df = pd.read_csv(io.StringIO(texto), dtype=str, skipinitialspace=True)
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise HTTPException(status_code=400, detail=f"El archivo '{nombre}' no tiene un formato CSV válido.") from exc

    df.columns = [c.strip().lower() for c in df.columns]

    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Al archivo '{nombre}' le faltan columnas obligatorias: {', '.join(faltantes)}.",
        )

    if df.empty:
        raise HTTPException(status_code=400, detail=f"El archivo '{nombre}' no tiene registros.")

    df = df[columnas].copy()

    for col in columnas:
        df[col] = df[col].str.strip().replace({"": None})

    for col in numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df