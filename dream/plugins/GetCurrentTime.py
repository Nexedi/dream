from dream.plugins import plugin
import datetime

class GetCurrentTime(plugin.InputPreparationPlugin):
    """ Input preparation 
        if there is no current time defined it gets it from the system
    """

    def preprocess(self, data):
        currentTime=data['general'].get('currentDate',None)
        if not currentTime:
            currentTime=datetime.datetime.now()
            dateFormat=data['general'].get('dateFormat','%Y/%m/%d %H:%M')
            data['general']['currentDate']=currentTime.strftime(dateFormat)               
        return data