from orionis import IOrionis, Orionis

app:IOrionis = Orionis()
app.withProviders([
    # ... Your service providers here ...
])
app.create()