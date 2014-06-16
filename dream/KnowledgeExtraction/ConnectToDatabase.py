'''
Created on 16 Jun 2014

@author: Ioannis
'''
# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================

import os.path
import pyodbc
    # choose a delimiter for the file to be read
SEPERATOR='='
class ConnectionData(object):
    ''' open the file defined by the user (where the database info is stored) and read the info stored there
            the data must be stored in this form:
            driver='{<name of the driver>}' e.g. driver='{MySQL ODBC 3.5.1 Driver}',  find out in system tools
            server='<server address> e.g. driver='localhost' if the server is local
            port='<the port of the server>' e.g. port='3306' the default for MySQL server
            data_base='<the name of the database>' 
            user='<the name of the user>'
            pass_word='<user password>' 
        '''
    def __init__(self, seekName='ServerData', file_path='',implicitExt='txt', number_of_cursors=0):
        if file_path=='':
            file_path=raw_input('insert the path to the file containing the connection data:')
        self.number_of_cursors=number_of_cursors
        self.cursors=[]                             # list of cursors
        self.file_path=file_path
        print self.file_path
        self.file_name=seekName
        self.file_extension=implicitExt
        cnxnInfo=self.getConnectionInfo()
        self.cnxn=pyodbc.connect("Driver="+cnxnInfo[0]+";SERVER="+cnxnInfo[1]+"; PORT="+cnxnInfo[2]+\
                                 ";DATABASE="+cnxnInfo[3]+";UID="+cnxnInfo[4]+"; PASSWORD="+cnxnInfo[5]+";")
        
    def getConnection(self):
        return self.cnxn
        
    def getCursors(self):
        for j in range(self.number_of_cursors):
            self.cursors.append(self.cnxn.cursor())
        return self.cursors
        

    def getConnectionDataPath(self):
        """ Given a pathsep-delimited path string, find seekName. 
        Returns path to seekName if found, otherwise None.
        >>> findFile('ls', '/usr/bin:/bin', implicit='.exe')
        'bin/ls.exe'
        """
        for file in os.listdir(self.file_path):
            if file.endswith(os.extsep+self.file_extension) and file.startswith(self.file_name):
                full_path=os.path.join(self.file_path,file)
                if os.path.isfile(full_path):
                    return full_path
                return False
    
    def getConnectionInfo(self):
        fileIN=open(self.getConnectionDataPath(),'r')
        line=fileIN.readline()
        while line:
            sout=line.split(SEPERATOR)
            name=sout[0]
            if name=='driver':
                driver=sout[1].rstrip()
            elif name=='server':
                server=sout[1].rstrip()
            elif name=='port':
                port=sout[1].rstrip()
            elif name=='data_base':
                data_base=sout[1].rstrip()
            elif name=='user':
                user=sout[1].rstrip()
            elif name=='pass_word':
                pass_word=sout[1].rstrip()
            line=fileIN.readline()
        return driver, server, port, data_base, user, pass_word