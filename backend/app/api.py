from fastapi import APIRouter, File, UploadFile

from app.conciliacion import conciliar
from app.csv_reader import (
    COLUMNAS_CONTABILIDAD,
    COLUMNAS_FACTURAS,
    NUMERICAS_CONTABILIDAD,
    NUMERICAS_FACTURAS,
    leer_csv,
)
from app.schemas import ResultadoConciliacion

router = APIRouter(prefix="/api", tags=["conciliacion"])


@router.post("/conciliacion", response_model=ResultadoConciliacion)
async def conciliar_archivos(
    facturas: UploadFile = File(...),
    contabilidad: UploadFile = File(...),
) -> ResultadoConciliacion:
    try:
        contenido_facturas = await facturas.read()
        contenido_contabilidad = await contabilidad.read()

        tabla_facturas = leer_csv(
            contenido_facturas,
            facturas.filename or "facturas.csv",
            COLUMNAS_FACTURAS,
            NUMERICAS_FACTURAS,
        )

        tabla_contabilidad = leer_csv(
            contenido_contabilidad,
            contabilidad.filename or "contabilidad.csv",
            COLUMNAS_CONTABILIDAD,
            NUMERICAS_CONTABILIDAD,
        )

        return conciliar(tabla_facturas, tabla_contabilidad)
    finally:
        await facturas.close()
        await contabilidad.close()