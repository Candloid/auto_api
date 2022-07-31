from auto_api import AutoAPI
import os


if __name__ == "__main__":
  host = '127.0.0.1'; port = 5000
  os.system(f"rundll32 url.dll,FileProtocolHandler http://{host}:{port}")
  api = AutoAPI(target='source', module_name='MainModule', prefix='', \
    strict_parameters_resolution=False, ignore_defaults=False, host=host, port=port)
  api.app.run(debug=True, host=host, port=port)