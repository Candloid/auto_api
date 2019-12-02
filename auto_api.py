from flask import Flask, Blueprint, render_template, render_template_string, jsonify
import inspect
from logger import Logger


class BuildAPI:
    """
    Creates a generic API based on a given class by name
    """

    class ArgumentsBucket:
        """
        This empty class will hold the functions necessary for interfacing later
        """
        pass

    @staticmethod
    def instantiate_service(target, module_name):
        exec(f'from {target} import {module_name}')
        exec(f'global svc; svc = {module_name}(); print("Loaded " + str(svc) + " instance successfully")')
        return [func for func in dir(svc) if callable(getattr(svc, func)) and not func.startswith("__")]

    @staticmethod
    def auto_extract_https_methods(fn_names_list):
        """
        Automatically extracts canonical HTTP methods from the names mentioned in the list :param fn_names_list
        :param fn_names_list: a string list containing the wanted names of the methods
        :return: a list of lists containing strings of canonical HTTP methods understandable by `Flask`.
        """
        result = []
        instance_list = []
        http_methods = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
        for index in range(len(fn_names_list)):
            for http_method in http_methods:
                if http_method in fn_names_list[index].upper():
                    instance_list.append(http_method)
            if not instance_list:
                result.append('GET')
            else:
                result.append(instance_list)
            instance_list = []
        return result

    @staticmethod
    def exclude_from_list(complete_list, raw_exclusion_list):
        """
        Removes the names of unwanted methods to be mapped from the complete list wanted methods.
        :param complete_list: a string list of all the wanted methods in the target module
        :param raw_exclusion_list: a string list of functions unwanted to be mapped
        :return:
        """
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
    def make_fun(fn_name, fn_params, fn_defaults, fn_defaults_dt, strict_parameters_resolution):
        def process_per_class(var, class_name):
            if 'str' in str(class_name):
                return '\"' + str(var) + '\"'
            elif 'dict' in str(class_name):
                return str(var).replace("'", "\"")
            else:
                return str(var)
        complete_params = ', '.join(fn_params)

        # Build a runtime function body
        fn_body = f"from flask import request\n" +\
                  f"\n" +\
                  f"\n" +\
                  f"def {fn_name}():\n"
        for i in range(len(fn_params)):
            param = fn_params[i]
            if strict_parameters_resolution:
                fn_body += "\t" + param + ' = request.args["' + param + '"]'
            else:
                fn_body += "\t" + param + ' = request.args.get("' + param + '")'
            if fn_defaults[i] != '':
                fn_body += ' or ' + process_per_class(str(fn_defaults[i]), fn_defaults_dt[i]) + '\n'
            else:
                fn_body += '\n'

        fn_body += f"\treturn svc.{fn_name}({complete_params})\n"

        Logger.info(f'\n=== Creating {fn_name} ===\n' + fn_body + '\n==================\n')

        exec(fn_body)
        return locals()[fn_name]

    def add_endpoint(self, index):
        fn_name = self.fn_names_list[index]
        if fn_name in dir(self.ArgumentsBucket):
            Logger.warn("Duplicate function definition discarded for:" + fn_name)
            return
        fn_pointer = getattr(svc, fn_name)
        fn_params = list(inspect.signature(fn_pointer).parameters.keys())
        fn_params = fn_params.remove('self') if 'self' in fn_params else fn_params
        fn_defaults = list(inspect.signature(fn_pointer).parameters.values())
        fn_defaults_dt = []
        for i in range(len(fn_defaults)):
            fn_defaults[i] = fn_defaults[i].default if fn_defaults[i].default is not inspect.Parameter.empty else ''
        for fn_def in fn_defaults:
            fn_defaults_dt.append(type(fn_def))
        # Save at self
        self.fn_params.append(fn_params)
        self.fn_defaults.append(fn_defaults)
        self.fn_defaults_dt.append(fn_defaults_dt)

        proxy_fn = self.make_fun(fn_name, fn_params, fn_defaults, fn_defaults_dt, self.strict_parameters_resolution)
        setattr(self.ArgumentsBucket, fn_name, proxy_fn)
        self.api_routes.route("/" + fn_name)(proxy_fn)
        Logger.info(' '.join(["\u2713 Binding fn:[", fn_name, "] to: endpoint [", self.endpoints_list[index], "]",
                              "accepting HTTP methods:[", str(self.http_methods_list[index]),
                              "] by matching the variables:", str(fn_params), "with the defaults classed as:",
                              str(fn_defaults_dt), "at the function:[", str(proxy_fn), "]"]))

    def create_app(self, module_name):
        """
        Initialize the core application
        :param module_name:
        :return:
        """
        app = Flask(module_name, instance_relative_config=False)
        app.url_map.strict_slashes = self.strict_slashes
        app.register_blueprint(self.api_routes, url_prefix='/' + self.prefix)

        @app.route('/')
        def root():
            return '</br>'.join([
                '{appName} application running'.format(appName=module_name)])

        @app.route('/postman')
        def get_postman_json():
            short_host = ''
            for char in self.host:
                if char.isdigit() or char == '.':
                    short_host += char
            host_a, host_b, host_c, host_d = short_host.split('.')
            len_fn_params = [len(pars) for pars in self.fn_params]
            len_http_methods_list = [len(httpm) for httpm in self.http_methods_list]

            # Masquerade dictionaries with text codes
            substitution_dictionary = {}
            for i in range(len(self.fn_defaults_dt)):
                for j in range(len(self.fn_defaults_dt[i])):
                    if 'dict' in str(self.fn_defaults_dt[i][j]):
                        value = self.fn_defaults[i][j]
                        ddph_id = 'ddph_id' + str(i) + str(j)
                        self.fn_defaults[i][j] = ddph_id
                        substitution_dictionary[ddph_id] = str(value)

            params = {
                "app_name": self.module_name,
                "fn_names_list": self.fn_names_list,
                "len_fn_names_list": len(self.fn_names_list),
                "http_methods_list": self.http_methods_list,
                "len_http_methods_list": len_http_methods_list,
                "endpoints": self.endpoints_list,
                "fn_params": self.fn_params,
                "len_fn_params": len_fn_params,
                "fn_defaults": self.fn_defaults,
                "host_a": host_a,
                "host_b": host_b,
                "host_c": host_c,
                "host_d": host_d,
                "port": self.port,
                "prefix": self.prefix
            }
            Logger.info(str(params))
            with open('auto_api_postman_collection_template.json', 'r') as file:
                data = file.read()
            json_string = render_template_string(data, **params)
            print(substitution_dictionary)
            for entry in substitution_dictionary:
                value = substitution_dictionary[entry]
                json_string = json_string.replace(entry, value)
            ep_response = app.response_class(
                response=json_string,
                status=200,
                mimetype='application/json'
            )

            for i in range(len(self.fn_defaults_dt)):
                for j in range(len(self.fn_defaults_dt[i])):
                    if 'dict' in str(self.fn_defaults_dt[i][j]) and 'ddph_id' in self.fn_defaults[i][j]:
                        self.fn_defaults[i][j] = substitution_dictionary[self.fn_defaults[i][j]]

            return ep_response

        @app.errorhandler(400)
        @app.errorhandler(404)
        def not_available(error):
            return render_template('40x.html', title='Unavailable',
                                   details='The access request you have made is not valid/available',
                                   error=str(error)), 404
        return app

    def __init__(self, target, module_name, prefix='auto', exclusion_list=[], inclusion_list=[],
                 http_methods_list=[], endpoints_list=[], strict_parameters_resolution=False, strict_slashes=False,
                 host='0.0.0.0', port=5000):

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

        auto_api = self.create_app(module_name)
        Logger.info('Routes Map:')
        Logger.info(auto_api.url_map)
        auto_api.run(debug=True, host=self.host, port=self.port)


if __name__ == "__main__":
    b_api = BuildAPI(target='target', module_name='Service', prefix='', strict_parameters_resolution=False)
