import { Component } from '@angular/core';

import { ArchivosConciliacion, CargaArchivos } from './components/carga-archivos/carga-archivos';

@Component({
  selector: 'app-root',
  imports: [CargaArchivos],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  protected onProcesar(archivos: ArchivosConciliacion): void {
    console.log('Archivos seleccionados', archivos);
  }
}
