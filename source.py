import inspect


class MainModule:
  """
  I'm Module and I know it
  """

  def __init__(self):
    print("Source module got initiated...")
  

  def get_some_sleep(self, really):
    return really


  @staticmethod
  def welcome():
    """
    This function serves no purpose other than showing this stupid message in marquee!!
    """
    return '<marquee scrollamount="30"><h1>' + \
      getattr(MainModule, inspect.currentframe().f_code.co_name).__doc__ + \
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
    return int(p1)+5

  def get_b(self, pa1='alpha', pa2=10, pa3=True):
    """
    Description for get_b
    """
    return '<br>'.join([getattr(MainModule, inspect.currentframe().f_code.co_name).__doc__,
              str(pa1), str(pa2), str(pa3)])

  def get_c(self):
    return self.__doc__

  def get_post_d(self, par1=[1, 2, 3, 4]):
    """
    Aight
    """
    return f'The type is: [{str(type(par1))}]'
  
  def get_e(self, d={1:2, 2:4, 4:8}):
    """
    Aight
    """
    return d

  def delete_f(self, param1={'some': 'map'}):
    """
    I ain't deleting nothing bro
    """
    return '<br>'.join([getattr(MainModule, inspect.currentframe().f_code.co_name).__doc__, str(param1)])

