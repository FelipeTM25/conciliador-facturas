import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ResultadoConciliacion } from '../models/conciliacion.model';

@Injectable({
  providedIn: 'root'
})
export class ConciliacionService {
  private readonly http = inject(HttpClient);
  private readonly url = 'http://127.0.0.1:8000/api/conciliacion';

  conciliar(
    facturas: File,
    contabilidad: File
  ): Observable<ResultadoConciliacion> {
    const archivos = new FormData();

    archivos.append('facturas', facturas);
    archivos.append('contabilidad', contabilidad);

    return this.http.post<ResultadoConciliacion>(
      this.url,
      archivos
    );
  }
}
