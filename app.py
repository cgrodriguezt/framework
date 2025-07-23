# from orionis import IOrionis, Orionis

# app:IOrionis = Orionis()
# app.create()

import json

from orionis.foundation.config.startup import Configuration

print(json.dumps(Configuration().getFields(), indent=4))