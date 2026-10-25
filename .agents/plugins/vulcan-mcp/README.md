# Maptek Vulcan MCP Plugin (Google Antigravity)

Plugin nativo de **Google Antigravity** ubicado en `.agents/plugins/vulcan-mcp/` para integrar **Maptek Vulcan 12 Desktop** directamente con el entorno de agentes.

---

## Estructura del Plugin

```text
.agents/plugins/vulcan-mcp/
├── plugin.json                         # Manifiesto oficial del plugin
├── mcp_config.json                     # Lanzador automático del servidor MCP vía uv
├── hooks.json                          # Hook PreInvocation que verifica el puerto TCP 9877
├── README.md                           # Este documento
├── agents/
│   └── mining-geologist.md             # Agente Especialista en Geología y Planificación Minera
├── rules/
│   └── AGENTS.md                       # Reglas permanentes activas mientras el plugin está habilitado
└── skills/
    ├── vulcan-tools-catalog/SKILL.md   # Catálogo de las 9 Herramientas Maestras MCP
    ├── vulcan-file-formats/SKILL.md    # Especificación de formatos .bmf, .00t, .dgd.isis, .dhd.isis, .scd
    ├── vulcan-python-sdk/SKILL.md      # Referencia de maptek.vulcan, maptek.vulcan_gui y mapteksdk 2.0
    └── vulcan-workflow/SKILL.md        # Flujos guiados de auditoría, cubicación y sondajes
```

---

## Componentes Incluidos

1. **Servidor MCP (`mcp_config.json`)**:
   * Registra el servidor `vulcan` ejecutando `uv run --directory <proyecto> vulcan-mcp-server`.
   * Lee automáticamente `VULCAN_MCP_TOKEN` desde el sistema o desde el archivo `.env` de la raíz del proyecto.
2. **Agente Personalizado (`agents/mining-geologist.md`)**:
   * **Identificador**: `mining-geologist` (*Vulcan Mining Specialist*).
   * **Capacidades**: Acceso completo a las 9 herramientas maestras de Vulcan y a las 4 skills especializadas.
3. **4 Skills de Divulgación Progresiva (`skills/*/SKILL.md`)**:
   * Se cargan bajo demanda solo cuando la tarea lo requiere para optimizar el consumo de tokens de contexto.
4. **Hook de Salud (`hooks.json`)**:
   * Antes de cada invocación (`PreInvocation`), comprueba de forma no bloqueante si el socket `127.0.0.1:9877` de Maptek Vulcan está en línea (`ONLINE` / `OFFLINE`).
5. **Reglas Operativas (`rules/AGENTS.md`)**:
   * Garantiza el uso de `uv run`, límites seguros de renderizado 3D (`<= 300` segmentos), soporte de columnas ISIS en español (`BUZ`, `DESDE`) y detección de ventanas modales en Vulcan.
