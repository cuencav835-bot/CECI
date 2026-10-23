import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { CuentaService } from './services/cuenta.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'ceci';

  constructor(public cuenta: CuentaService) {
    this.cuenta.iniciar();
  }
}
