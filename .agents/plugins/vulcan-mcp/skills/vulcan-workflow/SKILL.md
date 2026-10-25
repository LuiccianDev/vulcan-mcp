---
name: vulcan-workflow
description: Flujos de trabajo guiados para interactuar con Maptek Vulcan 12 a traves de Vulcan MCP (auditoria de proyecto, analisis de modelos de bloques, sondajes y capturas 3D).
---

# Flujos de Trabajo Mineros con Vulcan MCP

Esta skill proporciona los procedimientos recomendados paso a paso para interactuar de forma segura y eficiente con Maptek Vulcan 12 Desktop.

---

## 1. Auditoría Rápida de Proyecto Minero

Cuando el usuario pregunte por el estado general del proyecto o los archivos disponibles:

1. **Verificar Conexión y Proyecto**:
   * Invocar `vulcan_system` con `action="ping"`.
   * Invocar `vulcan_system` con `action="project_info"`.
2. **Listar Modelos y Triangulaciones**:
   * Invocar `vulcan_block_model` con `action="list"`.
   * Invocar `vulcan_triangulation` con `action="list"`.
   * Invocar `vulcan_drillholes` con `action="list_dbs"`.
3. **Reportar un resumen conciso**: Indicar el directorio del proyecto, los modelos de bloques `.bmf` disponibles, las superficies principales `.00t` y las bases de datos de sondajes `.dhd.isis`.

---

## 2. Análisis y Cubicación de Modelo de Bloques

Para responder preguntas de tonelaje, leyes o reservas:

1. Obtener metadatos del modelo:
   * Invocar `vulcan_block_model` con `action="info"`, indicando el nombre del `.bmf`.
   * Identificar las variables disponibles (ej: `CUT`, `DENS`, etc.).
2. Calcular estadísticas y reservas:
   * Invocar `vulcan_block_model` con `action="stats"`, `variable="CUT"`, y si aplica `cutoff=0.5`.
   * Reportar tonelaje total, ley media y porcentaje sobre la ley de corte.

---

## 3. Exploración de Sondajes y Tramos de Alta Ley

1. Consultar el esquema de la base de datos de sondajes:
   * Invocar `vulcan_drillholes` con `action="schema"`, `db="nombre.dhd.isis"`.
2. Identificar intervalos mineralizados:
   * Invocar `vulcan_drillholes` con `action="high_grade"`, `db="...", table="LEYES", field="CUT", min_value=1.0`.
3. Visualización en 3D:
   * Invocar `vulcan_drillholes` con `action="display"`, `limit=10` (para evitar saturar la GUI).
   * Tomar una captura con `vulcan_screenshot` para confirmar la visualización.
