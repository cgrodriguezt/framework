import time
from orionis import Orionis, IOrionis

app: IOrionis = Orionis()
# app.load([
#     # Add your service providers here
# ])

workers = app.make('core.orionis.workers')

# Start time measurement
start_time = time.time()

result = workers.calculate()  # 12

# End time measurement
end_time = time.time()

# Calculate milliseconds
elapsed_ms = (end_time - start_time) * 1000

print(f"Result: {result}")
print(f"Execution time: {elapsed_ms:.4f} milliseconds")