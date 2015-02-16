from datetime import datetime
from datetime import timedelta
import random
from pprint import pformat

from dream.plugins import plugin

class TimeSupportMixin(object):
  """Helper methods to handle time units.
  """
  initialized = False

  def initializeTimeSupport(self, data):
    self.timeUnitPerDay = data['general']['timeUnitPerDay']
    self.dateFormat = data['general'].get('dateFormat', '%Y/%m/%d %H:%M:%S')
    # Convert simulation 0 time to real world time
    self.now = datetime.strptime(data['general']['currentDate'], self.dateFormat)
    self.initialized = True

  def convertToRealWorldTime(self, simulation_time):
    """Convert simulation clock time to real world time, as python datetime object.
    """
    assert self.initialized, "initializeTimeSupport has not been called"
    return self.now + timedelta(days=simulation_time/self.timeUnitPerDay)

  def convertToSimulationTime(self, real_world_time):
    """Convert real world time (as python datetime object) to simulation clock time.
    """
    assert self.initialized, "initializeTimeSupport has not been called"
    raise NotImplementedError

  def getTimeUnitText(self):
    """Return the time unit as text.
    """
    assert self.initialized, "initializeTimeSupport has not been called"
    if self.timeUnitPerDay == 24 * 60:
      return 'minute'
    if self.timeUnitPerDay == 24:
      return 'hour'
    if self.timeUnitPerDay == 1:
      return 'day'
    if self.timeUnitPerDay == 1/7.:
      return 'week'
    if self.timeUnitPerDay == 1/30.:
      return 'month'
    if timeUnitPerDay == 1/360.:
      return 'year'
    raise ValueError("Unsupported time unit %s" % self.timeUnitPerDay)

