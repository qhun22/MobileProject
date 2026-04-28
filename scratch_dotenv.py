import os
from dotenv import load_dotenv

with open('.env.test', 'w') as f:
    f.write('MY_VAR=from_env\n')

os.environ['MY_VAR'] = ''
load_dotenv('.env.test')
print(f"MY_VAR is: '{os.getenv('MY_VAR')}'")

os.environ['MY_VAR_2'] = 'from_os'
with open('.env.test2', 'w') as f:
    f.write('MY_VAR_2=from_env\n')
load_dotenv('.env.test2')
print(f"MY_VAR_2 is: '{os.getenv('MY_VAR_2')}'")
