# System Architecture

## Overview
The bar-directory-recon system is designed as a modular data reconnaissance platform with a clear separation between core pipeline functionality and pluggable components.

## Directory Structure

### `src/` - Core Pipeline
The `src/` directory contains the core ETL pipeline and shared business logic:

- **Job orchestration**: Main pipeline runners and workflow management
- **Data models**: Shared data structures and validation schemas
- **Core utilities**: Common helper functions, configuration management
- **Business logic**: Core processing algorithms and transformation rules
- **Database integration**: Core data persistence and retrieval logic

**Responsibilities:**
- Define the main data processing workflow
- Provide stable APIs for plugin integration
- Handle configuration and environment management
- Manage core data models and schemas
- Implement shared utilities and common patterns

### `universal_recon/` - Plugin System
The `universal_recon/` directory implements a flexible plugin architecture:

- **Plugin interface**: Base classes and contracts for plugin development
- **Source adapters**: Connectors for different data sources (web scraping, APIs, files)
- **Output adapters**: Formatters and exporters for various output formats
- **Dynamic discovery**: Automatic plugin registration and loading
- **Extension points**: Hooks for custom processing logic

**Responsibilities:**
- Provide extensible interfaces for new data sources
- Enable custom output formats and destinations
- Support dynamic plugin loading and configuration
- Isolate external dependencies and vendor-specific code
- Allow for easy addition of new reconnaissance techniques

## Integration Model

### Plugin Registration
Plugins in `universal_recon/` register themselves with the core system through:
- Entry point discovery mechanisms
- Configuration-based plugin activation
- Runtime plugin management APIs

### Data Flow
1. Core pipeline (`src/`) orchestrates the overall workflow
2. Plugin system (`universal_recon/`) provides specialized processors
3. Data flows through standardized interfaces between core and plugins
4. Results are aggregated and processed by core business logic

### Configuration
- Core configuration managed in `src/config/`
- Plugin-specific configuration isolated in `universal_recon/`
- Environment-specific overrides supported at both levels

## Development Guidelines

### Adding New Features
- **Core functionality**: Add to `src/` if it's essential business logic
- **Data sources**: Add to `universal_recon/` as source plugins
- **Output formats**: Add to `universal_recon/` as output plugins
- **Utilities**: Add to `src/` if widely used, `universal_recon/` if plugin-specific

### Plugin Development
- Implement plugin interfaces defined in `universal_recon/base/`
- Follow the plugin naming convention: `universal_recon.{category}.{name}`
- Include plugin metadata and dependencies in plugin modules
- Write tests that can run independently of core system

### Deployment Considerations
- Core system (`src/`) should be deployable without any plugins
- Plugins can be selectively included based on deployment requirements
- Configuration should support enabling/disabling plugins at runtime
- Dependencies should be isolated to prevent version conflicts

## Future Extensibility
This architecture supports:
- Adding new data sources without modifying core code
- Implementing custom processing workflows through plugin composition
- Supporting multiple output formats and destinations
- Scaling individual components independently
- Testing plugins in isolation from the core system
