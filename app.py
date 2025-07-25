from orionis import IOrionis, Orionis

app:IOrionis = Orionis()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False,
    folder_path=[
        "example",
        "console/base",
        "console/debug",
        "console/dynamic",
        "console/output",
    ]
)
app.create()