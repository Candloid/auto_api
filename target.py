import inspect


class Service:
    """
    I'm service and I know it
    """
    @staticmethod
    def get_demo():
        """
        Description for get_demo
        """
        return '<marquee><h1>' + inspect.currentframe().f_code.co_name + '</marquee>'

    @staticmethod
    def get_a(p1: int):
        """
        Description for get_a
        """
        if p1 is None:
            return 'Set a value for p1 please...'
        return '<br>'.join([inspect.currentframe().f_code.co_name, str(p1), Service.get_b.__doc__])

    def get_b(self, pa1='alpha', pa2=10, pa3=True):
        """
        Description for get_b
        """
        return '<br>'.join([inspect.currentframe().f_code.co_name, str([pa1, pa2, pa3]), self.get_b.__doc__])

    def get_c(self):
        return self.__doc__

    def get_post_d(self, par1=[1, 2, 3, 4]):
        return '<br>'.join([inspect.currentframe().f_code.co_name, str(par1), self.get_b.__doc__])

    def delete_e(self, param1={'some': 'map'}):
        return '<br>'.join([inspect.currentframe().f_code.co_name, str(param1), self.get_b.__doc__])
