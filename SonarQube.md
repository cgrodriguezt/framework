# Configuración recomendada de SonarLint/SonarQube

Teniendo en cuenta que el framework está inspirado en la convención de nomenclatura de **frameworks web modernos**, es necesario realizar algunos ajustes en **SonarQube/SonarLint** para evitar falsos positivos durante el análisis estático.

## Reglas sugeridas en `settings.json`

```json
"sonarlint.rules": {
    "python:S100": {
        "level": "on",
        "parameters": {
            "format": "^_{0,2}[a-z][a-zA-Z0-9]*_{0,2}$"
        }
    },
    "python:S2638": {
        "level": "off"
    }
},
"sonarlint.automaticAnalysis": true
```

### Explicación de las reglas

* **`python:S100`** → Permite definir nombres de métodos con guiones bajos iniciales o con estructura tipo camelCase (`_metodo`, `miMetodo`, etc.), alineados con el estilo del framework inspirado en patrones de desarrollo web modernos.

* **`python:S2638`** → Se desactiva, ya que no reconoce de forma implícita la sintaxis de inyección de dependencias utilizada en el framework.

## Manejo de Complejidad Cognitiva (`python:S3776`)

Es posible que ciertos métodos superen el límite de complejidad cognitiva por defecto de **15**.

### Recomendación

**No desactivar la regla globalmente**. En su lugar:

1. Marca únicamente el método afectado con `# NOSONAR` para casos puntuales
2. Esto mantiene la evaluación del resto del código bajo la regla

```python
def metodo_complejo(...):  # NOSONAR
    # Lógica compleja que requiere excepción
    ...
```

> **Nota:** Usar `# NOSONAR` con moderación y solo cuando la complejidad sea justificada por la naturaleza del problema a resolver.

---

# Recommended SonarLint/SonarQube Configuration

Given that the framework is inspired by **modern web frameworks** naming conventions, some adjustments in **SonarQube/SonarLint** are necessary to avoid false positives during static analysis.

## Suggested rules in `settings.json`

```json
"sonarlint.rules": {
    "python:S100": {
        "level": "on",
        "parameters": {
            "format": "^_{0,2}[a-z][a-zA-Z0-9]*_{0,2}$"
        }
    },
    "python:S2638": {
        "level": "off"
    }
},
"sonarlint.automaticAnalysis": true
```

### Rules explanation

* **`python:S100`** → Allows defining method names with initial underscores or camelCase structure (`_method`, `myMethod`, etc.), aligned with the framework style inspired by modern web development patterns.

* **`python:S2638`** → Disabled, as it doesn't implicitly recognize the dependency injection syntax used in the framework.

## Cognitive Complexity Management (`python:S3776`)

Some methods might exceed the default cognitive complexity limit of **15**.

### Recommendation

**Don't disable the rule globally**. Instead:

1. Mark only the affected method with `# NOSONAR` for specific cases
2. This keeps the evaluation of the rest of the code under the rule

```python
def complex_method(...):  # NOSONAR
    # Complex logic that requires exception
    ...
```

> **Note:** Use `# NOSONAR` moderately and only when complexity is justified by the nature of the problem to solve.