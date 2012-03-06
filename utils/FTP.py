# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities . Included is the abilty to run code transparently in
### OpenNebula cloud environments. There are various software
### dependencies, but all are FOSS.
###
### This file may be used under the terms of the GNU General Public
### License version 2.0 as published by the Free Software Foundation
### and appearing in the file LICENSE.GPL included in the packaging of
### this file.  Please review the following to ensure GNU General Public
### Licensing requirements will be met:
### http://www.opensource.org/licenses/gpl-license.php
###
### If you are unsure which license is appropriate for your use (for
### instance, you are interested in developing a commercial derivative
### of VisTrails), please contact us at vistrails@sci.utah.edu.
###
### This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
### WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
###
#############################################################################
"""This module provides FTP functionality.
"""
# library
import ftplib
import os
import socket
# third-party
# vistrails
from core.modules.vistrails_module import Module, ModuleError
from core.modules import basic_modules
from core.modules.basic_modules import File, Path, String, Boolean
# eo4vistrails


class FTPReader(Module):
    """Reads a file from an FTP server.

    Input ports:
        server:
            the server on which the file is located
        directory:
            the full path to the file to be transferred (including end slash)
        filename:
            full name of the file to be transferred
        username:
            optional username to log on to the server
        password:
            optional password to log on to the server
        directory_out:
            optional full path to where the file is to be stored
            (including end slash)
        filename_out:
            optional full name of the file to be stored
            (default is the transfer filename but this is only used if the
            `directory_out` is specified)

    Output ports:
        transferred_file:
            a pointer to the file that has been transferred

    """

    _input_ports = [('server', '(edu.utah.sci.vistrails.basic:String)'),
                    ('directory', '(edu.utah.sci.vistrails.basic:String)'),
                    ('filename', '(edu.utah.sci.vistrails.basic:String)'),
                    ('username', '(edu.utah.sci.vistrails.basic:String)'),
                    ('password', '(edu.utah.sci.vistrails.basic:String)'),
                    ('directory_out', '(edu.utah.sci.vistrails.basic:String)'),
                    ('filename_out', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('transferred_file',
                      '(edu.utah.sci.vistrails.basic:File)')]

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        self.server = self.getInputFromPort('server')
        self.directory = self.getInputFromPort('directory')
        self.filename = self.getInputFromPort('filename')
        self.username = self.forceGetInputFromPort('username', '')
        self.password = self.forceGetInputFromPort('password', '')
        self.directory_out = self.forceGetInputFromPort('directory_out', '')
        self.filename_out = self.forceGetInputFromPort('filename', '')

        try:
            f = ftplib.FTP(self.server)
            #print 'FTP:93 Connected to host "%s"' % self.server
        except (socket.error, socket.gaierror), e:
            e = 'Cannot reach "%s"' % self.server
            raise ModuleError(self, e)

        if self.username and self.password:
            try:
                f.login(self.username, self.password)
                #print 'FTP:99 Logged in as "%s"' % self.username
            except ftplib.error_perm:
                e = 'Unable to login with given username and password'
                f.quit()
                raise ModuleError(self, e)
        else:
            try:
                f.login()
                #print 'FTP:109 Logged in as "anonymous"'
            except ftplib.error_perm:
                e = 'Cannot login anonymously'
                f.quit()
                raise ModuleError(self, e)

        try:
            f.cwd(self.directory)
            #print 'FTP:117 Changed to "%s" folder' % self.directory
        except ftplib.error_perm:
            e = 'Cannot change to directory "%s"' % self.directory
            f.quit()
            raise ModuleError(self, e)
        
        fileObj = None
        try:            
            # create output file
            try:
                if self.directory_out:
                    if not self.filename_out:
                        self.filename_out = self.filename
                    _file = self.directory_out + self.filename_out
                    fileObj = basic_modules.File()
                    fileObj.name = _file
                    f_out = open(_file, 'wb')
                    #print 'FTP:134', fileObj, fileObj.name
                else:
                    fileObj = self.interpreter.filePool.create_file()
                    self.filename_out = fileObj.name
                    f_out = open(self.filename_out, 'wb')
                    #print 'FTP:138', fileObj, fileObj.name
            except:
                e = 'Unable to create output file "%s"' % self.filename_out
                f_out.close()
                raise ModuleError(self, e)
            # read file from server
            f.retrbinary('RETR %s' % self.filename, f_out.write)
            f_out.close()
            f.quit()
            self.setResult('transferred_file', fileObj)
            #print 'FTP:148 Downloaded "%s" from current dir as "%s"' % \
            #        (self.filename, self.filename_out)
        except ftplib.error_perm:
            e = 'Cannot read file "%s"' % self.filename
            os.unlink(self.filename)
            f_out.close()
            f.quit()
            raise ModuleError(self, e)
