export interface Resumen {
  total_facturas: number;
  correctas: number;
  con_inconsistencia: number;
  inconsistencias_por_causa: Record<string, number>;
}

export interface FacturaResultado {
  fila: number;
  id_factura: string;
  nit_proveedor: string | null;
  fecha_factura: string | null;
  concepto: string | null;
  base_gravable: number | null;
  tarifa_iva: number | null;
  valor_iva: number | null;
  iva_esperado: number | null;
  valor_retencion: number | null;
  total_factura: number | null;
  total_esperado: number | null;
  estado_contable: string | null;
  estado: 'Correcta' | 'Con inconsistencia';
  causas: string[];
}

export interface ResultadoConciliacion {
  resumen: Resumen;
  detalle: FacturaResultado[];
}
