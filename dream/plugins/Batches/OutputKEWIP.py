from dream.plugins import plugin

class OutputKEWIP(plugin.OutputPreparationPlugin):
    """ Output the station utilization metrics in a format compatible with 
    """

    def postprocess(self, data):
        if data['general'].get('wipSource',None)=='Manually':
            data['result']['result_list'][0][self.configuration_dict['output_id']]=[[
                                                                                     'WIP Was defined Manually. No KE tool Input!'
                                                                                   ]]
            return data
        outPutSpreadsheet=[['Station','# units awaiting processing','# units complete but not passed on']]
        nodes=data['graph']['node']
        
        for node_id, node in nodes.iteritems():       
            if 'Machine' in node['_class'] or 'M3' in node['_class']:        
                outPutSpreadsheet.append([node_id,0])
                
        for node_id, node in nodes.iteritems():       
            if 'Queue' in node['_class'] or 'Clearance' in node['_class']:
                wip=node.get('wip',[])
                stationId=self.getNextStation(data, node_id)
                print node_id,stationId
                totalUnits=0
                for element in wip:
                    numberOfUnits=element.get('numberOfUnits',0)
                    totalUnits+=numberOfUnits
                for record in outPutSpreadsheet:
                    print record
                    if record[0]==stationId:
                        print 'appending',totalUnits
                        record[1]=(totalUnits)
        data['result']['result_list'][0][self.configuration_dict['output_id']]=outPutSpreadsheet
        return data

    # returns the next station that is a machine
    def getNextStation(self,data,bufferId):
        nodes=data['graph']['node']
        current=bufferId
        # find all the successors that may share batches
        while 1:
            next=self.getSuccessors(data, current)[0]   
            if 'Machine' in nodes[next]['_class'] or 'M3' in nodes[next]['_class']:     
                return next
            current=next