from orionis.foundation.application import Application, IApplication

app:IApplication = Application()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False
)
app.create()

# # from orionis.services.environment.core.dot_env import DotEnv
# # env = DotEnv()