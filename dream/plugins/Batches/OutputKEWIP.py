from dream.plugins import plugin

class OutputKEWIP(plugin.OutputPreparationPlugin):
    """ Output the WIP the KE tool return in a DREAM formatted spreadsheet
    """

    def postprocess(self, data):
        # if the wip was defined manually, no report should be given, just a message to explain.
        if data['general'].get('wipSource',None)=='Manually':
            data['result']['result_list'][0][self.configuration_dict['output_id']]=[[
                                        'WIP Was defined Manually. No KE tool Input!'
                                                                                   ]]
            return data
        # if the mode was to read by KE but no spreadsheet was uploaded, give a warning.
        if not data['input'].get('wip_report',{}):
            data['result']['result_list'][0][self.configuration_dict['output_id']]=[[
                                        'Warning! No WIP Report was provided. KE could not be run and no WIP was defined in the model!'
                                                                                   ]]
            return data
            
        # set the titles
        outPutSpreadsheet=[['Station','# units awaiting processing','# units complete but not passed on']]
        nodes=data['graph']['node']
        
        # create rows for all the stations
        for node_id, node in nodes.iteritems():       
            if 'Machine' in node['_class'] or 'M3' in node['_class']:        
                outPutSpreadsheet.append([node_id,0])
        
        # read the input and for the queues that have WIP set the total number of units to the next station
        # WIP from KE tool now is only in Queues but the manual input is done as '# units awaiting processing' in station
        for node_id, node in nodes.iteritems():       
            if 'Queue' in node['_class'] or 'Clearance' in node['_class']:
                wip=node.get('wip',[])
                stationId=self.getNextStation(data, node_id)
                totalUnits=0
                for element in wip:
                    numberOfUnits=element.get('numberOfUnits',0)
                    totalUnits+=numberOfUnits
                for record in outPutSpreadsheet:
                    if record[0]==stationId:
                        record[1]=(totalUnits)
        data['result']['result_list'][0][self.configuration_dict['output_id']]=outPutSpreadsheet
        return data

    # returns the next station that is a machine
    def getNextStation(self,data,bufferId):
        nodes=data['graph']['node']
        current=bufferId
        while 1:
            next=self.getSuccessors(data, current)[0]   
            if 'Machine' in nodes[next]['_class'] or 'M3' in nodes[next]['_class']:     
                return next
            current=next