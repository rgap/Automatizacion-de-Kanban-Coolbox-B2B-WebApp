Usando el formato de user story definido dentro de formato_de_user_story.md crea un archivo user_stories.csv con 15 issues como Product Backlog para un MVP v1.0 definido dentro [mvp] y desarrollado con SCRUM de 4 sprints y sprints de una semana.

Considera el contexto de proyecto definido dentro de [contexto], con prototipo UI que sigue EXACTAMENTE la arquitectura de información definida dentro de [arquitectura], y alineado con la protopersona descrita dentro de en [protopersona] para completar el taskflow dentro de [taskflow].

## REGLAS OBLIGATORIAS

Las columnas del CSV deben ser:

- Titulo
- Descripción
- Referencias visuales
- Criterios de aceptación en formato test cases
- Tareas
- Estimación del esfuerzo (story points)
- Prioridad
- Etiquetas (labels)

Las tareas deben ser varias técnicas con términos técnicos porque las realizarán SCRUM developers:

| Nombre del rol         | Abreviatura |
| ---------------------- | ----------- |
| Frontend Developer     | FE          |
| Backend Developer      | BE          |
| Quality Assurance      | QA          |
| UX/UI Designer         | UX          |
| DevOps Engineer        | DEVOPS      |
| Database Administrator | DB          |
| Security Engineer      | SEC         |
| Cloud Engineer         | CLD         |
| Technical Writer       | DOC         |
| Mobile Developer       | MOB         |

## MVP

[mvp]

# MVP v1.0

## Descripción

El MVP v1.0 es una versión simple del sistema de seguimiento post-venta B2B para Coolbox.

Se desarrolla en 4 sprints de 1 semana cada uno. En esta versión solo se trabaja el registro de clientes y la generación de alertas.

## Qué debe tener

- Registro básico de clientes.
- Lista básica de clientes.
- Ficha básica del cliente.
- Lista de alertas de recompra.
- Datos de prueba con clientes existentes y compras anteriores.

## Resultado esperado

Al final de los 4 sprints debe existir una versión básica donde se puedan registrar clientes, ver clientes existentes y visualizar alertas de recompra.

[/mvp]

## CONTEXTO, PROTOPERSONA Y TASKFLOW:

[contexto]

Empresa: Coolbox, empresa de retail especializado en tecnología (B2B y B2C), operada por Rash Perú S.R.L. Con más de 150 tiendas en Lima y provincias, y un canal corporativo B2B dedicado a empresas, instituciones y emprendimientos.

Proceso analizado: Ventas corporativas B2B, desde el primer contacto del cliente hasta el seguimiento post-venta.

Problema central identificado en el avance anterior: Los encargados de ventas corporativas gestionan entre 15 y 30 clientes corporativos de forma simultánea. Al no contar con un sistema de seguimiento automatizado, dependen de su memoria y de hojas de cálculo para recordar cuándo contactar a cada cliente después de una venta. Esto genera pérdida sistemática de oportunidades de recompra y up-selling, en especial en productos tecnológicos con ciclos de renovación predecibles (laptops, equipos de cómputo, cámaras de seguridad).

Innovación propuesta: Implementar alertas automáticas en un CRM B2B que notifiquen al encargado de ventas en el momento óptimo para contactar a cada cliente corporativo, calculadas en función de la vida útil estimada del producto adquirido.

[/contexto]

[protopersona]

**Nombre y apellido:** Diego Salas
**Rol / tipo de usuario:** Encargado de Ventas Corporativas B2B
**Descripción del rol:** Persona responsable de gestionar la cartera de clientes corporativos de Coolbox, desde el primer contacto hasta el cierre de la venta y el seguimiento post-venta.
**Puntos de dolor:** Atiende entre 15 y 30 clientes corporativos de forma simultánea sin una herramienta que le indique cuándo contactar a cada cliente. Pierde oportunidades de recompra por olvido. Cuando recuerda llamar, el cliente ya cotizó con la competencia.
**Necesidades:** Un sistema que le notifique automáticamente cuándo contactar a cada cliente, con el contexto suficiente (empresa, producto comprado, monto, fecha) para personalizar la llamada en menos de un minuto, sin necesidad de buscar información en otra pantalla.

[/protopersona]

[taskflow]

**Taskflow 1:** Revisión y acción sobre una alerta de recompra urgente _(Happy Path)_

**Rol / tipo de usuario:** Encargado de Ventas Corporativas B2B

