from orionis.app import Orionis

app = Orionis()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False
)
app.create()