import inspect


class Service:
    """
    I'm service and I know it
    """
    @staticmethod
    def get_demo():
        """
        This function serves no purpose rather than showing this stupid message in marquee!!
        """
        return '<marquee scrollamount="30"><h1>' + \
               getattr(Service, inspect.currentframe().f_code.co_name).__doc__ + \
               '</marquee>'

    @staticmethod
    def get_a(p1: int):
        """
        Description for get_a
        :param p1 just a random parameter
        :return returns the description of the function
        """
        if p1 is None:
            return 'Set a value for p1 please...'
        return '<br>'.join([getattr(Service, inspect.currentframe().f_code.co_name).__doc__, str(p1)])

    def get_b(self, pa1='alpha', pa2=10, pa3=True):
        """
        Description for get_b
        """
        return '<br>'.join([getattr(Service, inspect.currentframe().f_code.co_name).__doc__,
                            str(pa1), str(pa2), str(pa3)])

    def get_c(self):
        return self.__doc__

    def get_post_d(self, par1=[1, 2, 3, 4]):
        "Aight"
        try:
            return '<br>'.join([getattr(Service, inspect.currentframe().f_code.co_name).__doc__, str(par1)])
        except:
            return 'Seriously dude throw in a description for this function!!'

    def delete_e(self, param1={'some': 'map'}):
        """
        I ain't deleting no BS bro
        """
        return '<br>'.join([getattr(Service, inspect.currentframe().f_code.co_name).__doc__, str(param1)])

