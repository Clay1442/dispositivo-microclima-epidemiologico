import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

config = f"""window.SAVA_CONFIG = {{
  influxUrl:    "{os.getenv('INFLUX_URL', '')}",
  influxToken:  "{os.getenv('INFLUX_TOKEN', '')}",
  influxOrg:    "{os.getenv('INFLUX_ORG', '')}",
  influxBucket: "{os.getenv('INFLUX_BUCKET', '')}"
}};
"""

output = os.path.join(os.path.dirname(__file__), 'js', 'config.js')
with open(output, 'w') as f:
    f.write(config)

print("✓ js/config.js gerado com sucesso")
