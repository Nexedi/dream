from dream.plugins import plugin
import datetime

class GetCurrentTime(plugin.InputPreparationPlugin):
    """ Input preparation 
        if there is no current time defined it gets it from the system
    """

    def preprocess(self, data):
        currentTime=data['general'].get('currentDate',None)
        print '----',currentTime
        if not currentTime:
            currentTime=datetime.datetime.now()
            year=currentTime.year
            month=currentTime.month
            day=currentTime.day
            minute=currentTime.minute
            hour=currentTime.hour
            minute=currentTime.minute
            second=currentTime.second
            dateFormat=data['general'].get('dateFormat','%Y/%m/%d %H:%M')
            if dateFormat=='%Y/%m/%d %H:%M:%S':
                currentTimeString=str(year)+'/'+str(month).zfill(2)+'/'+str(day).zfill(2)+' '+str(hour).zfill(2)+':'+str(minute).zfill(2)+':'+str(second).zfill(2)
            elif dateFormat=='%Y/%m/%d %H:%M':
                currentTimeString=str(year)+'/'+str(month).zfill(2)+'/'+str(day).zfill(2)+' '+str(hour).zfill(2)+':'+str(minute).zfill(2)
            elif dateFormat=='%Y/%m/%d':
                currentTimeString=str(year)+'/'+str(month).zfill(2)+'/'+str(day).zfill(2)
            print currentTimeString
            data['general']['currentDate']=currentTimeString      
        return data