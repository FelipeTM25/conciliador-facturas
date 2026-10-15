import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';

import {
  ArchivosConciliacion,
  CargaArchivos
} from './components/carga-archivos/carga-archivos';
import { ResultadoConciliacion } from './models/conciliacion.model';
import { ConciliacionService } from './services/conciliacion.service';

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

  protected onProcesar(archivos: ArchivosConciliacion): void {
    if (this.cargando()) {
      return;
    }

    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

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
