
from instapy import multiaccount
multiaccount.run()

"""
  TODO:
  Implement a process fork on each bot that 
  will watch for changes in accunt configuration and
  dispatch action based on that
  eg: if backend for some reason stop the both
  we should call session.end()
"""
