import os
from flask import Flask, Blueprint, Response, request, render_template, send_from_directory
import inspect
from logger import Logger
from json import dumps

TAB = "  "
LNF = "\n"
target_module = None
target = None
module = None

class AutoAPI:
  """
  Creates a generic API based on a given class by name
  """

  class CallablesProxies:
    """
    This class should hold the application's functions to interface
    """
    pass

  @staticmethod
  def instantiate_service(tgt, mdl_nm):
    global target_module, target, module_name
    target = tgt
    module_name = mdl_nm
    exec(f'from {target} import {module_name}', globals(), locals())
    exec(f'print("Loaded {module_name} instance successfully")')
    target_module = locals()[f"{module_name}"]
    return [func for func in dir(target_module) if callable(getattr(target_module, func)) and not func.startswith("__")]

  @staticmethod
  def auto_extract_https_methods(fn_names_list):
    """
    Automatically extracts canonical HTTP methods from the names mentioned in the list :param fn_names_list
    :param fn_names_list: a string list containing the wanted names of the methods
    :return: a list of lists containing strings of canonical HTTP methods understandable by `Flask`.
    """
    aggregated_methods_list = []
    methods_list = []
    http_methods = ["COPY", "DELETE", "GET", "HEAD","LINK", "LOCK", "OPTIONS", \
      "PATCH", "POST", "PROPFIND", "PURGE", "PUT", "UNLINK", "UNLOCK", "VIEW"]
    for fn_name in fn_names_list:
      for http_method in http_methods:
        if http_method + "_" in fn_name.upper():
          methods_list.append(http_method)
      if not methods_list:
        methods_list = ["GET"]
      aggregated_methods_list.append(methods_list)
      methods_list = []
    return aggregated_methods_list

  @staticmethod
  def exclude_from_list(complete_list, raw_exclusion_list):
    result = []
    for item in complete_list:
      if item not in raw_exclusion_list:
        result.append(item)
      else:
        raw_exclusion_list.remove(item)
    if len(raw_exclusion_list) != 0:
      Logger.warn('Unrecognized method name' + raw_exclusion_list)
    return result

  @staticmethod
  def include_from_list(complete_list, raw_inclusion_list):
    result = []
    for item in complete_list:
      if item in raw_inclusion_list:
        result.append(item)
        raw_inclusion_list.remove(item)
    if len(raw_inclusion_list) != 0:
      Logger.warn('Unrecognized method name' + raw_inclusion_list)
    return result

  @staticmethod
  def make_fun(fn_name, fn_params, fn_defaults, fn_defaults_dt, strict_parameters_resolution, ignore_defaults):
    global target, module_name
    def process_per_class(var, class_name):
      if 'str' == class_name:
        return '\"' + str(var) + '\"'
      elif 'dict' == class_name:
        return str(var).replace("'", "\"")
      elif all(number == class_name for number in ['int', 'float', 'complex']):
        return getattr(__builtins__, class_name)(var)
      else:
        return str(var)
    
    complete_params = ', '.join(fn_params)

    # Build a runtime function body
    fn_body = f"def {fn_name}():" + LNF
    for i in range(len(fn_params)):
      param = fn_params[i]
      if strict_parameters_resolution:
        fn_body += TAB + param + ' = request.args["' + param + '"]'
      else:
        fn_body += TAB + param + ' = request.args.get("' + param + '")'
      if fn_defaults[i] != '' or ignore_defaults:
        fn_body += ' or ' + process_per_class(str(fn_defaults[i]), fn_defaults_dt[i])
      fn_body += LNF
    fn_body += TAB + f"return_value = getattr(target_module,'{fn_name}')({complete_params})" + LNF
    fn_body += TAB + f"if 'dict' in str(type(return_value)):" + LNF
    fn_body += TAB*2 + f"return Response(dumps(return_value), mimetype='application/json')" + LNF

    fn_body += TAB + f"else:" + LNF
    fn_body += TAB*2 + f"return str(return_value)" + LNF

    Logger.color(LNF + \
      '======================= ' + f'{fn_name}' + ' =======================\n' + \
      fn_body + LNF + \
      '====================================================================' + LNF, Logger.TextColor.YELLOW)

    exec(fn_body, globals(), locals())
    return locals()[fn_name]

  def add_endpoint(self, index):
    global target_module
    fn_name = self.fn_names_list[index]
    if fn_name in dir(self.CallablesProxies):
      Logger.warn("Duplicate function definition discarded for:" + fn_name)
      return
    fn_pointer = getattr(target_module, fn_name)
    fn_params = list(inspect.signature(fn_pointer).parameters.keys())
    found_self = 'self' in fn_params
    if found_self:
      found_self = True
      fn_params.remove('self')
    fn_defaults = list(inspect.signature(fn_pointer).parameters.values())
    if found_self:
      fn_defaults.pop(0)
    fn_defaults_dt = []
    for i in range(len(fn_defaults)):
      fn_defaults[i] = fn_defaults[i].default if fn_defaults[i].default is not inspect.Parameter.empty else ''
    for fn_def in fn_defaults:
      fn_defaults_dt.append(str(type(fn_def)))
    # Save at self
    self.fn_params.append(fn_params)
    self.fn_defaults.append(fn_defaults)
    self.fn_defaults_dt.append(fn_defaults_dt)

    proxy_fn = self.make_fun(fn_name, fn_params, fn_defaults, fn_defaults_dt, self.strict_parameters_resolution,
                 self.enforce_blank_defaults)
    setattr(self.CallablesProxies, fn_name, proxy_fn)
    self.api_routes.route("/" + fn_name, methods=self.http_methods_list[index])(proxy_fn)
    Logger.info(' '.join([
      "\u2713 Binding fn:[", fn_name, "] to: endpoint [", self.endpoints_list[index], "]" + LNF,
      "accepting the HTTP methods:", str(self.http_methods_list[index]), LNF,
      "running on variables:", str(fn_params), "of the datatypes", str(fn_defaults_dt), "at:", str(proxy_fn)]))

  def create_app(self, module_name):
    app = Flask(module_name, instance_relative_config=False)
    app.url_map.strict_slashes = self.strict_slashes
    app.register_blueprint(self.api_routes, url_prefix='/' + self.prefix)

    @app.route('/')
    def root():
      return '</br>'.join([
        '{appName} application running'.format(appName=module_name)])
    
    @app.route('/favicon.ico')
    def favicon():
      return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.errorhandler(400)
    @app.errorhandler(404)
    def not_available(error):
      return render_template('40x.html', title='Unavailable',
                   details='The access request you have made is not valid/available',
                   error=str(error)), 404
    
    return app

  def __init__(self, target, module_name, prefix='auto', exclusion_list=[], inclusion_list=[],
         http_methods_list=[], endpoints_list=[], strict_parameters_resolution=False, strict_slashes=False,
         ignore_defaults=False, host='0.0.0.0', port=5000):

    # Store the original parameters
    self.target = target
    self.module_name = module_name
    self.prefix = prefix
    self.exclusion_list = exclusion_list
    self.inclusion_list = inclusion_list
    self.http_methods_list = http_methods_list
    self.endpoints_list = endpoints_list
    self.strict_parameters_resolution = strict_parameters_resolution
    self.strict_slashes = strict_slashes
    self.enforce_blank_defaults = ignore_defaults
    self.host = host
    self.port = port
    self.fn_defaults = []
    self.fn_defaults_dt = []
    self.fn_params = []

    # Dynamically import the `module_name` class from the target `python` file
    #  and loads all of the methods there is unless excluded
    self.fn_names_list = self.instantiate_service(self.target, self.module_name)
    self.fn_names_list = self.include_from_list(self.fn_names_list, self.inclusion_list)\
      if self.inclusion_list else self.fn_names_list
    self.fn_names_list = self.exclude_from_list(self.fn_names_list, self.exclusion_list)\
      if self.exclusion_list else self.fn_names_list
    self.endpoints_list = self.fn_names_list \
      if not self.endpoints_list else self.endpoints_list
    self.http_methods_list = self.auto_extract_https_methods(self.fn_names_list)\
      if not self.http_methods_list else self.http_methods_list
    self.api_routes = Blueprint(module_name, __name__)

    for index in range(len(self.endpoints_list)):
      self.add_endpoint(index)

    self.app = self.create_app(module_name)
    Logger.info('Routes Map:')
    Logger.info(self.app.url_map)