from orionis.foundation.application import Application, IApplication

app:IApplication = Application()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False
)
app.create()

# import os
# from orionis.services.environment.core.dot_env import DotEnv
# from orionis.services.environment.enums.value_type import EnvironmentValueType
# env = DotEnv()

# env.set("EXAMPLE_PATH", '/tests', EnvironmentValueType.PATH)
# print(env.get("EXAMPLE_PATH"))

# env.set("EXAMPLE_STR", 'hello', EnvironmentValueType.STR)
# print(env.get("EXAMPLE_STR"))

# env.set("EXAMPLE_INT", 123, EnvironmentValueType.INT)
# print(env.get("EXAMPLE_INT"))

# env.set("EXAMPLE_FLOAT", 3.14, EnvironmentValueType.FLOAT)
# print(env.get("EXAMPLE_FLOAT"))

# env.set("EXAMPLE_BOOL", True, EnvironmentValueType.BOOL)
# print(env.get("EXAMPLE_BOOL"))

# env.set("EXAMPLE_LIST", [1, 2, 3], EnvironmentValueType.LIST)
# print(env.get("EXAMPLE_LIST"))

# env.set("EXAMPLE_DICT", {"a": 1, "b": 2}, EnvironmentValueType.DICT)
# print(env.get("EXAMPLE_DICT"))

# env.set("EXAMPLE_TUPLE", (1, 2), EnvironmentValueType.TUPLE)
# print(env.get("EXAMPLE_TUPLE"))

# env.set("EXAMPLE_SET", {1, 2, 3}, EnvironmentValueType.SET)
# print(env.get("EXAMPLE_SET"))

# env.set("EXAMPLE_BASE64", os.urandom(32).hex(), EnvironmentValueType.BASE64)
# print(env.get("EXAMPLE_BASE64"))

#---------

# env.set("EXAMPLE_PATH", '/tests')
# print(env.get("EXAMPLE_PATH"))

# env.set("EXAMPLE_STR", 'hello')
# print(env.get("EXAMPLE_STR"))

# env.set("EXAMPLE_INT", 123)
# print(env.get("EXAMPLE_INT"))

# env.set("EXAMPLE_FLOAT", 3.14)
# print(env.get("EXAMPLE_FLOAT"))

# env.set("EXAMPLE_BOOL", True)
# print(env.get("EXAMPLE_BOOL"))

# env.set("EXAMPLE_LIST", [1, 2, 3])
# print(env.get("EXAMPLE_LIST"))

# env.set("EXAMPLE_DICT", {"a": 1, "b": 2})
# print(env.get("EXAMPLE_DICT"))

# env.set("EXAMPLE_TUPLE", (1, 2))
# print(env.get("EXAMPLE_TUPLE"))

# env.set("EXAMPLE_SET", {1, 2, 3})
# print(env.get("EXAMPLE_SET"))

# env.set("EXAMPLE_BASE64", "Raul Uñate")
# print(env.get("EXAMPLE_BASE64"))