**Objetivo del usuario dentro del sistema:** Identificar el cliente corporativo más urgente del día, revisar su contexto y registrar el resultado del contacto realizado sin desvíos ni errores

```text
1. Ingresa al CRM
2. Mira el Dashboard del Encargado de Ventas
3. Mira el widget "Alertas de recompra activas"
4. Identifica 2 alertas en rojo en el contador "Urgentes"
5. Hace clic en la tarjeta de la primera alerta urgente
6. Mira la Vista: Ficha del cliente
7. Lee el nombre de la empresa, el contacto, el producto, el monto y la fecha de la última compra
8. Realiza la llamada al cliente fuera del sistema
9. Hace clic en el botón "Registrar contacto"
10. Mira el Modal: Registro de contacto
11. Selecciona el resultado del contacto (ej. "Interesado en recompra")
12. Escribe una nota sobre la conversación
13. Confirma o edita la fecha del próximo seguimiento
14. Hace clic en "Guardar y cerrar"
15. Mira el Dashboard del Encargado de Ventas con la alerta cerrada y el contador actualizado
```

[/taskflow]

## ARQUITECTURA:

[arquitectura]

```text
Vista: Dashboard del Encargado de Ventas
	Sección: Barra superior
		Nombre del encargado activo
		Ícono: Notificaciones
		Ícono: Ayuda
	Sección: Alertas de recompra activas
		Contador: Urgentes (vencidas o con vencimiento hoy) -> Vista: Ficha del cliente
		Contador: Próximas (1–7 días) -> Vista: Ficha del cliente
		Contador: En seguimiento (8–30 días) -> Vista: Ficha del cliente
		Tarjeta de alerta
			Nombre de la empresa
			Producto de la última compra
			Monto
			Días restantes
			Botón: Ver ficha -> Vista: Ficha del cliente
			Botón: Posponer
	Sección: Actividades del día
		Lista de llamadas pendientes

Vista: Ficha del cliente
	Enlace: Volver al Dashboard -> Vista: Dashboard del Encargado de Ventas
	Nombre de la empresa
	RUC
	Contacto principal
		Nombre
		Teléfono
	Encargado asignado
	Sección: Última compra
		Producto
		Cantidad
		Monto
		Fecha de cierre
		Campo editable: Ciclo de recompra (días)
		Fecha de alerta calculada
	Sección: Notas del encargado de ventas
		Texto libre editable
	Sección: Acciones
		Botón: Registrar contacto -> Modal: Registro de contacto
		Botón: Posponer (N días)
		Botón: Sin oportunidad actual

Modal: Registro de contacto
	Ícono: Cerrar modal
	Selector: Resultado del contacto
		Opción: Interesado en recompra
		Opción: No interesado actualmente
		Opción: No contestó
	Campo: Notas del contacto
	Campo editable: Fecha del próximo seguimiento (default: fecha actual + ciclo de recompra)
	Botón: Guardar y cerrar
	Botón: Cancelar

Vista: Clientes
	Sección: Barra superior
		Nombre del encargado activo
		Ícono: Notificaciones
		Ícono: Ayuda
	Sección: Listado de empresas
		Buscador
		Tarjeta de empresa
			Nombre
			RUC
			Encargado asignado
			Enlace: Ver ficha -> Vista: Ficha del cliente

Vista: Pipeline de Ventas B2B
	Sección: Barra superior
		Nombre del encargado activo
		Ícono: Notificaciones
		Ícono: Ayuda
	Sección: Tablero de etapas
		Columna: Prospecto
		Columna: Cotización enviada
		Columna: Evaluación crediticia
		Columna: Venta cerrada (activa el workflow de alerta automáticamente)
		Columna: Seguimiento activo
		Tarjeta de oportunidad
			Nombre de la empresa
			Monto
			Fecha estimada de cierre

Vista: Panel Gerencial
	Sección: Barra superior
		Nombre del gerente activo
		Ícono: Notificaciones
		Ícono: Ayuda
	Sección: Métricas del equipo
		Contador: Alertas vencidas sin acción
		Contador: Contactos realizados esta semana
		Indicador: Tasa de conversión seguimiento → nueva cotización
	Sección: Filtros
		Selector: Filtrar por encargado de ventas
		Selector: Filtrar por período
	Sección: Tabla de seguimiento
		Fila por encargado de ventas
			Nombre del encargado de ventas
			Alertas vencidas
			Contactos registrados
			Conversión
```

[/arquitectura]
