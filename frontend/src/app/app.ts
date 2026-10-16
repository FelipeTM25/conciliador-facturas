import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';

import {
  ArchivosConciliacion,
  CargaArchivos
} from './components/carga-archivos/carga-archivos';
import {
  FacturaResultado,
  ResultadoConciliacion
} from './models/conciliacion.model';
import { ConciliacionService } from './services/conciliacion.service';

type FiltroEstado = 'Todas' | FacturaResultado['estado'];

@Component({
  selector: 'app-root',
  imports: [CargaArchivos],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly conciliacionService = inject(ConciliacionService);

  protected readonly cargando = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly resultado = signal<ResultadoConciliacion | null>(null);
  protected readonly filtro = signal<FiltroEstado>('Todas');

  protected readonly filtros: FiltroEstado[] = ['Todas', 'Correcta', 'Con inconsistencia'];

  protected readonly facturasFiltradas = computed(() => {
    const detalle = this.resultado()?.detalle ?? [];
    const filtro = this.filtro();
    return filtro === 'Todas'
      ? detalle
      : detalle.filter((factura) => factura.estado === filtro);
  });

  protected onProcesar(archivos: ArchivosConciliacion): void {
    if (this.cargando()) {
      return;
    }

    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);
    this.filtro.set('Todas');

    this.conciliacionService
      .conciliar(archivos.facturas, archivos.contabilidad)
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (resultado) => {
          this.resultado.set(resultado);
        },
        error: (error: HttpErrorResponse) => {
          const detalle = error.error?.detail;

          this.error.set(
            error.status === 0
              ? 'No se pudo conectar con el backend. Revisa que esté iniciado y que CORS esté configurado.'
              : typeof detalle === 'string'
                ? detalle
                : 'No se pudieron procesar los archivos.'
          );
        }
      });
  }
}
