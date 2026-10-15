from typing import Dict, List, Optional

from pydantic import BaseModel


class FacturaResultado(BaseModel):
    fila: int
    id_factura: str
    nit_proveedor: Optional[str] = None
    fecha_factura: Optional[str] = None
    concepto: Optional[str] = None
    base_gravable: Optional[float] = None
    tarifa_iva: Optional[float] = None
    valor_iva: Optional[float] = None
    iva_esperado: Optional[float] = None
    valor_retencion: Optional[float] = None
    total_factura: Optional[float] = None
    total_esperado: Optional[float] = None
    estado_contable: Optional[str] = None
    estado: str
    causas: List[str]


class Resumen(BaseModel):
    total_facturas: int
    correctas: int
    con_inconsistencia: int
    inconsistencias_por_causa: Dict[str, int]


class ResultadoConciliacion(BaseModel):
    resumen: Resumen
    detalle: List[FacturaResultado]