from orionis import IOrionis, Orionis

app:IOrionis = Orionis()
app.setConfigTesting(
    execution_mode="sequential",
    persistent=False,
    web_report=False,
    folder_path=[
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
        "example",
        "metadata",
        "services/asynchrony",
        "services/environment",
    ]
)
app.create()