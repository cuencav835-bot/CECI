import { Routes } from '@angular/router';
import { InicioComponent } from './pages/inicio/inicio.component';
import { AgenteVentasComponent } from './pages/agente-ventas/agente-ventas.component';
import { AgenteCuentosComponent } from './pages/agente-cuentos/agente-cuentos.component';
import { AgenteMenuComponent } from './pages/agente-menu/agente-menu.component';

export const routes: Routes = [
  { path: '', component: InicioComponent },
  { path: 'agente-ventas', component: AgenteVentasComponent },
  { path: 'agente-cuentos', component: AgenteCuentosComponent },
  { path: 'agente-menu', component: AgenteMenuComponent },
  { path: '**', redirectTo: '' }
];
