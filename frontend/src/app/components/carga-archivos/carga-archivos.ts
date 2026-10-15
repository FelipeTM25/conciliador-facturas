import { Component, output, signal } from '@angular/core';

export interface ArchivosConciliacion {
  facturas: File;
  contabilidad: File;
}

type TipoArchivo = 'facturas' | 'contabilidad';

@Component({
  selector: 'app-carga-archivos',
  imports: [],
  templateUrl: './carga-archivos.html',
  styleUrl: './carga-archivos.scss',
})
export class CargaArchivos {
  readonly procesar = output<ArchivosConciliacion>();

  protected readonly facturas = signal<File | null>(null);
  protected readonly contabilidad = signal<File | null>(null);
  protected readonly error = signal<string | null>(null);

  protected seleccionar(event: Event, tipo: TipoArchivo): void {
    const input = event.target as HTMLInputElement;
    const archivo = input.files?.[0] ?? null;
    const destino = tipo === 'facturas' ? this.facturas : this.contabilidad;

    if (archivo && !archivo.name.toLowerCase().endsWith('.csv')) {
      this.error.set(`El archivo "${archivo.name}" no es un CSV.`);
      input.value = '';
      destino.set(null);
      return;
    }

    this.error.set(null);
    destino.set(archivo);
  }

  protected enviar(): void {
    const facturas = this.facturas();
    const contabilidad = this.contabilidad();
    if (facturas && contabilidad) {
      this.procesar.emit({ facturas, contabilidad });
    }
  }
}
