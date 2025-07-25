from orionis import IOrionis, Orionis

app:IOrionis = Orionis()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False
)
app.create()

