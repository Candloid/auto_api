from flask import Flask, Blueprint, render_template, request
import inspect
from logger import Logger
import itertools


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
    def make_fun(fn_name, fn_params, strict_parameters_resolution):
        complete_params = ', '.join(fn_params)

        # Build a runtime function body
        fn_body = f"from flask import request\n" +\
                  f"\n" +\
                  f"\n" +\
                  f"def {fn_name}():\n"
        for param in fn_params:
            if strict_parameters_resolution:
                fn_body += "\t" + param + ' = request.args["' + param + '"]\n'
            else:
                fn_body += "\t" + param + ' = request.args.get("' + param + '")\n'
        fn_body += f"\treturn svc.{fn_name}({complete_params})\n"
        '''
        Logger.info(f'=== Creating {fn_name} ===\n' +
                    fn_body +
                    '\n==================\n')
        '''
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

        proxy_fn = self.make_fun(fn_name, fn_params, self.strict_parameters_resolution)
        setattr(self.ArgumentsBucket, fn_name, proxy_fn)
        self.api_routes.route("/" + fn_name)(proxy_fn)
        Logger.info(' '.join(["\u2713 Binding fn:[", fn_name, "] to: endpoint [", self.endpoints_list[index], "]",
                              "accepting HTTP methods:[", str(self.http_methods_list[index]),
                              "] by matching the variables:", str(fn_params), "at the function:[", str(proxy_fn), "]"]))

    def create_app(self, module_name):
        """
        Initialize the core application
        :param module_name:
        :return:
        """
        app = Flask(module_name, instance_relative_config=False)
        app.url_map.strict_slashes = False
        app.register_blueprint(self.api_routes, url_prefix='/' + self.prefix)

        @app.route('/')
        def root():
            return '</br>'.join([
                '{appName} application running'.format(appName=module_name)])

        @app.errorhandler(404)
        def page_not_found(error):
            return render_template('40x.html', title='Page not found',
                                   going_on='The page you are trying to access is not available',
                                   body=str(error)), 404

        @app.errorhandler(400)
        def bad_request(error):
            return render_template('40x.html', title='Bad request',
                                   going_on='The way you have called the endpoint is not correct.',
                                   body=str(error)), 404

        @app.route('/postman')
        def get_postman_json():
            fn_pairs = []
            for index in range(len(self.fn_names_list)):
                fn_pairs.extend(list(itertools.product(self.fn_names_list[index], self.http_methods_list[index])))

            short_host = ''
            for char in self.host:
                if char.isdigit() or char == '.':
                    short_host += char
            host_a, host_b, host_c, host_d = short_host.split('.')

            short_host.replace('/','')
            params={}
            params['app_name']=self.module_name
            params['raw_host']="http://"+short_host+'/'
            params['host_a']=host_a
            params['host_b']=host_b
            params['host_c']=host_c
            params['host_d']=host_d
            return render_template('auto_api.postman_collection.json', app_name=self.module_name,
                                   raw_host='', host_a=, host_b=, host_c=, host_d=)

        root()
        return app

    def __init__(self, target, module_name, prefix='auto', exclusion_list=[], inclusion_list=[],
                 http_methods_list=[], endpoints_list=[], strict_parameters_resolution=False, host='0.0.0.0'):

        # Store the original parameters
        self.target = target
        self.module_name = module_name
        self.prefix = prefix
        self.exclusion_list = exclusion_list
        self.inclusion_list = inclusion_list
        self.http_methods_list = http_methods_list
        self.endpoints_list = endpoints_list
        self.strict_parameters_resolution = strict_parameters_resolution
        self.host = host

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
        auto_api.run(debug=True, host=self.host)


if __name__ == "__main__":
    b_api = BuildAPI(target='target', module_name='Service', prefix='', strict_parameters_resolution=True)
