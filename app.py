from orionis import IOrionis, Orionis

app:IOrionis = Orionis()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False,
    folder_path=[

        # Console Services
        "console/base",
        "console/debug",
        "console/dynamic",
        "console/output",

        "container/context",
        "container/entities",
        "container/facades",
        "container/providers",
        "container/resolver",
        "container",

        # Example
        "example",

        # Metadata Framework
        "metadata",

        # Services
        "services/asynchrony",
        "services/system",
    ]
)
app.create()

# from enum import Enum
# from orionis.services.environment.core.dot_env import DotEnv
# from orionis.services.environment.enums.cast_type import EnvCastType


# env = DotEnv()
# env.set("NOMBRE", 1243, EnvCastType.INT)