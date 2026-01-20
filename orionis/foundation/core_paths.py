from types import MappingProxyType

CORE_APP_PATHS: MappingProxyType = MappingProxyType({
    "app": "app",
    "console": "app/console",
    "exceptions": "app/exceptions",
    "http": "app/http",
    "models": "app/models",
    "providers": "app/providers",
    "notifications": "app/notifications",
    "services": "app/services",
    "jobs": "app/jobs",
    "bootstrap": "app/bootstrap",
    "config": "config",
    "database": "database/database",
    "resources": "resources",
    "routes": "routes",
    "storage": "storage",
    "tests": "tests",
})
