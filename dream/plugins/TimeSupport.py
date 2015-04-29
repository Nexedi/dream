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
    self.timeUnit = data['general']['timeUnit']
    if self.timeUnit == 'second':
      self.timeUnitPerDay = 24 * 60 * 60.
    elif self.timeUnit == 'minute':
      self.timeUnitPerDay = 24 * 60.
    elif self.timeUnit == 'hour':
      self.timeUnitPerDay = 24.
    elif self.timeUnit == 'day':
      self.timeUnitPerDay = 1.
    elif self.timeUnit == 'week':
      self.timeUnitPerDay = 1 / 7.
    elif self.timeUnit == 'month':
      self.timeUnitPerDay = 1 / 30.
    elif self.timeUnit == 'year':
      self.timeUnitPerDay = 1 / 360.
    else:
      raise ValueError("Unsupported time unit %s" % self.timeUnit)

    self.dateFormat = data['general'].get('dateFormat', '%Y/%m/%d %H:%M:%S')
    # Convert simulation 0 time to real world time
    self.now = datetime.strptime(data['general']['currentDate'], self.dateFormat)
    self.initialized = True

  def convertToRealWorldTime(self, simulation_time):
    """Convert simulation clock time to real world time, as python datetime object.
    """
    assert self.initialized, "initializeTimeSupport has not been called"
    assert not simulation_time==float("inf"), "cannot convert infinite simulation time to real world time"
    return self.now + timedelta(days=simulation_time/self.timeUnitPerDay)

  def convertToFormattedRealWorldTime(self, simulation_time):
    """Convert simulation clock time to real world time, as string formatted according to general dateFormat
    """
    assert self.initialized, "initializeTimeSupport has not been called"
    return (self.now + timedelta(days=simulation_time/self.timeUnitPerDay)).strftime(self.dateFormat)

  def convertToTimeStamp(self, simulation_time):
    """Convert simulation clock time to real world time, as timestamp.
    """
    return (self.convertToRealWorldTime(simulation_time) - datetime(1970, 1, 1)).total_seconds()

  def convertToSimulationTime(self, real_world_time):
    """Convert real world time (as python datetime object) to simulation clock time.
    """
    assert self.initialized, "initializeTimeSupport has not been called"
    # get the seconds difference and divide by (24*60*60/self.timeUnitPerDay)
    # 24*60*60 is timeUnitPerDay if the unit is seconds
    return (real_world_time - self.now).total_seconds()/(86400/self.timeUnitPerDay)

  def getTimeUnitText(self):
    """Return the time unit as text.
    """
    assert self.initialized, "initializeTimeSupport has not been called"
    return self.timeUnit
