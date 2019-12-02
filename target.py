import inspect


class Service:
    """
    I'm service and I know it
    """
    @staticmethod
    def get_demo():
        return '<marquee><h1>' + inspect.currentframe().f_code.co_name + '</marquee>'

    @staticmethod
    def get_a(p1):
        if p1 is None:
            return 'Set a value for p1 please...'
        return inspect.currentframe().f_code.co_name + '<br>' + str(p1)

    def get_b(self, pa1='alpha', pa2=10, pa3=True):
        return inspect.currentframe().f_code.co_name + '<br>' + str([pa1, pa2, pa3])

    def get_c(self):
        return self.__doc__

    def get_post_d(self, par1=[1, 2, 3, 4]):
        return inspect.currentframe().f_code.co_name + str(par1)

    def delete_e(self, param1={'some': 'map'}):
        return inspect.currentframe().f_code.co_name + str(param1)
