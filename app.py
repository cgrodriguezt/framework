from orionis import Orionis, IOrionis

# Create and bootstrap the application with method chaining
app:IOrionis = Orionis()
app.withProviders([
    # Add your service providers here
])
app.create()