
# import os.path
from readWip import findFile
import os, sys

''' choose the file where we have the info related to the database we are about to connect to'''
# insert the path to the file containing the data of the connection, for info see bellow within getConnectionInfo method#
# XXXX update the arguments with the server data stored on your computer, ADDED FOR TESTING
filename=findFile('ServerData',os.path.dirname(os.path.abspath(sys.argv[0])), 'txt' )
# choose a delimiter for the file to be read
seperator='='


def getConnectionInfo():
    ''' open the file defined by the user (where the database info is stored) and read the info stored there
        the data must be stored in this form:
        driver='{<name of the driver>}' e.g. driver='{MySQL ODBC 3.5.1 Driver}',  find out in system tools
        server='<server address> e.g. driver='localhost' if the server is local
        port='<the port of the server>' e.g. port='3306' the default for MySQL server
        data_base='<the name of the database>' 
        user='<the name of the user>'
        pass_word='<user password>' 
    '''
    fileIN=open(filename,'r')
    line=fileIN.readline()
    while line:
        sout=line.split(seperator)
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