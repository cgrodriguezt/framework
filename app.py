from orionis import IOrionis, Orionis

app:IOrionis = Orionis()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=True,
    persistent_driver="sqlite",
    web_report=True,
    folder_path=[
        "example",
        "console/base"
    ]
)
app.create()