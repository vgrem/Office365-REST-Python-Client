import random
import string

random_seed = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
