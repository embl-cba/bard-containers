#!/usr/bin/env python3
#
# Software Name : abcdesktop.io
# Version: 0.2
# SPDX-FileCopyrightText: Copyright (c) 2020-2021 Orange
# SPDX-License-Identifier: GPL-2.0-only
#
# This software is distributed under the GNU General Public License v2.0 only
# see the "license.txt" file for more details.
#
# Author: abcdesktop.io team
# Software description: cloud native desktop service
#

import logging
from platform import node
from typing_extensions import assert_type
import oc.logging
from oc.od.apps import ODApps
import oc.od.error
import oc.od.settings
import oc.lib 
import oc.auth.namedlib
import os
import time
import datetime
import binascii
import urllib3


import yaml
import json
import chevron
import requests
import copy
import threading
import hashlib

from kubernetes import client, config, watch
from kubernetes.stream import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL
from kubernetes.client.rest import ApiException

from kubernetes.client.api.core_v1_api import CoreV1Api

from kubernetes.client.models.v1_pod import V1Pod
# from kubernetes.client.models.v1_pod_spec import V1PodSpec
from kubernetes.client.models.v1_pod_status import V1PodStatus
# from kubernetes.client.models.v1_container import V1Container
from kubernetes.client.models.v1_ephemeral_container import V1EphemeralContainer
from kubernetes.client.models.v1_status import V1Status
from kubernetes.client.models.v1_container import V1Container

# kubernetes.client.models.v1_container
from kubernetes.client.models.v1_container_status import V1ContainerStatus
from kubernetes.client.models.v1_container_state import V1ContainerState
from kubernetes.client.models.v1_container_state_terminated import V1ContainerStateTerminated
from kubernetes.client.models.v1_container_state_running import V1ContainerStateRunning
from kubernetes.client.models.v1_container_state_waiting import V1ContainerStateWaiting

# Volume
from kubernetes.client.models.v1_persistent_volume_claim import V1PersistentVolumeClaim
#from kubernetes.client.models.v1_volume import V1Volume
#from kubernetes.client.models.v1_volume_mount import V1VolumeMount
#from kubernetes.client.models.v1_local_volume_source import V1LocalVolumeSource
#from kubernetes.client.models.v1_flex_volume_source import V1FlexVolumeSource
#from kubernetes.client.models.v1_host_path_volume_source import V1HostPathVolumeSource
#from kubernetes.client.models.v1_secret_volume_source import V1SecretVolumeSource

# Secret
from kubernetes.client.models.v1_secret import V1Secret
#from kubernetes.client.models.v1_secret_list import V1SecretList
from kubernetes.client.models.v1_event_source import V1EventSource

from kubernetes.client.models.core_v1_event import CoreV1Event
from kubernetes.client.models.v1_node_list import V1NodeList
from kubernetes.client.models.v1_node import V1Node
from kubernetes.client.models.v1_env_var import V1EnvVar 
from kubernetes.client.models.v1_pod_list import V1PodList
#from kubernetes.client.models.v1_config_map import V1ConfigMap
#from kubernetes.client.models.v1_endpoint import V1Endpoint
from kubernetes.client.models.v1_endpoints import V1Endpoints
#from kubernetes.client.models.v1_endpoints_list import V1EndpointsList
from kubernetes.client.models.v1_endpoint_subset import V1EndpointSubset 
from kubernetes.client.models.core_v1_endpoint_port import CoreV1EndpointPort
from kubernetes.client.models.v1_endpoint_address import V1EndpointAddress
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from kubernetes.client.models.v1_resource_requirements import V1ResourceRequirements

from kubernetes.client.models.v1_delete_options import V1DeleteOptions


import oc.lib
import oc.od.acl
import oc.od.volume
import oc.od.persistentvolumeclaim
import oc.od.secret         # manage secret for kubernetes
import oc.od.configmap
import oc.od.appinstancestatus
from   oc.od.error          import ODAPIError, ODError   # import all error classes
from   oc.od.desktop        import ODDesktop
from   oc.auth.authservice  import AuthInfo, AuthUser # to read AuthInfo and AuthUser
from   oc.od.vnc_password   import ODVncPassword

logger = logging.getLogger(__name__)


DEFAULT_PULSE_TCP_PORT = 4713
DEFAULT_CUPS_TCP_PORT  = 631


def selectOrchestrator():
    """select Orchestrator
    return a kubernetes ODOrchestratorKubernetes

    Returns:
        [ODOrchestrator]: [description]
    """
    myOrchestrator = oc.od.orchestrator.ODOrchestratorKubernetes()
    return myOrchestrator

@oc.logging.with_logger()
class ODOrchestratorBase(object):

    def on_desktoplaunchprogress(self, key, *args):
        if callable(self.desktoplaunchprogress): 
            self.desktoplaunchprogress(self, key, *args)

    def __init__(self):

        # container name is x-UUID
        self.graphicalcontainernameprefix   = 'x'   # graphical container letter prefix x for x11
         # container name is a-UUID
        self.spawnercontainernameprefix     = 'a'   # graphical container letter prefix a for spwaner
        # printer name is c-UUID
        self.printercontainernameprefix     = 'c'   # printer container letter prefix c for cups
        # sound name is s-UUID
        self.soundcontainernameprefix       = 's'   # sound container letter prefix p for pulseaudio
        # sound name is p-UUID
        self.filercontainernameprefix       = 'f'   # file container letter prefix f for file service
        # init name is i-UUID
        self.initcontainernameprefix        = 'i'   # init container letter prefix i for init
        # storage name is o-UUID
        self.storagecontainernameprefix     = 'o'   # storage container letter prefix o for secret storage
        # ssh name is h-UUID
        self.sshcontainernameprefix         = 'h'   # ssh container letter prefix h for ssh
        # webshell name is w-UUID
        self.webshellcontainernameprefix    = 'w'   # webshell container letter prefix w
        # name separtor only for human read 
        self.rdpcontainernameprefix         = 'r'   # rdp container letter prefix r for xrdp
        # 
        self.x11overlaycontainernameprefix  = 'v'   # x11 overlay container letter prefix v for overlay
        # name separtor only for human read 
        self.containernameseparator         = '-'   # separator

        self.nameprefixdict = { 'graphical' : self.graphicalcontainernameprefix,
                                'spawner'   : self.spawnercontainernameprefix,
                                'webshell'  : self.webshellcontainernameprefix,
                                'printer'   : self.printercontainernameprefix,
                                'sound'     : self.soundcontainernameprefix,  
                                'filer'     : self.filercontainernameprefix,
                                'init'      : self.initcontainernameprefix,
                                'storage'   : self.storagecontainernameprefix,
                                'ssh'       : self.sshcontainernameprefix,
                                'rdp'       : self.rdpcontainernameprefix,
                                'x11overlay' : self.x11overlaycontainernameprefix
        }
        self.name                   = 'base'
        self.desktoplaunchprogress  = oc.pyutils.Event()        
        self.x11servertype          = 'x11server'        
        self.pod_application        = 'pod_application'
        self.pod_application_pull   = 'pod_application_pull'
        self.endpoint_domain        = 'desktop'
        self.ephemeral_container    = 'ephemeral_container'
        self.abcdesktop_role_desktop = 'desktop'

    def get_containername( self, authinfo, userinfo, currentcontainertype, myuuid ):
        prefix = self.nameprefixdict[currentcontainertype]
        name = prefix + self.containernameseparator + authinfo.provider + self.containernameseparator + userinfo.userid
        name = oc.auth.namedlib.normalize_name_dnsname( name )
        # return self.get_basecontainername( prefix, userid, myuuid )
        return name

    # def get_basecontainername( self, containernameprefix, userid, container_name ):
    #    user_container_name = self.containernameseparator
    #    if isinstance( userid, str ):
    #        user_container_name = userid + self.containernameseparator
    #    name = containernameprefix + self.containernameseparator + user_container_name + container_name
    #    name = oc.auth.namedlib.normalize_name_dnsname( name )
    #    return name

    def get_normalized_username(self, name ):
        """[get_normalized_username]
            return a username without accent to be use in label and container name
        Args:
            name ([str]): [username string]

        Returns:
            [str]: [username correct value]
        """
        return oc.lib.remove_accents( name ) 
   
    def resumedesktop(self, authinfo, userinfo, **kwargs):
        raise NotImplementedError('%s.resumedesktop' % type(self))

    def createdesktop(self, authinfo, userinfo, **kwargs):
        raise NotImplementedError('%s.createdesktop' % type(self))

    def build_volumes( self, authinfo, userinfo, volume_type, secrets_requirement, rules, **kwargs):
        raise NotImplementedError('%s.build_volumes' % type(self))

    def findDesktopByUser( self, authinfo, userinfo ):
        raise NotImplementedError('%s.findDesktopByUser' % type(self))

    def removedesktop(self, authinfo, userinfo, args={}):
        raise NotImplementedError('%s.removedesktop' % type(self))

    def get_auth_env_dict( self, authinfo, userinfo ):
        raise NotImplementedError('%s.get_auth_env_dict' % type(self))

    def getsecretuserinfo(self, authinfo, userinfo):
        raise NotImplementedError('%s.getsecretuserinfo' % type(self))

    def garbagecollector( self, timeout ):
        raise NotImplementedError(f"{type(self)}.garbagecollector")

    def execwaitincontainer( self, desktop, command, timeout):
        raise NotImplementedError(f"{type(self)}.execwaitincontainer")

    def is_configured( self):
        raise NotImplementedError(f"{type(self)}.is_configured")

    def countdesktop(self):
        raise NotImplementedError(f"{type(self)}.countdesktop")

    def listContainerApps( self, authinfo, userinfo, apps ):
        raise NotImplementedError('%s.listContainerApps' % type(self))

    def countRunningContainerforUser( self, authinfo, userinfo):  
        raise NotImplementedError('%s.countRunningContainerforUser' % type(self))

    def envContainerApp( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str):
        raise NotImplementedError('%s.envContainerApp' % type(self))
    
    def removeContainerApp( self, authinfo, userinfo, containerid):
        raise NotImplementedError('%s.removeContainerApp' % type(self))

    def logContainerApp( self, authinfo, userinfo, podname, containerid):
        raise NotImplementedError('%s.logContainerApp' % type(self))

    def stopContainerApp( self, authinfo, userinfo, myDesktop, podname, containerid, timeout=5 ):
        raise NotImplementedError('%s.stopContainerApp' % type(self))

    def get_volumename(self, prefix, userinfo):
        if not isinstance(prefix,str):
             raise ValueError('invalid prefix value %s' % type(prefix))

        if not isinstance(userinfo, oc.auth.authservice.AuthUser):
             raise ValueError('invalid userinfo value %s' % type(userinfo))

        name = prefix + '-' + userinfo.get('userid')
        normalize_name = oc.auth.namedlib.normalize_name( name )
        return normalize_name

    def user_connect_count(self, desktop:ODDesktop, timeout=10):
        """user_connect_count
            call bash script /composer/connectcount.sh inside a desktop
        Args:
            desktop (ODDesktop): ODDesktop
            timeout (int, optional): in seconds. Defaults to 10.

        Raises:
            ValueError: ValueError('invalid desktop object type') if desktop id not an ODDesktop

        Returns:
            int: number of user connected on a desktop
                -1 if error
                else number of connection to the x11 websocket 
        """
        self.logger.debug('')
        nReturn = -1 # default value is a error
        if not isinstance(desktop,ODDesktop):
            raise ValueError('invalid desktop object type')

        # call bash script in oc.user 
        # bash script 
        # !/bin/bash
        # COUNT=$(netstat -t | grep 'ESTABLISHED' | grep 6081 | wc -l)
        # echo $COUNT
        command = [ '/composer/connectcount.sh' ]      
        result = self.execwaitincontainer( desktop, command, timeout)
        if not isinstance(result,dict):
            # do not raise exception 
            return nReturn

        self.logger.info( f"command={command} returns exitcode={result.get('ExitCode')} output={result.get('stdout')}" )
        if result.get('ExitCode') == 0 and result.get('stdout'):
            try:
                nReturn = int(result.get('stdout'))
            except ApiException as e:
                self.logger.error(e)
        return nReturn

    def list_dict_secret_data( self, authinfo, userinfo, access_type=None, hidden_empty=False ):
        """get a dict of secret (key value) for the access_type
           if access_type is None will list all user secrets
        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 
            access_type (str): type of secret like 'auth' 

        Returns:
            dict: return dict of secret key value 
        """
        return {}

    def waitForDesktopProcessReady(self, desktop, callback_notify):
        self.logger.debug('')

        nCountMax = 42
        # check if supervisor has stated all processs
        nCount = 1
        bListen = { 'graphical': False, 'spawner': False }
        # loop
        # wait for a listen dict { 'x11server': True, 'spawner': True }

        while nCount < nCountMax:

            for service in ['graphical', 'spawner']: 
                self.logger.debug( f"desktop services status bListen {bListen}" ) 
                # check if WebSockifyListening id listening on tcp port 6081
                if bListen[service] is False:
                    messageinfo = f"c.Waiting for desktop {service} service {nCount}/{nCountMax}"
                    callback_notify(messageinfo)
                    bListen[service] = self.waitForServiceListening( desktop, service=service)
                    if bListen[service] is False:
                        messageinfo = f"c.Desktop {service} service is not ready."
                        time.sleep(1)
            nCount += 1
            
            if bListen['graphical'] is True and bListen['spawner'] is True:     
                self.logger.debug( "desktop services are ready" )                  
                callback_notify( f"c.Desktop services are running after {nCount} s" )              
                return True
        
        # Can not chack process status     
        self.logger.warning( f"waitForDesktopProcessReady not ready services status:{bListen}" )
        return False


    def waitForServiceHealtz(self, desktop, service, timeout=5):
        """waitForServiceHealtz

        Args:
            desktop (ODDesktop): desktop object to waitForServiceHealtz
            service (str): namwe of the service 
            timeout (int, optional): timeout in seconds. Defaults to 1.

        Raises:
            ValueError: invalid desktop object type, desktop is not a ODDesktop
            ODAPIError: error in configuration file 'healtzbin' must be a string
            ODAPIError: error in configuration file 'tcpport' must be a int

        Returns:
            bool: True the the service healtz is up, else False
        """
        self.logger.debug('')
        # Note the same timeout value is used twice
        # for the wait_port command and for the exec command         
        
        assert_type( desktop, ODDesktop)

        # healtz binary command is optional 
        # return True if not define
        if not isinstance( oc.od.settings.desktop_pod[service].get('healtzbin'), str):
            # no healtz binary command has been set
            # no need to run command
            return True
        
        port = port=oc.od.settings.desktop_pod[service].get('tcpport')
        binding = f"http://{desktop.ipAddr}:{port}/{service}/healtz"

        # curl --max-time [SECONDS] [URL]
        healtzbintimeout = oc.od.settings.desktop_pod[service].get('healtzbintimeout', timeout*1000 )
        command = [ oc.od.settings.desktop_pod[service].get('healtzbin'), '--max-time', str(healtzbintimeout), binding ]       
        result = self.execwaitincontainer( desktop, command, timeout)
        self.logger.debug( 'command %s , return %s output %s', command, str(result.get('exit_code')), result.get('stdout') )

        if isinstance(result, dict):
            return result.get('ExitCode') == 0
        else:
            return False

      
    def waitForServiceListening(self, desktop:ODDesktop, service:str, timeout:int=2)-> bool:
        """waitForServiceListening

        Args:
            desktop (ODDesktop): desktop object to waitForServiceListening
            service (str): name of the service to check, should be 'graphical' or 'spawner'
            timeout (int, optional): timeout in seconds. Defaults to 2.

        Raises:
            ValueError: invalid desktop object type, desktop is not a ODDesktop
            ODAPIError: error in configuration file 'waitportbin' must be a string
            ODAPIError: error in configuration file 'tcpport' must be a int

        Returns:
            bool: True the the service is up
        """

        self.logger.debug(locals())       
        assert_type( desktop, ODDesktop)

        # Note the same timeout value is used twice
        # for the wait_port command and for the exec command  

        waitportbincommand = oc.od.settings.desktop_pod[service].get('waitportbin')
        # check if waitportbincommand is a string
        if not isinstance( waitportbincommand, str):
            # no waitportbin command has been set
            self.logger.error(f"error in configuration file 'waitportbin' must be a string. Type read in config {type(waitportbincommand)}" )
            raise ODAPIError( f"error in configuration file 'waitportbin' must be a string defined as healtz command line. type defined {type(waitportbincommand)}" )
        
        port = oc.od.settings.desktop_pod[service].get('tcpport')
        if not isinstance( port, int):
            # no tcpport has been set
            self.logger.error(f"error in configuration file 'tcpport' must be a int. Type read in config {type(port)}" )
            raise ODAPIError( f"error in configuration file 'tcpport' must be a int. Type read in config {type(port)}" )
        
        binding = f"{desktop.ipAddr}:{port}"
        # 
        # waitportbin use a timeout (in milliseconds).
        # execwaitincontainer use a timeout (in seconds).
        # 
        waitportbintimeout = oc.od.settings.desktop_pod[service].get('waitportbintimeout', timeout*1000 )
        command = [ oc.od.settings.desktop_pod[service].get('waitportbin'), '-t', str(waitportbintimeout), binding ]       
        result = self.execwaitincontainer( desktop, command, timeout)
     
        if isinstance(result, dict):
            self.logger.debug( f"command={command} exit_code={result.get('ExitCode')} stdout={result.get('stdout')}" )
            isportready = result.get('ExitCode') == 0
            self.logger.debug( f"isportready={isportready}")
            if isportready is True:
                self.logger.debug( f"binding {binding} is up")
                return self.waitForServiceHealtz(desktop, service, timeout)

        self.logger.info( f"binding {binding} is down")
        return False

    @staticmethod
    def generate_cookie( cookie_len:int):
        assert_type( cookie_len, int )
        key = binascii.b2a_hex(os.urandom(cookie_len))
        return key.decode( 'utf-8' )

    @staticmethod
    def generate_xauthkey():
        """generate_xauthkey
            create a xauth cookie
        Returns:
            str: xauth cookie
        """
        # generate key, xauth requires 128 bit hex encoding
        # xauth add ${HOST}:0 . $(xxd -l 16 -p /dev/urandom)
        return ODOrchestratorBase.generate_cookie(cookie_len=15)

    @staticmethod
    def generate_pulseaudiocookie():
        """generate_pulseaudiocookie
            create a pulse audio cookie of 32 Bytes
        Returns:
            str: pulseaudiocookie
        """
        # generate key, PULSEAUDIO requires PA_NATIVE_COOKIE_LENGTH 256 Bytes
        # but kubernetes labels must be no more than 63 characters
        # len( binascii.b2a_hex(os.urandom(16)).decode( 'utf-8' )) = 32 < 64
        # use this fix in entrypoint
        # for i in {1..8} 
        # do 
        #   echo "$PULSEAUDIO_COOKIE" >> cookie 
        # done
        return ODOrchestratorBase.generate_cookie(cookie_len=16)

    @staticmethod
    def generate_broadcastcookie():
        """generate_broadcastcookie
             create a pulse broadcast cookie

        Returns:
            str: broadcastcookie value
        """
        # generate key, SPAWNER and BROADCAT service
        # use os.urandom(24) as key 
        return ODOrchestratorBase.generate_cookie(cookie_len=24)

@oc.logging.with_logger()
class ODOrchestrator(ODOrchestratorBase):
    
    def __init__(self ):
        super().__init__()
        self.name = 'docker'
        
    def prepareressources(self, authinfo:AuthInfo, userinfo:AuthUser):
        self.logger.info('externals ressources are not supported in docker mode')  

    def getsecretuserinfo(self, authinfo:AuthInfo, userinfo:AuthUser):  
        ''' cached userinfo are not supported in docker mode '''    
        ''' return an empty dict '''
        self.logger.info('get cached userinfo are not supported in docker mode')
        return {} 

    def build_volumes( self, authinfo:AuthInfo, userinfo:AuthUser, volume_type, secrets_requirement, rules, **kwargs):
        raise NotImplementedError('%s.build_volumes' % type(self))
  
    def countdesktop(self):
        raise NotImplementedError('%s.countdesktop' % type(self))

    def removedesktop(self, authinfo, userinfo, args={}):
        raise NotImplementedError('%s.removedesktop' % type(self))

    def is_instance_app( self, appinstance ):
        raise NotImplementedError('%s.is_instance_app' % type(self))

    def execwaitincontainer( self, desktop, command, timeout=1000):
        raise NotImplementedError('%s.removedesktop' % type(self))

    def execininstance( self, container_id, command):
        raise NotImplementedError('%s.execininstance' % type(self))

    def getappinstance( self, authinfo, userinfo, app ):        
        raise NotImplementedError('%s.getappinstance' % type(self))

    def get_auth_env_dict( self, authinfo, userinfo  ):
        return {}

    @staticmethod
    def applyappinstancerules_homedir( authinfo, rules ):
        homedir_enabled = False      # by default application do not share the user homedir

        # Check if there is a specify rules to start this application
        if type(rules) is dict  :
            # Check if there is a homedir rule
            rule_homedir =  rules.get('homedir')
            if type(rule_homedir) is dict:

                # read the default rule first and them apply specific rules
                homedir_enabled = rule_homedir.get('default', False )
                
                # list user context tag 
                # check if user auth tag context exist
                for kn in rule_homedir.keys():
                    ka = None
                    for ka in authinfo.get_labels() :
                        if kn == ka :
                            if type(rule_homedir.get(kn)) is bool:
                                homedir_enabled = rule_homedir.get(kn)
                            break
                    if kn == ka :   # double break 
                        break

        return homedir_enabled

    @staticmethod
    def applyappinstancerules_network( authinfo, rules ):
        """[applyappinstancerules_network]
            return a dict network_config

        Args:
            authinfo ([type]): [description]
            rules ([type]): [description]

        Returns:
            [dict ]: [network config]
            network_config = {  'network_disabled' : network_disabled, 
                                'name': name, 
                                'dns': dns
                                'webhook' : webhook}
        """
        # set default context value 
        network_config = {  'network_disabled' :    False, 
                            'annotations':          None,
                            'name':                 None, 
                            'external_dns':         None,
                            'internal_dns':         None,
                            'webhook' :             None,
                            'websocketrouting' :    oc.od.settings.websocketrouting,
                            'websocketrouting_interface' :  None }
      

        # Check if there is a specify rules to start this application
        if type(rules) is dict  :
            # Check if there is a network rule
            rule_network =  rules.get('network')
            if type(rule_network) is dict:
                # read the default context first 
                rule_network_default = rule_network.get('default', True)
                if rule_network_default is False:
                    network_config[ 'network_disabled' ] = True
              
                if type(rule_network_default) is dict:
                    network_config.update( rule_network_default )
                
                # list user context tag 
                # check if user auth tag context exist
                for kn in rule_network.keys():
                    ka = None
                    for ka in authinfo.get_labels():
                        if kn == ka :
                            network_config.update ( rule_network.get(kn) )
                            break
                    if kn == ka :
                        break

        return network_config
    

    def createappinstance(self, myDesktop, app, authinfo, userinfo={}, userargs=None, **kwargs ):                    
        raise NotImplementedError('%s.createappinstance' % type(self))

    def buildwebhookinstance( self, authinfo, userinfo, app, network_config, network_name=None, appinstance_id=None ):

        webhook = None

        # if context_network_webhook call request to webhook and replace all datas
        context_network_webhook = network_config.get('webhook')
        if isinstance( context_network_webhook, dict) : 
            webhook = {}
            # if create exist 
            webhookstartcmd = context_network_webhook.get('create')
            if isinstance( webhookstartcmd, str) :
                # build the webhook url 
                # fillwebhook return None if nothing to do
                webhookcmd = self.fillwebhook(  mustachecmd=webhookstartcmd, 
                                                app=app, 
                                                authinfo=authinfo, 
                                                userinfo=userinfo, 
                                                network_name=network_name, 
                                                containerid=appinstance_id )
                webhook['create'] = webhookcmd

            # if destroy exist 
            webhookstopcmd = context_network_webhook.get('destroy')
            if isinstance( webhookstopcmd, str) :
                # fillwebhook return None if nothing to do
                webhookcmd = self.fillwebhook(  mustachecmd=webhookstopcmd, 
                                                app=app, 
                                                authinfo=authinfo, 
                                                userinfo=userinfo, 
                                                network_name=network_name, 
                                                containerid=appinstance_id )
                webhook['destroy'] = webhookcmd
        return webhook

    def fillwebhook(self, mustachecmd, app, authinfo, userinfo, network_name, containerid ):
        if not isinstance(mustachecmd, str) :
            return None
        sourcedict = {}
        # merge all dict data from app, authinfo, userinfo, and containerip
        # if add is a ODDekstop use to_dict to convert ODDesktop to dict 
        # else app is a dict 
        
        self.logger.debug( f"type(app) is {type(app)}" )

        if isinstance( app, dict ) :
            sourcedict.update( app )
        elif isinstance(app, ODDesktop ):
            sourcedict.update( app.to_dict().copy() )
            # desktop_interface is a dict 
            # { 
            #   'eth0': {'mac': '56:c7:eb:dc:c0:b8', 'ips': '10.244.0.239'      }, 
            #   'net1': {'mac': '2a:94:43:e0:f4:46', 'ips': '192.168.9.137'     }, 
            #   'net2': {'mac': '1e:50:5f:b7:85:f6', 'ips': '161.105.208.143'   }
            # }
            self.logger.debug( f"type(desktop_interfaces) is {type(app.desktop_interfaces)}" )
            if isinstance(app.desktop_interfaces, dict ):
                self.logger.debug( f"desktop_interfaces is {app.desktop_interfaces}" )
                for interface in app.desktop_interfaces.keys():
                    self.logger.debug( f"{interface} is {app.desktop_interfaces.get(interface)}" )
                    ipAddr = app.desktop_interfaces.get(interface).get('ips')
                    self.logger.debug( f"{interface} has ip addr {ipAddr}" )
                    sourcedict.update( { interface: ipAddr } )

        # Complete with user data
        sourcedict.update( authinfo.todict() )
        sourcedict.update( userinfo )

        # merge all dict data from desktopwebhookdict, app, authinfo, userinfo, and containerip
        moustachedata = {}
        for k in sourcedict.keys():
            if isinstance(sourcedict[k], str):
                if oc.od.settings.desktop['webhookencodeparams'] is True:
                    moustachedata[k] = requests.utils.quote(sourcedict[k])
                else: 
                    moustachedata[k] = sourcedict[k]

        moustachedata.update( oc.od.settings.desktop['webhookdict'] )
        self.logger.debug( f"moustachedata={moustachedata}" )
        webhookcmd = chevron.render( mustachecmd, moustachedata )
        return webhookcmd

    def logs( self, authinfo, userinfo ):
        raise NotImplementedError('%s.logs' % type(self))

    def isgarbagable( self, container, expirein, force=False ):
        raise NotImplementedError('%s.isgarbagable' % type(self))

    def garbagecollector( self, expirein, force=False ):
        raise NotImplementedError('%s.garbagecollector' % type(self))

@oc.logging.with_logger()
class ODOrchestratorKubernetes(ODOrchestrator):

    def __init__(self):
        super().__init__()

        # define two king of application:
        # - ephemeral container
        # - pod
        self.appinstance_classes = {    
            'ephemeral_container': ODAppInstanceKubernetesEphemeralContainer,
            'pod_application': ODAppInstanceKubernetesPod 
        }
        self.all_phases_status = [ 'Running', 'Terminated', 'Waiting', 'Completed', 'Succeeded']
        self.all_running_phases_status = [ 'Running', 'Waiting' ]

        # self.appinstance_classes = appinstance_classes_dict.
        # Configs can be set in Configuration class directly or using helper
        # utility. If no argument provided, the config will be loaded from
        # default location.
    
        #check if we are inside a cluster or not
        # https://kubernetes.io/docs/concepts/services-networking/connect-applications-service/#environment-variables
        # Example
        #   KUBERNETES_SERVICE_HOST=10.0.0.1
        #   KUBERNETES_SERVICE_PORT=443
        #   KUBERNETES_SERVICE_PORT_HTTPS=443
        #
        # if os.getenv('KUBERNETES_SERVICE_HOST') and os.getenv('KUBERNETES_SERVICE_PORT') :
        #     # self.logger.debug( 'env has detected $KUBERNETES_SERVICE_HOST and $KUBERNETES_SERVICE_PORT' )
        #    # self.logger.debug( 'config.load_incluster_config start')
        #    config.load_incluster_config() # set up the client from within a k8s pod
        #    # self.logger.debug( 'config.load_incluster_config kubernetes mode done')
        #else:
        #    # self.logger.debug( 'config.load_kube_config not in cluster mode')
        #    config.load_kube_config()
        #    # self.logger.debug( 'config.load_kube_config done')
        
        try:   
            # self.logger.debug( f"KUBERNETES_SERVICE_HOST={os.getenv('KUBERNETES_SERVICE_HOST')}" )
            # self.logger.debug( f"KUBERNETES_SERVICE_PORT={os.getenv('KUBERNETES_SERVICE_PORT')}" ) 
            # self.logger.debug( f"KUBERNETES_SERVICE_PORT_HTTPS={os.getenv('KUBERNETES_SERVICE_PORT_HTTPS')}" )
            config.load_incluster_config() # set up the client from within a k8s pod
            self.logger.info( "load_incluster_config done" )
        except Exception as e_in:
            # self.logger.debug( f"ODOrchestratorKubernetes load_kube_config" )
            # use KUBE_CONFIG_DEFAULT_LOCATION = os.environ.get('KUBECONFIG', '~/.kube/config')
            self.logger.debug( "ODOrchestratorKubernetes load_kube_config" )
            try:
                config.load_kube_config()
                self.logger.info( f"load_kube_config done" )
            except Exception as e_out:
                self.logger.error( f"This is a fatal error" )
                self.logger.error( f"load_incluster_config failed {e_in}" )
                self.logger.error( f"load_kube_config failed {e_out}" )

        # 
        # previous line is 
        #   from kubernetes.client import configuration 
        #   SSL hostname verification failure with websocket-client #138
        #   https://github.com/kubernetes-client/python/issues/138#
        # 
        #   you're using minikube for development purpose. It is not able to recognise your hostname. 
        #   https://stackoverflow.com/questions/54050504/running-connect-get-namespaced-pod-exec-using-kubernetes-client-corev1api-give
        #
        client.configuration.assert_hostname = False
        self.kubeapi = client.CoreV1Api()
        self.namespace = oc.od.settings.namespace
        self.bConfigure = True
        self.name = 'kubernetes'

        # defined remapped tmp volume
        # if app is a pod use a specifed path in /var/abcdesktop/pods
        # if app id a docker container use an empty
        # if oc.od.settings.desktopusepodasapp :
        # volume_tmp =      { 'name': 'tmp', 'emptyDir': { 'sizeLimit': '8Gi' } }
        # volume_tmp_path = { 'name': 'tmp', 'mountPath': '/tmp', 'subPathExpr': '$(POD_NAME)' }
        # volumemount_tmp =  {'mountPath': '/tmp',       'name': 'tmp'} ]
        # volumemount_tmp_path = {'mountPath': '/tmp',       'name': 'tmp', 'subPathExpr': '$(POD_NAME)'}
        # self.volume
        # no pods

        self.default_volumes = {}
        self.default_volumes_mount  = {}
        
        #
        # POSIX shared memory requires that a tmpfs be mounted at /dev/shm. 
        # The containers in a pod do not share their mount namespaces so we use volumes 
        # to provide the same /dev/shm into each container in a pod. 
        # read https://docs.openshift.com/container-platform/3.6/dev_guide/shared_memory.html
        # Here is the information of a pod on the cluster, we can see that the size of /dev/shm is 64MB, and when writing data to the shared memory via dd, it will throw an exception when it reaches 64MB: “No space left on device”.
        #
        # $ dd if=/dev/zero of=/dev/shm/test
        # dd: writing to '/dev/shm/test': No space left on device
        # 131073+0 records in
        # 131072+0 records out
        # 67108864 bytes (67 MB, 64 MiB) copied, 0.386939 s, 173 MB/s

        # 
        shareProcessMemorySize = oc.od.settings.desktop_pod.get('spec',{}).get('shareProcessMemorySize', oc.od.settings.DEFAULT_SHM_SIZE)
        self.default_volumes['shm']       = { 'name': 'shm', 'emptyDir': {  'medium': 'Memory', 'sizeLimit': shareProcessMemorySize } }
        self.default_volumes_mount['shm'] = { 'name': 'shm', 'mountPath' : '/dev/shm' }

        self.default_volumes['tmp']       = { 'name': 'tmp',  'emptyDir': { 'medium': 'Memory', 'sizeLimit': '8Gi' } }
        self.default_volumes_mount['tmp'] = { 'name': 'tmp',  'mountPath': '/tmp' }

        self.default_volumes['run']       = { 'name': 'run',  'emptyDir': { 'medium': 'Memory', 'sizeLimit': '1M' } }
        self.default_volumes_mount['run'] = { 'name': 'run',  'mountPath': '/var/run/desktop' }

        self.default_volumes['log']       = { 'name': 'log',  'emptyDir': { 'medium': 'Memory', 'sizeLimit': '8M' } }
        self.default_volumes_mount['log'] = { 'name': 'log',  'mountPath': '/var/log/desktop' }

        self.default_volumes['rundbus']       = { 'name': 'rundbus',  'emptyDir': { 'medium': 'Memory', 'sizeLimit': '8M' } }
        self.default_volumes_mount['rundbus'] = { 'name': 'rundbus',  'mountPath': '/var/run/dbus' }

        self.default_volumes['runuser']       = { 'name': 'runuser',  'emptyDir': { 'medium': 'Memory', 'sizeLimit': '8M' } }
        self.default_volumes_mount['runuser'] = { 'name': 'runuser',  'mountPath': '/run/user/' }

        self.default_volumes['x11socket'] = { 'name': 'x11socket',  'emptyDir': { 'medium': 'Memory' } }
        self.default_volumes_mount['x11socket'] = { 'name': 'x11socket',  'mountPath': '/tmp/.X11-unix' }

        self.default_volumes['pulseaudiosocket'] = { 'name': 'pulseaudiosocket',  'emptyDir': { 'medium': 'Memory' } }
        self.default_volumes_mount['pulseaudiosocket'] = { 'name': 'pulseaudiosocket',  'mountPath': '/tmp/.pulseaudio' }

        self.default_volumes['cupsdsocket'] = { 'name': 'cupsdsocket',  'emptyDir': { 'medium': 'Memory' } }
        self.default_volumes_mount['cupsdsocket'] = { 'name': 'cupsdsocket',  'mountPath': '/tmp/.cupsd' }

        # self.logger.debug( f"ODOrchestratorKubernetes done configure={self.bConfigure}" )


    def close(self):
        #self.kupeapi.close()
        pass

    def is_configured(self)->bool: 
        """[is_configured]
            return True if kubernetes is configured 
            call list_node() API  
        Returns:
            [bool]: [True if kubernetes is configured, else False]
        """
        return self.bConfigure
        
    def is_list_node_enabled(self)->bool: 
        """[is_list_node_enabled]
            return True if kubernetes is configured and can call list_node() API  
        Returns:
            [bool]: [True if kubernetes is configured, else False]
        """
        bReturn = False
        try:
            if self.bConfigure :
                # run a dummy node list to check if kube is working
                node_list = self.kubeapi.list_node()
                if isinstance( node_list, V1NodeList) and len(node_list.items) > 0:
                    bReturn = True
        except Exception as e:
            self.logger.error( str(e) )
        return bReturn


    def listEndpointAddresses( self, endpoint_name:str )->tuple:
        """listEndpointAddresses

        Args:
            endpoint_name (str): name of the endpoint

        Returns:
            tuple: (int, [ str ]) (port, list of address)
            port: can be None or int
            list of address: can be None or list of str 
        """
        list_endpoint_addresses = None
        list_endpoint_port = None
        endpoint = self.kubeapi.read_namespaced_endpoints( name=endpoint_name, namespace=self.namespace )
        if isinstance( endpoint, V1Endpoints ):
            if not isinstance( endpoint.subsets, list) or len(endpoint.subsets) == 0:
                return (list_endpoint_port, list_endpoint_addresses) # (None, None)

            endpoint_subset = endpoint.subsets[0]
            if isinstance( endpoint_subset, V1EndpointSubset ) :
                list_endpoint_addresses = []
                # read the uniqu port number
                # pyos listen on only one tcp port
                endpoint_port = endpoint_subset.ports[0]
                if isinstance( endpoint_port, CoreV1EndpointPort ):
                    list_endpoint_port = endpoint_port.port

                # read add addreses
                if not isinstance( endpoint_subset.addresses , list ):
                    self.logger.error('read_namespaced_endpoints no entry addresses found')
                else:
                    for address in endpoint_subset.addresses :
                        if isinstance( address, V1EndpointAddress):
                            list_endpoint_addresses.append( address.ip )

        return (list_endpoint_port, list_endpoint_addresses)

    def get_podname( self, authinfo:AuthInfo, userinfo:AuthUser, pod_sufix:str )->str:
        """[get_podname]
            return a pod name from authinfo, userinfo and uuid 
        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 
            pod_sufix ([str]): [uniqu sufix]

        Returns:
            [str]: [name of the user pod]
        """
        userid = userinfo.userid
        if authinfo.provider == 'anonymous':
            userid = 'anonymous'
        return oc.auth.namedlib.normalize_name_dnsname( userid + self.containernameseparator + pod_sufix)[0:252]       
 
    def get_labelvalue( self, label_value:str)->str:
        """[get_labelvalue]

        Args:
            label_value ([str]): [label_value name]

        Returns:
            [str]: [return normalized label name]
        """
        assert isinstance(label_value, str),  f"label_value has invalid type {type(label_value)}"
        normalize_data = oc.auth.namedlib.normalize_label( label_value )
        no_accent_normalize_data = oc.lib.remove_accents( normalize_data )
        return no_accent_normalize_data

    def logs( self, authinfo:AuthInfo, userinfo:AuthUser )->str:
        """logs

        Args:
            authinfo (AuthInfo): AuthInfo
            userinfo (AuthUser): AuthUser

        Returns:
            str: str log content
            return '' empty str by default ( if not found of error ) 
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"

        strlogs = ''
        myPod = self.findPodByUser(authinfo, userinfo)
        if isinstance(myPod, V1Pod):
            try:
                myDesktop = self.pod2desktop( pod=myPod )
                pod_name = myPod.metadata.name  
                container_name = myDesktop.container_name
                strlogs = self.kubeapi.read_namespaced_pod_log( name=pod_name, namespace=self.namespace, container=container_name, pretty='true' )
            except ApiException as e:
                self.logger.error( str(e) )
        else:
            self.logger.info( f"No pod found for user {userinfo.userid}" )
        return strlogs

    def build_volumes_secrets( self, authinfo:AuthInfo, userinfo:AuthUser, volume_type:str, secrets_requirement:list, rules={}, **kwargs:dict)->dict:
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"

        volumes = {}        # set empty dict of V1Volume dict by default
        volumes_mount = {}  # set empty dict of V1VolumeMount by default
        #
        # mount secret in /var/secrets/abcdesktop
        # abcdesktop is the default namespace
        # mount secret in /var/secrets/$NAMESPACE
        #
        self.logger.debug( f"secrets_requirement is {secrets_requirement}" ) 
        if not isinstance( secrets_requirement, list ):
            self.logger.debug( f"skipping secrets_requirement type={type(secrets_requirement)}, no secret to mount" ) 
        else:
            self.logger.debug( "listing list_dict_secret_data access_type='auth'" )
            mysecretdict = self.list_dict_secret_data( authinfo, userinfo, access_type='auth' )
            if isinstance( mysecretdict, dict):
                # read all entries in dict
                # {'auth-ntlm-fry': {'type': 'abcdesktop/ntlm', 'data': {...}}}
                self.logger.debug(f"list of secret is {mysecretdict.keys()}")
                for secret_auth_name in mysecretdict.keys():
                    # https://kubernetes.io/docs/concepts/configuration/secret
                    # create an entry eq: 
                    #
                    # /var/secrets/abcdesktop/ntlm
                    # /var/secrets/abcdesktop/kerberos
                    #  
                    self.logger.debug(f"checking {secret_auth_name} access_type='auth'")

                    if not isinstance(mysecretdict[secret_auth_name], dict):
                        self.logger.error(f"skipping secret {secret_auth_name} is not a dict")
                        continue

                    # only mount secrets_requirement
                    if 'all' not in secrets_requirement:
                        if mysecretdict[secret_auth_name]['type'] not in secrets_requirement:
                            self.logger.debug(f"skipping {mysecretdict[secret_auth_name]['type']} not in {secrets_requirement}")
                            continue

                    self.logger.debug( f"adding secret type {mysecretdict[secret_auth_name]['type']} to volume pod" )
                    secretmountPath = oc.od.settings.desktop['secretsrootdirectory'] + mysecretdict[secret_auth_name]['type'] 
                    # mode is 644 -> rw-r--r--
                    # Owing to JSON limitations, you must specify the mode in decimal notation.
                    # 644 in decimal equal to 420
                    volumes[secret_auth_name] = {
                        'name':secret_auth_name, 
                        'secret': { 
                            'secretName': secret_auth_name, 
                            'defaultMode': 420
                        }
                    }
                    volumes_mount[secret_auth_name] = {
                        'name':secret_auth_name, 
                        'mountPath':secretmountPath 
                    }   
        return (volumes, volumes_mount)

    def build_volumes_additional_by_rules( self, authinfo, userinfo, volume_type, secrets_requirement, rules={}, **kwargs):
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"

        volumes = {}        # set empty volume dict by default
        volumes_mount = {}  # set empty volume_mount dict by default
        if isinstance( rules, dict ):
            self.logger.debug( f"selected volume by rules {rules}" )
            mountvols = oc.od.volume.selectODVolumebyRules( authinfo, userinfo, rules=rules.get('volumes') )
            for mountvol in mountvols:
                fstype = mountvol.fstype
                volume_name = self.get_volumename( mountvol.name, userinfo )
                self.logger.debug( f"selected volume fstype:{fstype} volumes name:{volume_name}")

                # if fstype='csi-driver'

                if fstype=='nfs':
                    volumes_mount[mountvol.name] = {
                        'name': volume_name, 
                        'mountPath': mountvol.mountPath 
                    }
                    volumes[mountvol.name] = {  
                        'name': volume_name,
                        'nfs' : {
                            'server': mountvol.server,
                            'path': mountvol.path,
                            'readOnly': mountvol.readOnly
                        }
                    }

                if fstype=='pvc':
                    claimName = mountvol.claimName
                    if isinstance(claimName, str):
                        volumes_mount[mountvol.name] = {
                            'name': volume_name, 
                            'mountPath': mountvol.mountPath 
                        }
                        volumes[mountvol.name] = { 
                            'name': volume_name, 
                            'persistentVolumeClaim': { 'claimName': mountvol.claimName } 
                        }
                        
                   

                # mount the remote home dir as a flexvol
                # WARNING ! if the flexvol mount failed, the pod must start
                # abcdesktop/cifs always respond a success
                # in case of failure access right is denied                
                # the flexvolume driver abcdesktop/cifs MUST be deploy on each node

                # Flex volume use kubernetes secret                    
                # Kubernetes secret as already been created by prepareressource function call 
                # Read the secret and use it

                secret = oc.od.secret.selectSecret( self.namespace, self.kubeapi, prefix=mountvol.name, secret_type=fstype )
                if isinstance( secret, oc.od.secret.ODSecret):
                    driver_type =  self.namespace + '/' + fstype
                    self.on_desktoplaunchprogress('b.Building flexVolume storage data for driver ' + driver_type )

                    # read the container mount point from the secret
                    # for example /home/balloon/U             
                    # Read data from secret    
                    secret_name         = secret.get_name( authinfo, userinfo )
                    secret_dict_data    = secret.read_alldata( authinfo, userinfo )
                    if not isinstance( secret_dict_data, dict ):
                        # skipping bad values
                        self.logger.error( f"Invalid value read from secret={secret_name} type={str(type(secret_dict_data))}" )
                        continue

                    mountPath           = secret_dict_data.get( 'mountPath')
                    networkPath         = secret_dict_data.get( 'networkPath' )
                    
                    # Check if the secret contains valid datas 
                    if not isinstance( mountPath, str) :
                        # skipping bad values
                        self.logger.error( f"Invalid value for mountPath read from secret={secret_name} type={str(type(mountPath))}" )
                        continue

                    if not isinstance( networkPath, str) :
                        # skipping bad values
                        self.logger.error( f"Invalid value for networkPath read from secret={secret_name}  type={str(type(networkPath))}" )
                        continue

                    volumes_mount[mountvol.name] = {'name': volume_name, 'mountPath': mountPath }     
                    posixaccount = self.alwaysgetPosixAccountUser( authinfo, userinfo )
                    # Default mount options
                    mountOptions = 'uid=' + str( posixaccount.get('uidNumber') ) + ',gid=' + str( posixaccount.get('gidNumber')  )
                    # concat mountOptions for the volume if exists 
                    if mountvol.has_options():
                        mountOptions += ',' + mountvol.mountOptions

                    # dump for debug
                    self.logger.debug( f"flexvolume: {mountvol.name} set option {mountOptions}" )
                    self.logger.debug( f"flexvolume: read secret {secret_name} to mount {networkPath}")
                    # add dict volumes entry mountvol.name
                    volumes[mountvol.name] = {  
                        'name': volume_name,
                        'flexVolume' : {
                            'driver': driver_type,
                            'fsType': fstype,
                            'secretRef' : { 'name': secret_name },
                            'options'   : { 'networkPath':  networkPath, 'mountOptions': mountOptions }
                        }
                    }
                    # dump for debug
                    self.logger.debug( f"volumes {mountvol.name} use volume {volumes[mountvol.name]} and volume mount {volumes_mount[mountvol.name]}")
        return (volumes, volumes_mount)

    def get_user_homedirectory(self, authinfo:AuthInfo, userinfo:AuthUser )->str:
        self.logger.debug('')
        assert_type(authinfo, AuthInfo)
        assert_type(userinfo, AuthUser)
        localaccount = oc.od.secret.ODSecretLocalAccount( namespace=self.namespace, kubeapi=self.kubeapi )
        localaccount_secret = localaccount.read( authinfo,userinfo )
        homeDirectory = oc.od.secret.ODSecretLocalAccount.read_data( localaccount_secret, 'homeDirectory' )
        if not isinstance( homeDirectory, str ):
            homeDirectory = oc.od.settings.getballoon_homedirectory()
        return homeDirectory

    def get_mixedataforchevron(self, authinfo:AuthInfo, userinfo:AuthUser )->dict:
        assert_type(authinfo, AuthInfo)
        assert_type(userinfo, AuthUser)
        mixedata = self.alwaysgetPosixAccountUser( authinfo, userinfo )
        mixedata.update( authinfo.todict() )
        mixedata.update( authinfo.get_labels())
        mixedata.update( userinfo )
        mixedata['provider']=authinfo.provider.lower()
        mixedata['uuid']=oc.lib.uuid_digits()
        return mixedata

    def build_volumes_home( self, authinfo:AuthInfo, userinfo:AuthUser, volume_type:str, secrets_requirement, rules={}, **kwargs):
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        volumes = {}        # set empty volume dict by default
        volumes_mount = {}  # set empty volume_mount dict by default
        self.on_desktoplaunchprogress('Building home dir data storage')
        volume_home_name = self.get_volumename( 'home', userinfo )

        # homedirectorytype is by default None 
        homedirectorytype = oc.od.settings.desktop['homedirectorytype']
        self.logger.debug(f"homedirectorytype is {homedirectorytype}")
        subpath_name = oc.auth.namedlib.normalize_name( userinfo.userid )
        self.logger.debug(f"subpath_name is {subpath_name}")
        user_homedirectory = os.path.join(  self.get_user_homedirectory(authinfo, userinfo), 
                                            oc.od.settings.desktop.get('appendpathtomounthomevolume','') )
        user_homedirectory = os.path.normpath( user_homedirectory )
        self.logger.debug( f"user_homedirectory mounts home volume to {user_homedirectory}" )
            
        # set default value 
        # home is emptyDir
        # cache is emptyDir Memory
        volumes['home']         = { 'name': volume_home_name, 'emptyDir': {} }
        volumes_mount['home']   = { 'name': volume_home_name, 'mountPath': user_homedirectory }

        # 'cache' volume
        # Take care if this is a pod application the .cache is empty
        self.logger.debug( f"map ~/.cache to emptyDir Memory is {oc.od.settings.desktop.get('homedirdotcachetoemptydir')}" )
        if oc.od.settings.desktop.get('homedirdotcachetoemptydir') is True :
            dotcache_user_homedirectory = self.get_user_homedirectory(authinfo, userinfo) + '/.cache'
            self.logger.debug( f"map {dotcache_user_homedirectory} to emptyDir medium Memory" )
            volumes['cache']       = { 'name': 'cache',  'emptyDir': { 'medium': 'Memory', 'sizeLimit': '8Gi' } }
            volumes_mount['cache'] = { 'name': 'cache',  'mountPath': dotcache_user_homedirectory }
            if volume_type in ['pod_application']:
                self.logger.debug( f"warning {volume_type} maps {dotcache_user_homedirectory} to emptyDir medium Memory" )
                self.logger.debug( f"warning {dotcache_user_homedirectory} does not share data" )
                self.logger.debug( f"warning to disable this features set desktop.homedirdotcachetoemptydir to False" )

        # now ovewrite home values
        if homedirectorytype == 'persistentVolumeClaim':
            claimName = None # None is the default value, nothing to do
            if isinstance( oc.od.settings.desktop['persistentvolumeclaim'], str):
                # oc.od.settings.desktop['persistentvolumeclaim'] is the name of the PVC
                # in this case, there is only one shared PVC for all users
                # and it must already exists 
                if volume_type in [ 'pod_desktop', 'pod_application' ] :
                    claimName = oc.od.settings.desktop['persistentvolumeclaim']

            elif isinstance( oc.od.settings.desktop['persistentvolumeclaim'], dict):
                # oc.od.settings.desktop['persistentvolumeclaim'] must be created by pyos
                if volume_type in [ 'pod_desktop', 'pod_application' ] :
                    # create a pvc to store desktop volume
                    persistentvolume = copy.deepcopy( oc.od.settings.desktop['persistentvolume'] )
                    persistentvolumeclaim = copy.deepcopy( oc.od.settings.desktop['persistentvolumeclaim'] )
                    # use chevron mustache to replace template value in persistentvolume and persistentvolumeclaim
                    mixeddata = self.get_mixedataforchevron( authinfo, userinfo )
                    self.updateChevronDictWithmixedData( persistentvolume, mixeddata=mixeddata)
                    self.updateChevronDictWithmixedData( persistentvolumeclaim, mixeddata=mixeddata)
                    self.logger.debug( f"persistentvolume={persistentvolume}" )
                    self.logger.debug( f"persistentvolumeclaim={persistentvolumeclaim}" )
                    self.on_desktoplaunchprogress( f"b.Creating your own volume to store files" )
                    # create the user's persistentVolumeClaim if not exist
                    odvol = oc.od.persistentvolumeclaim.ODPersistentVolumeClaim( self.namespace, self.kubeapi )
                    pvc = odvol.create( authinfo=authinfo,
                                        userinfo=userinfo, 
                                        persistentvolume_request=persistentvolume,
                                        persistentvolumeclaim_request=persistentvolumeclaim )
                    # wait for user's persistentVolumeClaim to bound 
                    if isinstance( pvc, V1PersistentVolumeClaim ):
                        claimName = pvc.metadata.name
                        (status,msg) = odvol.waitforBoundPVC( name=claimName, callback_notify=self.on_desktoplaunchprogress )
                        self.logger.debug( f"bound PersistentVolumeClaim {claimName} return {status} {msg}" )
                        if status is False:
                            self.logger.error( f"PersistentVolumeClaim {claimName} can NOT Bound, {msg}")
                            # we continue but this can be a fatal error
                        self.on_desktoplaunchprogress( msg )
                    else:
                        self.logger.error( "can not create PersistentVolumeClaim" )
                        self.on_desktoplaunchprogress( "can not create PersistentVolumeClaim read log file" )
                        # we continue but this can be a fatal error
                        
                if volume_type in [ 'ephemeral_container']:
                    persistentvolumeclaim = copy.deepcopy( oc.od.settings.desktop['persistentvolumeclaim'] )
                    # use chevron mustache to replace template value in persistentvolumeclaim
                    mixeddata = self.get_mixedataforchevron( authinfo, userinfo )
                    self.updateChevronDictWithmixedData( persistentvolumeclaim, mixeddata=mixeddata)
                    self.logger.debug( f"persistentvolumeclaim={persistentvolumeclaim}" )
                    odpvc = oc.od.persistentvolumeclaim.ODPersistentVolumeClaim(self.namespace, self.kubeapi)
                    pvc = odpvc.find_pvc(authinfo, userinfo, persistentvolumeclaim )
                    assert isinstance(pvc, V1PersistentVolumeClaim ),  f"persistentvolumeclaim for {volume_type} is not found"
                    claimName = pvc.metadata.name
               
            # Map the home directory
            # volume_type is in [ 'ephemeral_container', 'pod_desktop', 'pod_application' ] :
            self.logger.debug( f"persistentVolumeClaim claimName={claimName}" )
            if isinstance(claimName, str):
                volumes['home'] = { 'name': volume_home_name, 'persistentVolumeClaim': { 'claimName': claimName } }
                volumes_mount['home'] = { 'name': volume_home_name, 'mountPath': user_homedirectory }
                if oc.od.settings.desktop['persistentvolumeclaimforcesubpath'] is True:
                    volumes_mount['home']['subPath'] = subpath_name
           
        elif homedirectorytype == 'hostPath' :
            # Map the home directory
            # mount_volume = '/mnt/abcdesktop/$USERNAME' on host
            # volume type is 'DirectoryOrCreate'
            # same as 'subPath' but use hostpath
            # 'subPath' is not supported for ephemeral container
            #
            # An empty directory will be created there as needed with permission set to 0755, 
            # having the same group and ownership with Kubelet.
            #
            mount_volume = oc.od.settings.desktop['hostPathRoot'] + '/' + subpath_name
            volumes['home'] = {
                'name':volume_home_name, 
                'hostPath': {
                    'path':mount_volume, 
                    'type':'DirectoryOrCreate'
                }  
            }
            volumes_mount['home'] = {
                'name':volume_home_name, 
                'mountPath':user_homedirectory
            }

        elif homedirectorytype == 'nfs' :
            nfs = copy.deepcopy( oc.od.settings.desktop['nfs'] )
            # use chevron mustache to replace template value in persistentvolumeclaim
            mixeddata = self.get_mixedataforchevron( authinfo, userinfo )
            self.updateChevronDictWithmixedData( nfs, mixeddata=mixeddata)
            self.logger.debug( f"nfs={nfs}" )
            volumes['home'] = {
                'name':volume_home_name, 
                'nfs': nfs
            }
            volumes_mount['home'] = {
                'name':volume_home_name, 
                'mountPath':user_homedirectory
            }

        self.logger.debug( f"volumes_mount['home']: {volumes_mount.get('home')}" )
        self.logger.debug( f"volumes['home']: {volumes.get('home')}")
        self.logger.debug( f"volumes_mount['cache']: {volumes_mount.get('cache')}" )
        self.logger.debug( f"volumes['cache']: {volumes.get('cache')}")
        return (volumes, volumes_mount)


    def build_volumes_vnc( self, authinfo:AuthInfo, userinfo:AuthUser, volume_type, secrets_requirement, rules={}, **kwargs):
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        volumes = {}        # set empty volume dict by default
        volumes_mount = {}  # set empty volume_mount dict by default
         # Add VNC password
        mysecretdict = self.list_dict_secret_data( authinfo, userinfo, access_type='vnc' )
        # mysecretdict must be a dict
        assert isinstance(mysecretdict, dict),  f"mysecretdict has invalid type {type(mysecretdict)}"
        assert len(mysecretdict)>0,             f"mysecretdict has invalid len {len(mysecretdict)}"
        # the should only be one secret type vnc
        secret_auth_name = next(iter(mysecretdict)) # first entry of the dict
        # create an entry /var/secrets/abcdesktop/vnc
        secretmountPath = oc.od.settings.desktop['secretsrootdirectory'] + mysecretdict[secret_auth_name]['type']
        # mode is 644 -> rw-r--r--
        # Owing to JSON limitations, you must specify the mode in decimal notation.
        # 644 in decimal equal to 420
        volumes[secret_auth_name] = {
            'name': secret_auth_name,
            'secret': { 
                'secretName': secret_auth_name, 
                'defaultMode':420 }
        }
        volumes_mount[secret_auth_name] = {
            'name':secret_auth_name, 
            'mountPath': secretmountPath
        } 
        return (volumes, volumes_mount)


    def get_volumes_localaccount_name( self, authinfo:AuthInfo, userinfo:AuthUser )->str:
        """get_volumes_localaccount_name

        Args:
            authinfo (AuthInfo): AuthInfo
            userinfo (AuthUser): AuthUser

        Returns:
            str: return the name of the localaccount volume same as secret 
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        
        localaccount_name = None
        mysecretdict = self.list_dict_secret_data( authinfo, userinfo, access_type='localaccount' )
        if isinstance(mysecretdict, dict ) and len(mysecretdict)>0:
            localaccount_name = list( mysecretdict.keys() )[0] # should be only one, get the first one
        return localaccount_name


    def build_volumes_localaccount( self, authinfo:AuthInfo, userinfo:AuthUser, volume_type, secrets_requirement, rules={}, **kwargs):
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        volumes = {}        # set empty volume dict by default
        volumes_mount = {}  # set empty volume_mount dict by default

        #
        # mount secret in directory desktop['secretslocalaccount'] eq: /etc/localaccount
        #
        mysecretdict = self.list_dict_secret_data( authinfo, userinfo, access_type='localaccount' )
        #secret = oc.od.secret.ODSecretLocalAccount( namespace=self.namespace, kubeapi=self.kubeapi )
        #localaccountsecret = secret.read_alldata
        for secret_auth_name in mysecretdict.keys():
            # https://kubernetes.io/docs/concepts/configuration/secret
            # create an entry in desktop['secretslocalaccount']
            # do not use the namespace
            self.logger.debug( f"adding secret type {mysecretdict[secret_auth_name]['type']}" )
            secretmountPath = oc.od.settings.desktop['secretslocalaccount']
            # mode is 644 -> rw-r--r--
            # Owing to JSON limitations, you must specify the mode in decimal notation.
            # 644 in decimal equal to 420
            volumes[secret_auth_name]       = { 'name': secret_auth_name, 'secret': { 'secretName': secret_auth_name, 'defaultMode': 420  } }
            volumes_mount[secret_auth_name] = { 'name': secret_auth_name, 'mountPath':  secretmountPath }

        return (volumes, volumes_mount)

    def build_volumes( self, authinfo:AuthInfo, userinfo:AuthUser, volume_type, secrets_requirement, rules={}, **kwargs):
        """[build_volumes]

        Args:
            authinfo ([type]): [description]
            userinfo (AuthUser): user data
            volume_type ([str]): 'container_desktop' 'pod_desktop', 'pod_application', 'ephemeral_container'
            rules (dict, optional): [description]. Defaults to {}.

        Returns:
            [type]: [description]
        """
        volumes = {}        # set empty volume dict by default
        volumes_mount = {}  # set empty volume_mount dict by default

        #
        # mount home volume
        #
        (home_volumes, home_volumes_mount) = self.build_volumes_home(authinfo, userinfo, volume_type, secrets_requirement, rules, **kwargs)
        volumes.update(home_volumes)
        volumes_mount.update(home_volumes_mount)

        #
        # Set localtime to server time
        #
        if oc.od.settings.desktop['uselocaltime'] is True:
            volumes['localtime'] = { 'name': 'localtime', 'hostPath': { 'path': '/etc/localtime' } }
            volumes_mount['localtime'] = { 'name': 'localtime', 'mountPath' : '/etc/localtime' }

        #
        # volume shared between all container inside the desktop pod
        #
        if volume_type in [ 'pod_desktop', 'ephemeral_container' ]:
            # add socket service 
            for vol_name in [ 'x11socket', 'pulseaudiosocket', 'cupsdsocket' ]:
                volumes[vol_name] = self.default_volumes[vol_name]
                volumes_mount[vol_name] = self.default_volumes_mount[vol_name]

            # add tmp run log to support readonly filesystem
            for vol_name in [ 'tmp', 'run', 'log' ]:
                volumes[vol_name] = self.default_volumes[vol_name]
                volumes_mount[vol_name] = self.default_volumes_mount[vol_name]

            # add dbus
            for vol_name in [ 'rundbus', 'runuser' ]:
                volumes[vol_name] = self.default_volumes[vol_name]
                volumes_mount[vol_name] = self.default_volumes_mount[vol_name]

        #
        # shm volume is shared between all container inside the desktop pod
        #
        if volume_type in [ 'pod_desktop', 'container_desktop', 'ephemeral_container' ]:
            volumes['shm'] = self.default_volumes['shm']
            volumes_mount['shm'] = self.default_volumes_mount['shm']

        #
        # mount localaccount secrets in desktop['secretslocalaccount'] eq: /etc/localaccount
        # desktop['secretslocalaccount'] SHOULD NOT use the namepace  
        # do not hard code the abcdesktop because oc.user container image use a symbolic link to 
        # - /etc/passwd -> desktop['secretslocalaccount']/passwd 
        # - /etc/shadow -> desktop['secretslocalaccount']/shadow 
        # - /etc/group  -> desktop['secretslocalaccount']/group 
        # - /etc/gshadow -> desktop['secretslocalaccount']/gshadow 
        # files are linked to desktop['secretslocalaccount']
        #
        if volume_type in [ 'pod_desktop', 'pod_application',  'ephemeral_container' ] :
            (localaccount_volumes, localaccount_volumes_mount) = \
                self.build_volumes_localaccount(authinfo, userinfo, volume_type, secrets_requirement, rules, **kwargs)
            volumes.update( localaccount_volumes )
            volumes_mount.update( localaccount_volumes_mount )

        #
        # mount vnc secret in /var/secrets/abcdesktop
        # always add vnc secret for 'pod_desktop'
        if volume_type in [ 'pod_desktop'  ] :
            (vnc_volumes, vnc_volumes_mount) = \
                self.build_volumes_vnc(authinfo, userinfo, volume_type, secrets_requirement, rules, **kwargs)
            volumes.update(vnc_volumes)
            volumes_mount.update(vnc_volumes_mount)

        #
        # mount secret in /var/secrets/abcdesktop
        #
        (secret_volumes, secret_volumes_mount) = \
            self.build_volumes_secrets(authinfo, userinfo, volume_type, secrets_requirement, rules, **kwargs)
        volumes.update(secret_volumes)
        volumes_mount.update(secret_volumes_mount)


        #
        # mount voulumes from rules
        #
        (rules_volumes, rules_volumes_mount) = \
            self.build_volumes_additional_by_rules(authinfo, userinfo, volume_type, secrets_requirement, rules, **kwargs)
        volumes.update(rules_volumes)
        volumes_mount.update(rules_volumes_mount)
        self.logger.debug('volumes end')        
        return (volumes, volumes_mount)

        
    def execwaitincontainer( self, desktop:ODDesktop, command:list, timeout:int=5):
        """execwaitincontainer
            execwaitincontainer execute command in desktop
        Args:
            desktop (ODDesktop): desktop
            command (list): list of string commands
            timeout (int, optional): timeout. Defaults to 5.

        Returns:
            dict: { 'ExitCode': int, 'stdout': None } 
            default { 'ExitCode': -1, 'stdout': None } 
        """
        self.logger.info('')
        result = { 'ExitCode': -1, 'stdout': None } # default value 
        #
        # calling exec and wait for response.
        # read https://github.com/kubernetes-client/python/blob/master/examples/pod_exec.py
        # for more example
        #   
        try:            
            resp = stream(  self.kubeapi.connect_get_namespaced_pod_exec, 
                            name=desktop.name, 
                            namespace=self.namespace, 
                            command=command,                                                                
                            container=desktop.container_name,
                            stderr=True, stdin=False,
                            stdout=True, tty=False,
                            _preload_content=False, #  need a client object websocket           
            )
            resp.run_forever(timeout) # timeout in seconds
            err = resp.read_channel(ERROR_CHANNEL, timeout=timeout)
            self.logger.debug( f"exec in desktop.name={desktop.name} container={desktop.container_name} command={command} return code {err}")
            respdict = yaml.load(err, Loader=yaml.BaseLoader )        
            result['stdout'] = resp.read_stdout()
            # should be like:
            # {"metadata":{},"status":"Success"}
            if isinstance(respdict, dict):
                # status = Success or ExitCode = ExitCode
                exit_code = respdict.get('ExitCode')
                if isinstance( exit_code, int):
                    result['ExitCode'] = exit_code
                else:
                    if respdict.get('status') == 'Success':
                        result['ExitCode'] = 0

        except Exception as e:
            self.logger.error( f"command exec failed {e}") 

        return result

    def removePod( self, myPod:V1Pod, propagation_policy:str='Foreground', grace_period_seconds:int=None) -> V1Pod:
        """_summary_
            Remove a pod
            like command 'kubectl delete pods'
        Args:
            myPod (V1Pod): V1Pod
            propagation_policy (str, optional): propagation_policy. Defaults to 'Foreground'.
            # https://kubernetes.io/docs/concepts/architecture/garbage-collection/
            # propagation_policy = 'Background'
            # propagation_policy = 'Foreground'
            # Foreground: Children are deleted before the parent (post-order)
            # Background: Parent is deleted before the children (pre-order)
            # Orphan: Owner references are ignored
            # delete_options = client.V1DeleteOptions( propagation_policy = propagation_policy, grace_period_seconds = grace_period_seconds )

        Returns:
            v1status: v1status
        """
        self.logger.debug('')
        assert isinstance(myPod, V1Pod), f"myPod invalid type {type(myPod)}"
        deletedPod = None
        try:  
            deletedPod = self.kubeapi.delete_namespaced_pod(  
                name=myPod.metadata.name, 
                namespace=self.namespace, 
                grace_period_seconds=grace_period_seconds, 
                propagation_policy=propagation_policy 
            ) 
        except ApiException as e:
            self.logger.error( str(e) )

        return deletedPod

    def removesecrets( self, authinfo:AuthInfo, userinfo:AuthUser )->bool:
        """removesecrets
            remove all kubernetes secrets for a give user
            list_dict_secret_data( authinfo, userinfo, access_type=None)
            then delete the secret 
            
        Args:
            authinfo (AuthInfo): authinfo
            userinfo (AuthUser): authuser

        Returns:
            bool: True if all users's secrets are deleted else False
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        ''' remove all kubernetes secrets for a give user '''
        ''' access_type is None will list all secret type '''
        bReturn = True
        # access_type is None will list all secret type
        dict_secret = self.list_dict_secret_data( authinfo, userinfo, access_type=None)
        for secret_name in dict_secret.keys():
            try:
                v1status = self.kubeapi.delete_namespaced_secret( name=secret_name, namespace=self.namespace )
                if not isinstance(v1status,V1Status) :
                    self.logger.error( 'invalid V1Status type return by delete_namespaced_secret')
                    continue
                self.logger.debug(f"secret={secret_name} status={v1status.status}") 
                if v1status.status != 'Success':
                    self.logger.error(f"secret {secret_name} can not be deleted {v1status}" ) 
                    bReturn = bReturn and False
            except ApiException as e:
                self.logger.error(f"secret {secret_name} can not be deleted {e}") 
                bReturn = bReturn and False
        self.logger.debug(f"removesecrets for {userinfo.userid} return {bReturn}" ) 
        return bReturn 
   


    def removeconfigmap( self, authinfo:AuthInfo, userinfo:AuthUser )->bool:
        """removeconfigmap
            remove all kubernetes configmap for a give user

        Args:
            authinfo (AuthInfo): authinfo
            userinfo (AuthUser): authuser

        Returns:
            bool: True if all users's configmaps are deleted else False
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        bReturn = True
        dict_configmap = self.list_dict_configmap_data( authinfo, userinfo, access_type=None)
        for configmap_name in dict_configmap.keys():
            try:            
                v1status = self.kubeapi.delete_namespaced_config_map( name=configmap_name, namespace=self.namespace )
                if not isinstance(v1status,V1Status) :
                    self.logger.error( 'Invalid V1Status type return by delete_namespaced_config_map')
                    continue
                self.logger.debug(f"configmap {configmap_name} status {v1status.status}") 
                if v1status.status != 'Success':
                    self.logger.error(f"configmap name {configmap_name} can not be deleted {str(v1status)}") 
                    bReturn = bReturn and False
                    
            except ApiException as e:
                self.logger.error(f"configmap name {configmap_name} can not be deleted: error {e}") 
                bReturn = bReturn and False
        return bReturn 

    def removepodindesktop(self, authinfo:AuthInfo, userinfo:AuthUser , myPod:V1Pod=None )->bool:
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        # get the user's pod
        if not isinstance(myPod, V1Pod ):
            myPod = self.findPodByUser(authinfo, userinfo )

        if isinstance(myPod, V1Pod ):
            # delete this pod immediatly
            deletedpod = self.removePod( myPod, propagation_policy='Foreground', grace_period_seconds=0 )
            if isinstance(deletedpod,V1Pod) :
                return True
        return False
    
    """removePodSync
    def removePodSync(self, authinfo:AuthInfo, userinfo:AuthUser , myPod:V1Pod=None )->bool:
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        # get the user's pod
        if not isinstance(myPod, V1Pod ):
            myPod = self.findPodByUser(authinfo, userinfo )
        nTry = 0
        nMaxTry = 42
        if isinstance(myPod, V1Pod ):
            deletedPod = self.removePod( myPod, propagation_policy='Foreground', grace_period_seconds=30 )
            if isinstance(deletedPod, V1Pod ):
                while nTry<nMaxTry:
                    try:
                        myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=deletedPod.metadata.name)
                        if isinstance(myPod, V1Pod ):
                            message = f"b.deleting {myPod.metadata.name} {myPod.status.phase} {nTry}/{nMaxTry}"
                            self.logger.debug( message )
                            self.on_desktoplaunchprogress( message )
                    except ApiException as e:
                        if e.status == 404:
                            return True
                        else:
                            self.on_desktoplaunchprogress( e )
                            return False
                    # wait one second
                    time.sleep(1) 
                    nTry = nTry + 1
        return False
    """

    def removedesktop(self, authinfo:AuthInfo, userinfo:AuthUser , myPod:V1Pod=None)->bool:
        """removedesktop
            remove kubernetes pod for a give user
            then remove kubernetes user's secrets and configmap
        Args:
            authinfo (AuthInfo): _description_
            userinfo (AuthUser): _description_
            myPod (V1Pod, optional): _description_. Defaults to None.

        Returns:
            bool: _description_
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        deletedpod = False # default value 
        self.logger.info( f"removedesktop for {authinfo.provider} {userinfo.userid}" )

        # get the user's pod
        if not isinstance(myPod, V1Pod ):
            myPod = self.findPodByUser(authinfo, userinfo )

        if isinstance(myPod, V1Pod ):
            # create an array of threads to remove user objects  
            # removePod: remove the user pod 
            # removeAppInstanceKubernetesPod: remove all applications pod
            # removesecrets: remove secret 
            # removeconfigmap: remove config map
            myappinstance = ODAppInstanceKubernetesPod( self )

            removethreads =  [  
                { 'fct':self.removePod, 'args': [ myPod ] },
                { 'fct':myappinstance.removeAppInstanceKubernetesPod, 'args': [ authinfo, userinfo ] },
                { 'fct':self.removesecrets, 'args': [ authinfo, userinfo ] },
                { 'fct':self.removeconfigmap, 'args': [ authinfo, userinfo ] },
                { 'fct':self.removepvc, 'args': [ authinfo, userinfo ] } 
            ]
   
            for removethread in removethreads:
                self.logger.debug( f"calling thread {removethread['fct'].__name__}" )
                removethread['thread']=threading.Thread(target=removethread['fct'], args=removethread['args'])
                removethread['thread'].start()

            deletedpod = True
            # need to wait for removethread['thread'].join()
            # for removethread in removethreads:
            #    removethread['thread'].join()

        else:
            self.logger.error( f"removedesktop can not find desktop {authinfo} {userinfo}" )
        return deletedpod

    def removepvc(self, authinfo:AuthInfo, userinfo:AuthUser)->V1PersistentVolumeClaim:
        self.logger.debug('')
        
        bReturn = False
        if isinstance( oc.od.settings.desktop['persistentvolumeclaim'], str):
            # there is only one PVC for all users
            # by pass this call
            return bReturn 
        
        if oc.od.settings.desktop['removepersistentvolumeclaim'] is False:
            # removepersistentvolumeclaim is False, do not delete 
            # by pass this call
            return bReturn 

        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        odvol = oc.od.persistentvolumeclaim.ODPersistentVolumeClaim( self.namespace, self.kubeapi )
        # list all pvc for the user and delete pvc
        deleted_pvc = odvol.delete_pvc( authinfo=authinfo, userinfo=userinfo )
        return deleted_pvc


    def preparelocalaccount( self, localaccount:dict )->dict:
        assert isinstance(localaccount, dict),f"invalid localaccount type {type(localaccount)}"    
        mydict_config = { 
            'passwd' : AuthUser.mkpasswd(localaccount), 
            'shadow' : AuthUser.mkshadow(localaccount), 
            'group'  : AuthUser.mkgroup(localaccount),
            'gshadow': AuthUser.mkgshadow(localaccount), 
        }
        return mydict_config
            
    def prepareressources(self, authinfo:AuthInfo, userinfo:AuthUser):
        """[prepareressources]

        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data

        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        # create a kerberos kubernets secret 
        #  
        # translate the userid as sAMAccountName in the authinfo.claims dict
        # Flex volume use kubernetes secret                    
        # arguments = authinfo.claims
        # arguments['user'] = authinfo.claims['userid']
        # arguments['data'] = { 'realm': authinfo.claims['realm'], 'ticket': authinfo.claims['ticket'] }

        # Build the kubernetes secret 
        # auth_type = 'kerberos'
        # secret_type = 'abcdesktop/' + auth_type
        # secret = ODSecret( self.namespace, self.kubeapi, secret_type )
        # auth_secret = secret.create( arguments )
          # compile a env list with the auth list  
        # translate auth environment to env 

        #
        # Create ODSecretLDIF, build userinfo object secret ldif cache
        # This section is necessary to get user photo in user_controller.py
        # dump the ldif in kubernetes secret 
        # whoami entry point use the ldiff secret 
        # create a ldif secret
        self.logger.debug('oc.od.secret.ODSecretLDIF creating')
        secret = oc.od.secret.ODSecretLDIF( namespace=self.namespace, kubeapi=self.kubeapi )
        createdsecret = secret.create( authinfo, userinfo, data=userinfo )
        if not isinstance( createdsecret, V1Secret):
            self.logger.error(f"can not create secret {secret.get_name(authinfo, userinfo)}")
        else:
            self.logger.debug(f"LDIF secret.create {secret.get_name(authinfo, userinfo)} created")
        self.logger.debug('create oc.od.secret.ODSecretLDIF created')

        # create files as secret 
        # - /etc/passwd 
        # - /etc/shadow 
        # - /etc/group 
        # - /etc/gshadow
        # files will be set as link in build_volumes
        localaccount_data = authinfo.get_localaccount()
        localaccount_files = self.preparelocalaccount( localaccount_data )
        self.logger.debug('localaccount secret.create creating')
        secret = oc.od.secret.ODSecretLocalAccount( namespace=self.namespace, kubeapi=self.kubeapi )
        createdsecret = secret.create( authinfo, userinfo, data=localaccount_files )
        if not isinstance( createdsecret, V1Secret):
            self.logger.error(f"can not create secret {secret.get_name(authinfo, userinfo)}")
        else:
            self.logger.debug(f"localaccount secret.create {secret.get_name(authinfo, userinfo)} created")

        if userinfo.isPosixAccount():
            self.logger.debug('posixaccount secret.create creating')
            secret = oc.od.secret.ODSecretPosixAccount( namespace=self.namespace, kubeapi=self.kubeapi )
            createdsecret = secret.create( authinfo, userinfo, data=userinfo.getPosixAccount())
            if not isinstance( createdsecret, V1Secret):
                self.logger.error(f"can not create posixaccount secret {secret.get_name(authinfo, userinfo)}")
            else:
                self.logger.debug(f"posixaccount secret.create {secret.get_name(authinfo, userinfo)} created")

        # for each identity in auth enabled
        identities = authinfo.get_identity()
        if isinstance( identities, dict ) :
            for identity_key in identities.keys():
                self.logger.debug(f"secret.create {identity_key} creating")
                secret = oc.od.secret.selectSecret( self.namespace, self.kubeapi, prefix=None, secret_type=identity_key )
                # build a kubernetes secret with the identity auth values 
                # values can be empty to be updated later
                if isinstance( secret, oc.od.secret.ODSecret):
                    identity_data=identities.get(identity_key)
                    createdsecret = secret.create( authinfo, userinfo, data=identity_data )
                    if not isinstance( createdsecret, V1Secret):
                        self.logger.error(f"can not create secret {secret.get_name(authinfo, userinfo)}")
                    else:
                        self.logger.debug(f"secret.create {secret.get_name(authinfo, userinfo)} created")
    
        # Create flexvolume secrets
        self.logger.debug('flexvolume secrets creating')
        rules = oc.od.settings.desktop['policies'].get('rules')
        if isinstance(rules, dict):
            mountvols = oc.od.volume.selectODVolumebyRules( authinfo, userinfo,  rules.get('volumes') )
            for mountvol in mountvols:
                # use as a volume defined and the volume is mountable
                fstype = mountvol.fstype # Get the fstype: for example 'cifs' or 'cifskerberos' or 'webdav' or 'nfs'
                # find a secret class, can return None if fstype does not need a auth
                secret = oc.od.secret.selectSecret( self.namespace, self.kubeapi, prefix=mountvol.name, secret_type=fstype)
                if isinstance( secret, oc.od.secret.ODSecret):
                    # Flex volume use kubernetes secret, add mouting path
                    arguments = { 'mountPath': mountvol.containertarget, 'networkPath': mountvol.networkPath, 'mountOptions': mountvol.mountOptions }
                    # Build the kubernetes secret
                    auth_secret = secret.create( authinfo, userinfo, arguments )
                    if not isinstance( auth_secret, V1Secret):
                        self.logger.error( f"Failed to build auth secret {secret.get_name(authinfo, userinfo)} fstype={fstype}" )
                    else:
                        self.logger.debug(f"secret.create {secret.get_name(authinfo, userinfo)} created")


    def get_annotations_lastlogin_datetime(self):
        """get_annotations_lastlogin_datetime
            return a dict { 'lastlogin_datetime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") }

        Returns:
            dict: { 'lastlogin_datetime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        """
        annotations = { 'lastlogin_datetime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") } 
        return annotations

    def read_pod_annotations_lastlogin_datetime(self, pod:V1Pod )->datetime.datetime:
        """read_pod_annotations_lastlogin_datetime
            read pod annotations data lastlogin_datetime value

        Args:
            pod (V1Pod): kubernetes pod

        Returns:
            datetime: a datetime from pod.metadata.annotations.get('lastlogin_datetime') None if not set
        """
        resumed_datetime = None
        str_lastlogin_datetime = pod.metadata.annotations.get('lastlogin_datetime')
        if isinstance(str_lastlogin_datetime,str):
            resumed_datetime = datetime.datetime.strptime(str_lastlogin_datetime, "%Y-%m-%dT%H:%M:%S")
        return resumed_datetime

    def resumedesktop(self, authinfo:AuthInfo, userinfo:AuthUser)->ODDesktop:
        """resume desktop update the lastconnectdatetime annotations data
           findPodByuser and update the lastconnectdatetime using patch_namespaced_pod
        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 

        Returns:
            [ODesktop]: Desktop Object updated annotations data
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        myDesktop = None
        myPod =  self.findPodByUser(authinfo, userinfo)
        if isinstance(myPod, V1Pod ):
            # check the pod status
            if isinstance(myPod.status, V1PodStatus):
                if myPod.status.phase != 'Running':
                    # someting goes wrong
                    return f"Your pod is in phase {myPod.status.phase}, resume pod failed" 
            else:
                return 'Your pod has no status entry, fatal error' 
            # update the metadata.annotations ['lastlogin_datetime'] in pod
            annotations = myPod.metadata.annotations
            new_lastlogin_datetime = self.get_annotations_lastlogin_datetime()
            annotations['lastlogin_datetime'] = new_lastlogin_datetime['lastlogin_datetime']
            newmetadata=V1ObjectMeta(annotations=annotations)
            body = V1Pod(metadata=newmetadata)
            v1newPod = self.kubeapi.patch_namespaced_pod(   
                name=myPod.metadata.name, 
                namespace=self.namespace, 
                body=body )
            if isinstance(v1newPod, V1Pod ):
                myDesktop = self.pod2desktop( pod=v1newPod, authinfo=authinfo, userinfo=userinfo )
            else:
                self.logger.error( 'Patch annontation lastlogin_datetime failed' )
                # reread the non updated desktop if patch failed
                myDesktop = self.pod2desktop( pod=myPod, authinfo=authinfo, userinfo=userinfo )
        return myDesktop

    def getsecretuserinfo(self, authinfo:AuthInfo, userinfo:AuthUser)->dict:
        """read cached user info dict from a ldif secret

        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 

        Returns:
            [dict]: cached user info dict from ldif secret
                    empty dict if None
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        dict_secret = self.list_dict_secret_data( authinfo, userinfo )
        raw_secrets = {}
        for key in dict_secret.keys():
            secret = dict_secret[key]
            if isinstance(secret, dict) and secret.get('type') == 'abcdesktop/ldif':
                raw_secrets.update( secret )
                break
        return raw_secrets

    def getldifsecretuserinfo(self, authinfo:AuthInfo, userinfo:AuthUser)->dict:
        """getldifsecretuserinfo 
                read cached user info dict from a ldif secret

        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 

        Returns:
            [dict]: cached user info dict from ldif secret
                    empty dict if None
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        secret = oc.od.secret.ODSecretLDIF( namespace=self.namespace, kubeapi=self.kubeapi )
        data = secret.read_alldata(authinfo,userinfo)
        return data


    def list_dict_configmap_data( self, authinfo:AuthInfo, userinfo:AuthUser, access_type=None, hidden_empty=False )->dict:
        """get a dict of secret (key value) for the access_type
           if access_type is None will list all user secrets
        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 
            access_type (str): type of secret like 'auth' 

        Returns:
            dict: return dict of secret key value 
        """
        access_userid = userinfo.userid
        access_provider = authinfo.provider
        configmap_dict = {}
        try: 
            label_selector = f"access_userid={access_userid}"
            if oc.od.settings.desktop['authproviderneverchange'] is True:
                label_selector += f",access_provider={access_provider}"
            if isinstance(access_type,str) :
                label_selector += f",access_type={access_type}"
           
            kconfigmap_list = self.kubeapi.list_namespaced_config_map(self.namespace, label_selector=label_selector)
          
            for myconfigmap in kconfigmap_list.items:
                if hidden_empty :
                    # check if mysecret.data is None or an emtpy dict 
                    if myconfigmap.data is None :
                        continue
                    if isinstance( myconfigmap.data, dict) and len( myconfigmap.data ) == 0: 
                        continue
                configmap_dict[myconfigmap.metadata.name] = { 'data': myconfigmap.data }
      
        except ApiException as e:
            self.logger.error("Exception %s", str(e) )
    
        return configmap_dict

    def list_dict_secret_data( self, authinfo:AuthInfo, userinfo:AuthUser, access_type=None, hidden_empty=False )->dict:
        """get a dict of secret (key value) for the access_type
           if access_type is None will list all user secrets
        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 
            access_type (str): type of secret like 'auth' 

        Returns:
            dict: return dict of secret key value 
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        access_userid = userinfo.userid
        access_provider = authinfo.provider
        secret_dict = {}
        try: 
            label_selector = f"access_userid={access_userid}"

            if oc.od.settings.desktop['authproviderneverchange'] is True:
                label_selector += f",access_provider={access_provider}"
            if isinstance(access_type,str) :
                label_selector += f",access_type={access_type}"
           
            ksecret_list = self.kubeapi.list_namespaced_secret(self.namespace, label_selector=label_selector)
          
            for mysecret in ksecret_list.items:
                if hidden_empty :
                    # check if mysecret.data is None or an emtpy dict 
                    if mysecret.data is None :
                        continue
                    if isinstance( mysecret.data, dict) and len( mysecret.data ) == 0: 
                        continue

                secret_dict[mysecret.metadata.name] = { 'type': mysecret.type, 'data': mysecret.data }
                if isinstance( mysecret.data, dict):
                    for mysecretkey in mysecret.data:
                        data = oc.od.secret.ODSecret.read_data( mysecret, mysecretkey )
                        secret_dict[mysecret.metadata.name]['data'][mysecretkey] = data 

        except ApiException as e:
            self.logger.error("Exception %s", str(e) )
    
        return secret_dict

    def get_auth_env_dict( self, authinfo:AuthInfo, userinfo:AuthUser )->dict:
        """get_auth_env_dict

        Args:
            authinfo (AuthInfo): _description_
            userinfo (AuthUser): _description_

        Returns:
            dict: return a dict without secret name, merge all data 
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        dict_secret = self.list_dict_secret_data( authinfo, userinfo, access_type='auth')
        raw_secrets = {}
        for key in dict_secret.keys():
            raw_secrets.update( dict_secret[key] )
        return raw_secrets


    def filldictcontextvalue( self, authinfo:AuthInfo, userinfo:AuthUser, desktop:ODDesktop, network_config:str, network_name=None, appinstance_id=None ):
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        fillvalue = network_config
        # self.logger.debug( f"type(network_config) is {type(network_config)}" )
        # check if network_config is str, dict or list
        if isinstance( network_config, str) :
            fillvalue = self.fillwebhook(   mustachecmd=network_config, 
                                            app=desktop, 
                                            authinfo=authinfo, 
                                            userinfo=userinfo, 
                                            network_name=network_name, 
                                            containerid=appinstance_id )

        elif isinstance( network_config, dict) :
            fillvalue = {}
            for k in network_config.keys():
                fillvalue[ k ] = self.filldictcontextvalue( authinfo, userinfo, desktop, network_config[ k ], network_name, appinstance_id )

        elif isinstance( network_config, list) :
            fillvalue = [None] * len(network_config)
            for i, item in enumerate(network_config):
                fillvalue[ i ] = self.filldictcontextvalue( authinfo, userinfo, desktop, item, network_name, appinstance_id )
    
        # self.logger.debug(f"filldictcontextvalue return fillvalue={fillvalue}")
        return fillvalue



    def is_instance_app( self, appinstance ):
        for app in self.appinstance_classes.values():
            if app(self).isinstance( appinstance ):
                return True
        return False

    def countRunningAppforUser( self, authinfo:AuthInfo, userinfo:AuthUser, myDesktop:ODDesktop)->int:
        """countRunningAppforUser

        Args:
            authinfo (AuthInfo): _description_
            userinfo (AuthUser): _description_
            myDesktop (ODDesktop): _description_

        Returns:
            int: counter of running applications for a user
        """
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        assert isinstance(myDesktop, ODDesktop),  f"myDesktop has invalid type {type(myDesktop)}"
        self.logger.debug('')
        count = 0
        for appinstance in self.appinstance_classes.values() :
            myappinstance = appinstance( self )
            count += len( myappinstance.list(authinfo, userinfo, myDesktop ) )
        return count

    def listContainerApps( self, authinfo:AuthInfo, userinfo:AuthUser, myDesktop:ODDesktop, apps:ODApps ):
        """listContainerApps

        Args:
            authinfo (AuthInfo): _description_
            userinfo (AuthUser): _description_
            myDesktop (ODDesktop): _description_
            apps (ODApps): _description_

        Returns:
            list: list of applications
        """
        assert isinstance(authinfo, AuthInfo),   f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),   f"userinfo has invalid type {type(userinfo)}"
        assert isinstance(myDesktop, ODDesktop), f"myDesktop has invalid type {type(myDesktop)}"
        assert isinstance(apps, ODApps), f"apps has invalid type {type(apps)}"
        self.logger.debug('')
        list_apps = []
        for appinstance in self.appinstance_classes.values() :
            myappinstance = appinstance( self )
            list_apps += myappinstance.list(authinfo, userinfo, myDesktop, phase_filter=self.all_phases_status, apps=apps)
        return list_apps


    def getAppInstanceKubernetes( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str):
        """getAppInstanceKubernetes
            return the AppInstanceKubernetes of an appliction
        Args:
            authinfo (_type_): _description_
            userinfo (_type_): _description_
            pod_name (_type_): _description_
            containerid (_type_): _description_

        Returns:
            ODAppInstanceBase can be :
                - ODAppInstanceKubernetesEphemeralContainer(ODAppInstanceBase): ephemeral container application
                - ODAppInstanceKubernetesPod(ODAppInstanceBase): pod application
        """
        assert isinstance(pod_name, str), f"podname has invalid type {type(pod_name)}"
        myappinstance = None
        myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=pod_name)
        if isinstance( myPod, V1Pod ):
            # if type is x11server app is an ephemeral container
            pod_type = myPod.metadata.labels.get( 'type' )
            if pod_type == self.x11servertype:
                myappinstance = ODAppInstanceKubernetesEphemeralContainer( self )
            elif pod_type in self.appinstance_classes.keys() :
                myappinstance = ODAppInstanceKubernetesPod( self )
        return myappinstance

    def logContainerApp( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str):
        assert isinstance(pod_name, str), f"podname has invalid type {type(pod_name)}"
        log_app = None
        myappinstance = self.getAppInstanceKubernetes(authinfo, userinfo, pod_name, containerid)
        if isinstance( myappinstance, ODAppInstanceBase ):
            log_app = myappinstance.logContainerApp(pod_name, containerid)
        return log_app

    def envContainerApp( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str):
        assert isinstance(pod_name, str), f"podname has invalid type {type(pod_name)}"
        env_result = None
        myappinstance = self.getAppInstanceKubernetes(authinfo, userinfo, pod_name, containerid)
        if isinstance( myappinstance, ODAppInstanceBase ):
            env_result = myappinstance.envContainerApp(authinfo, userinfo, pod_name, containerid)
        return env_result

    def stopContainerApp( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str):
        assert isinstance(pod_name, str), f"podname has invalid type {type(pod_name)}"
        stop_result = None
        myappinstance = self.getAppInstanceKubernetes(authinfo, userinfo, pod_name, containerid)
        if isinstance( myappinstance, ODAppInstanceBase ):
            stop_result = myappinstance.stop(pod_name, containerid)
        return stop_result

    def removeContainerApp( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str):
        return self.stopContainerApp( authinfo, userinfo, pod_name, containerid)

    def getappinstance( self, authinfo, userinfo, app ):    
        self.logger.debug('')
        for app_class in self.appinstance_classes.values():
            app_object = app_class( orchestrator=self )
            appinstance = app_object.findRunningAppInstanceforUserandImage( authinfo, userinfo, app )
            if app_object.isinstance( appinstance ):
                return appinstance

    def execininstance( self, desktop:ODDesktop, command:str)->dict:
        self.logger.info('')
        assert_type( desktop, ODDesktop)

        result = { 'ExitCode': -1, 'stdout':None }
        timeout=5
        # calling exec and wait for response.
        # exec_command = [
        #    '/bin/sh',
        #        '-c',
        #        'echo This message goes to stderr >&2; echo This message goes to stdout']
        # str connect_get_namespaced_pod_exec(name, namespace, command=command, container=container, stderr=stderr, stdin=stdin, stdout=stdout, tty=tty)     
        #
        # Todo
        # read https://github.com/kubernetes-client/python/blob/master/examples/pod_exec.py
        #   
        # container_name = self.get
        try:            
            resp = stream(  self.kubeapi.connect_get_namespaced_pod_exec,
                                name=desktop.name, 
                                container=desktop.container_name, 
                                namespace=self.namespace, 
                                command=command,
                                stderr=True, stdin=False,
                                stdout=True, tty=False,
                                _preload_content=False )
            resp.run_forever(timeout=timeout) 
            if resp.returncode is None:
                # A None value indicates that the process hasn't terminated yet.
                # do not wait 
                result = { 'ExitCode': None, 'stdout': None, 'status': 'Success' }
                resp.close()
            else:
                err = resp.read_channel(ERROR_CHANNEL, timeout=timeout)
                pod_exec_result = yaml.load(err, Loader=yaml.BaseLoader )  
                result['stdout'] = resp.read_stdout(timeout=timeout)
                # should be like:
                # {"metadata":{},"status":"Success"}
                if isinstance(pod_exec_result, dict):
                    if pod_exec_result.get('status') == 'Success':
                        result['status'] = pod_exec_result.get('status')
                        result['ExitCode'] = 0
                    exit_code = pod_exec_result.get('ExitCode')
                    if exit_code is not None:
                        result['ExitCode'] = exit_code
                resp.close()

        except Exception as e:
            self.logger.error( 'command exec failed %s', str(e)) 

        return result

    """
    def read_configmap( self, name, entry ):
        data = None
        try:
            result = self.kubeapi.read_namespaced_config_map( name=name, namespace=self.namespace)      
            if isinstance( result, client.models.v1_config_map.V1ConfigMap):
                data = result.data
                data = json.loads( data.get(entry) )
        except ApiException as e:
            if e.status != 404:
                self.logger.info("Exception when calling read_namespaced_config_map: %s" % e)
        except Exception as e:
            self.logger.info("Exception when calling read_namespaced_config_map: %s" % e)
        return data
    """

        
    def isenablecontainerinpod( self, authinfo:AuthInfo, currentcontainertype:str)->bool:
        """isenablecontainerinpod
            read the desktop configuration and check if this currentcontainertype is allowed
            if currentcontainertype is allowed return True else False

        Args:
            authinfo (_type_): _description_
            currentcontainertype (str): type of container must be defined in list
            [ 'init', 'graphical', 'ssh', 'rdpgw', 'sound', 'printer', 'filter', 'storage' ]

        Returns:
            bool: True if enable, else False
        """

        bReturn =   isinstance( oc.od.settings.desktop_pod.get(currentcontainertype), dict ) is True and \
                    oc.od.acl.ODAcl().isAllowed( authinfo, oc.od.settings.desktop_pod[currentcontainertype].get('acl') ) is True and \
                    oc.od.settings.desktop_pod[currentcontainertype].get('enable') is True
        return bReturn

    def createappinstance(self, myDesktop:ODDesktop, app:dict, authinfo:AuthInfo, userinfo:AuthUser={}, userargs=None, **kwargs )->oc.od.appinstancestatus.ODAppInstanceStatus:
        """createappinstance
            containerengine can be one of the values
                - 'ephemeral_container'
                - 'pod_application'
            the default containerengine value is 'ephemeralcontainer'

        Args:
            myDesktop (ODDesktop): _description_
            app (dict): _description_
            authinfo (AuthInfo): _description_
            userinfo (AuthUser, optional): _description_. Defaults to {}.
            userargs (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: unknow containerengine value {containerengine}

        Returns:
            ODAppInstanceStatus: oc.od.appinstancestatus.ODAppInstanceStatus
        """
        self.logger.debug('')
        assert isinstance(myDesktop, ODDesktop),f"desktop has invalid type {type(myDesktop)}"
        assert isinstance(app,       dict),     f"app has invalid type {type(app)}"
        assert isinstance(authinfo,  AuthInfo), f"authinfo has invalid type {type(authinfo)}"
        # read the container enigne specific value from app properties
        containerengine = app.get('containerengine', 'ephemeral_container' )
        if containerengine not in self.appinstance_classes.keys():
            raise ValueError( f"unknow containerengine value {containerengine} must be defined in {list(self.appinstance_classes.keys())}")
        self.logger.debug(f"createappinstance containerengine={containerengine}")
        appinstance_class = self.appinstance_classes.get(containerengine)
        self.logger.debug(f"createappinstance appinstance_class={appinstance_class}")
        appinstance = appinstance_class(self)
        self.logger.debug(f"createappinstance containerengine={containerengine} type={appinstance.type}")
        appinstancestatus = appinstance.create(myDesktop, app, authinfo, userinfo, userargs, **kwargs )
        self.logger.debug(f"createappinstance appinstancestatus={appinstancestatus}")
        return appinstancestatus


    def labelfilter2str( self, labelfilter )->str:
        """labelfilter2str
            convert a dict filter to str

        Args:
            labelfilter (dict or str): labelfilter     
    
        Returns:
            str: labelfilter string formated
        """
        label_selector = ''
        if isinstance( labelfilter, dict ):
            for k in labelfilter:
                if len( label_selector ) > 0:
                    label_selector += ','
                label_selector += f"{k}={labelfilter[k]}"
        elif isinstance(labelfilter, str ):
            label_selector = labelfilter

        return label_selector

    def get_label_nodeselector( self )->str:
        """get_label_nodeselector
            convert a dict filter as string
        Returns:
            str: nodeselector str label filter
        """
        label_selector = self.labelfilter2str( oc.od.settings.desktop.get('nodeselector') )
        return label_selector

    def pullimage_on_all_nodes(self, app:dict):
        """pullimage_on_all_nodes
            pullimage app to all nodes
        Args:
            app (dict): app

        Returns:
            None
        """
        self.logger.info('')
        bReturn = True # default value 
        nodeselector = oc.od.settings.desktop.get('nodeselector')
        if isinstance( nodeselector, dict ):
            # convert dict as filter str
            label_selector = self.get_label_nodeselector()
            self.logger.info('list_node label_selector={label_selector}')

            # Check if we can call list_node
            # if the pyos_service account has ClusterRole
            listnode = None
            try:
                # query nodes
                listnode = self.kubeapi.list_node(label_selector=label_selector)
                self.logger.info(f"pulling image on nodelist={listnode}")
            except Exception as e:
                self.logger.warning( f"Can not get list of nodes. {e}, service account can not get nodelist, check RoleBinding and ClusterRoleBinding" )

            if isinstance( listnode, V1NodeList ) and len(listnode.items) > 0:
                for node in listnode.items :
                    if isinstance( node, V1Node): 
                        self.logger.debug( f"pulling image on node={node.metadata.name}")
                        pull = self.pullimage( app, node.metadata.name )
                        bReturn = pull and bReturn # return False if one error occurs
                    else:
                        self.logger.error( f"skipping bad entry in nodelist {node}")
            else:
                # fallback if no list node 
                self.logger.warning( f"pullimage on default nodeselector, no node list")
                pull = self.pullimage( app )
                bReturn = pull and bReturn # return False if one error occurs
        else:
            pull = self.pullimage( app )
            bReturn = pull and bReturn # return False if one error occurs

        return bReturn


    def pullimage(self, app:dict, nodename:str=None )->bool:
        """pullimage
            pull on image by creating a pod with 
            'imagePullPolicy': 'Always'
            on a specifici nodename
            if nodename is None, use the default nodeSelector
        Args:
            app (dict): application dict
            nodename (str, optional):node name to pull image. Defaults to None.

        Returns:
            bool: True if the pod has been created
        """
        assert_type( app, dict )
        self.logger.debug('')
        self.logger.info(f"pull by creating pod image={app['name']} on nodename={nodename}")
        self.logger.info(f"app unique id {app.get('_id')}")


        bReturn = False
        h = hashlib.new('sha256')
        h.update( str(app).encode() )
        digest = h.hexdigest()
        if isinstance( nodename, str):
            id = nodename + '_' + str( digest )
        else:
            id = 'localhost_' + str( digest )
        _containername = 'pull_' + oc.auth.namedlib.normalize_imagename( app['name'] + '_' + id )
        podname =  oc.auth.namedlib.normalize_name_dnsname( _containername )
        self.logger.debug( f"pullimage define podname={podname}" )

        '''
        # check if a running podname is already exist
        try:
            pod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=podname)
            if isinstance( pod, V1Pod ):
                self.logger.info( f"podname={podname} already exists")
                return pod
        except client.exceptions.ApiException as e:
            # Pod does not exist
            if e.status == 404:
                # Pod does not exist
                pass
            else:
                self.logger.error( e )

        except Exception as e:
            self.logger.error( e )
        '''
        labels = { 'type': self.pod_application_pull }

        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': podname,
                'namespace': self.namespace,
                'labels': labels
            },
            'spec': {
                'automountServiceAccountToken': False,  # disable service account inside pod
                'restartPolicy' : 'Never',
                'terminationGracePeriodSeconds': 0,  # Time to wait before moving from a TERM signal to the pod's main process to a KILL signal.'
                'containers':[ {   
                    'name': podname,
                    # When imagePullSecrets hasn’t been set, 
                    # the secrets of the default service account in the current namespace is used instead. 
                    # If those aren’t defined either, default or no credentials are used
                    'imagePullSecrets': oc.od.settings.desktop_pod.get(self.pod_application,{}).get('imagePullSecrets'),
                    'imagePullPolicy': 'Always',
                    'image': app['id'],
                    'command': ['/bin/sleep'],
                    'args': [ '42' ]
                } ]
            }
        }

        # set nodeName or nodeSelector
        if isinstance( nodename, str):
            # use nodeName if set
            pod_manifest['spec']['nodeName'] = nodename
        else:
            # use config nodeSelector
            pod_manifest['spec']['nodeSelector'] = oc.od.settings.desktop.get('nodeselector')

        self.logger.debug( f"pullimage create pod {pod_manifest}")

        pod = None
        try:
            pod = self.kubeapi.create_namespaced_pod(namespace=self.namespace,body=pod_manifest )
            if isinstance(pod, V1Pod ):
                bReturn = True
                self.logger.info( f"create_namespaced_pod pull image ask to run on node {pod.spec.node_name}" )
            else:
                self.logger.error( f"error in pulimage failed to create pod {podname}")
        except client.exceptions.ApiException as e:
             self.logger.error( e )
        except Exception as e:
            self.logger.error( e )

        return bReturn

    def alwaysgetPosixAccountUser(self, authinfo:AuthInfo, userinfo:AuthUser ) -> dict :
        """alwaysgetPosixAccountUser

        Args:
            userinfo (AuthUser): auth user info

        Returns:
            dict: posic account dict 
        """
        if not userinfo.isPosixAccount():
            # try to read a posix account from secret
            self.logger.debug('build a posixaccount secret trying')
            posixsecret = oc.od.secret.ODSecretPosixAccount( namespace=self.namespace, kubeapi=self.kubeapi )
            self.logger.debug('read the posixaccount secret trying')
            posixaccount = posixsecret.read_alldata( authinfo, userinfo )
            if not isinstance( posixaccount, dict):
                self.logger.debug('posixaccount does not exist use localaccount default')
                localaccount = oc.od.secret.ODSecretLocalAccount( namespace=self.namespace, kubeapi=self.kubeapi )
                self.logger.debug('read the localaccount secret')
                localaccount_data = localaccount.read_alldata( authinfo, userinfo )
                posixaccount = AuthUser.getPosixAccountfromlocalAccount(localaccount_data)
                userinfo['posix'] = posixaccount
            else:
                self.logger.debug('posixaccount reuse cached secret data')
                userinfo['posix'] = posixaccount
        else:
            self.logger.debug('posixaccount already decoded use userinfo dict')
            posixaccount = userinfo.getPosixAccount()

        return posixaccount


    def updateChevronDictWithmixedData( self, d, mixeddata:dict):
        if isinstance( d, dict):
            for k in d.keys():
                d[k] = self.updateChevronDictWithmixedData( d[k], mixeddata)
            return d
        if isinstance( d, list):
            for i in range(len(d)):
                d[i] = self.updateChevronDictWithmixedData( d[i], mixeddata)
            return d
        if isinstance( d, str):
            return chevron.render( d, mixeddata )
        else:
            return d

    def chevronWithUserInfo( self, list_data:list, authinfo: AuthInfo, userinfo:AuthUser ) -> list:
        """chevronWithUserInfo

            replace uidNumber and gidNumber by posix account values
            chevron update command 
            'command': [ 'sh', '-c',  'chown {{ uidNumber }}:{{ gidNumber }} ~' ] 
            after chevron
            'command': [ 'sh', '-c',  'chown 1234:5432 ~' ] 
            return list [ 'sh', '-c',  'chown 1234:5432 ~' ] 
        Args:
            currentcontainertype (str): 'init'
            userinfo (AuthUser): AuthUser

        Returns:
            list: command line updated
        """
        list_command = list_data
        if isinstance( list_command, list ):
            new_list_command = []
            posixuser = self.alwaysgetPosixAccountUser( authinfo, userinfo )
            for command in list_command:
                new_command  = chevron.render( command, posixuser )
                new_list_command.append( new_command )
            list_command = new_list_command
        return list_command


    def updateSecurityContextWithUserInfo( self, currentcontainertype:str, authinfo:AuthInfo, userinfo:AuthUser ) -> dict:
        """updateSecurityContextWithUserInfo

        Args:
            currentcontainertype (str): type of container
            userinfo (AuthUser): userinfo

        Returns:
            dict: a securityContext dict with { 'runAsUser': UID , 'runAsGroup': GID } or None
        """
        securityContext = None
        securityContextConfig = oc.od.settings.desktop_pod.get(currentcontainertype, {}).get( 'securityContext')
        if isinstance( securityContextConfig, dict):
            securityContext = copy.deepcopy(securityContextConfig)
            runAsUser  = securityContext.get('runAsUser')
            runAsGroup = securityContext.get('runAsGroup')
            supplementalGroups = securityContext.get('supplementalGroups')
            posixuser = self.alwaysgetPosixAccountUser( authinfo, userinfo )

            # replace 'runAsUser' if exist in configuration file
            if isinstance( runAsUser, str ): 
                securityContext['runAsUser']  = int( chevron.render( runAsUser, posixuser ) )
            
            # replace 'runAsGroup' if exist in configuration file
            if isinstance( runAsGroup, str ): 
                securityContext['runAsGroup'] = int( chevron.render( runAsGroup, posixuser ) )
            
            if securityContext.get('supplementalGroups'):
                # add 'supplementalGroups' if exist in configuration file
                # and posixuser.get('groups') is a list with element
                # add 'supplementalGroups' if exist in configuration file
                if isinstance( supplementalGroups, list ):
                    for i in range(0,len(supplementalGroups)):
                        # Replace  '{{ supplementalGroups }}' by the posic groups
                        if supplementalGroups[i] == '{{ supplementalGroups }}':
                            del supplementalGroups[i] 
                            posixuser_supplementalGroups =  AuthUser.mksupplementalGroups( posixuser )
                            if isinstance( posixuser_supplementalGroups, list ):
                                for posixuser_supplementalGroup in posixuser_supplementalGroups:
                                    supplementalGroups.append(posixuser_supplementalGroup)
                            break
                else:
                    del securityContext['supplementalGroups']

        return securityContext

    def getimagecontainerfromauthlabels( self, currentcontainertype:str, authinfo:AuthInfo )->str:
        """getimagecontainerfromauthlabels
            return the name of image to use for a container

        Args:
            currentcontainertype (str): type of container
            authinfo (AuthInfo): authinfo

        Raises:
            ValueError: invalid image type

        Returns:
            str: name of the container image
        """
        assert_type(currentcontainertype, str)
        assert_type(authinfo, AuthInfo)

        imageforcurrentcontainertype = None
        image = oc.od.settings.desktop_pod.get(currentcontainertype,{}).get('image')
        if isinstance( image, str):
            imageforcurrentcontainertype = image
        elif isinstance( image, dict ):
            imageforcurrentcontainertype = image.get('default')
            labels = authinfo.get_labels()
            for k,v in labels.items():
                if image.get(k):
                    imageforcurrentcontainertype=v
                    break
        
        if not isinstance(imageforcurrentcontainertype, str):
            raise ValueError( f"invalid image type for {currentcontainertype} type={type(image)} data={image}")

        return imageforcurrentcontainertype


    @staticmethod
    def appendkubernetesfieldref(envlist:list)->None:
        """appendkubernetesfieldref
            add NODE_NAME POD_NAME POD_NAMESPACE POD_IP
            as
            env:
                - name: NODE_NAME
                    valueFrom:
                    fieldRef:
                        fieldPath: spec.nodeName
                - name: POD_NAME
                    valueFrom:
                    fieldRef:
                        fieldPath: metadata.name
                - name: POD_NAMESPACE
                    valueFrom:
                    fieldRef:
                        fieldPath: metadata.namespace
                - name: POD_IP
                    valueFrom:
                    fieldRef:
                        fieldPath: status.podIP
        Args:
            envlist (list): env list
        """
        assert isinstance(envlist, list),  f"env has invalid type {type(envlist)}, list is expected"
        # kubernetes env formated dict
        envlist.append( { 'name': 'NODE_NAME',      'valueFrom': { 'fieldRef': { 'fieldPath':'spec.nodeName' } } } )
        envlist.append( { 'name': 'POD_NAME',       'valueFrom': { 'fieldRef': { 'fieldPath':'metadata.name' } } } )
        envlist.append( { 'name': 'POD_NAMESPACE',  'valueFrom': { 'fieldRef': { 'fieldPath':'metadata.namespace' } } } )
        envlist.append( { 'name': 'POD_IP',         'valueFrom': { 'fieldRef': { 'fieldPath':'status.podIP' } } } )

    def getPodStartedMessage(self, containernameprefix:str, myPod:V1Pod, myEvent:CoreV1Event )->str:
        """getPodStartedMessage

        Args:
            containernameprefix (str): containername
            myPod (V1Pod): pod
            myEvent (CoreV1Event): event

        Returns:
            str: started message

        """

        assert isinstance(containernameprefix, str),  f"env has invalid type {type(containernameprefix)}, str is expected"
        assert isinstance(myPod, V1Pod),  f"myPod has invalid type {type(myPod)}, V1Pod is expected"

        startedmsg = f"b.{myPod.status.phase.lower()}"
        if isinstance( myEvent, CoreV1Event):
            # myEvent.count can be None if something goes wrong
            if isinstance(myEvent.count, int) and myEvent.count > 1 :
                startedmsg = f"b.{myPod.status.phase.lower()} {myEvent.count}"

        c = self.getcontainerfromPod( containernameprefix, myPod )
        if isinstance( c, V1ContainerStatus):
            startedmsg += f": {c.name} "
            if  c.started is False: 
                startedmsg += "is starting"
            elif c.started is True and c.ready is False:
                startedmsg += "is started"
            elif c.started is True and c.ready is True:
                startedmsg += "is ready"
        return startedmsg

    @staticmethod
    def envdict_to_kuberneteslist(env:dict)->list:
        """ envdict_to_kuberneteslist
            convert env dictionnary to env list format for kubernes
            env = { 'KEY': 'VALUE' }
            return a list of dict key/valye
            envlist = [ { 'name': 'KEY', 'value': 'VALUE' } ]

        Args:
            env (dict): env var dict 

        Returns:
            list: list of { 'name': k, 'value': str(value) }
        """
        assert isinstance(env, dict),  f"env has invalid type {type(env)}, dict is expected"
        envlist = []
        for k, v in env.items():
            # need to convert v as str : kubernetes supports ONLY string type to env value
            envlist.append( { 'name': k, 'value': str(v) } )
        return envlist

    @staticmethod
    def expandchevron_envdict( env: dict, posixuser:dict )->None:
        """expandchevron_envdict
            replace in chevron key
            used for desktop.envlocal 
            env :  {
                'UID'                   : '{{ uidNumber }}',
                'GID'                   : '{{ gidNumber }}',
                'LOGNAME'               : '{{ uid }}'
            }
            by posix account value or default user account values
            example
            env :  {
                'UID'                   : '1024',
                'GID'                   : '2045',
                'LOGNAME'               : 'toto'
            }
        Args:
            env (dict): env var dict 
            posixuser (dict): posix accont dict 
        """
        assert isinstance(env, dict),  f"env has invalid type {type(env)}, dict is expected"
        assert isinstance(posixuser, dict),  f"posixuser has invalid type {type(posixuser)}, dict is expected"
        for k, v in env.items():
            if isinstance( v, str ):
                try:
                    new_value = chevron.render( v, posixuser )
                    env[k] = new_value 
                except Exception:
                    pass
    
    def get_ownerReferences( self, secrets:dict )->list:
        ownerReferences = []
        for name in secrets.keys():
            ownerReference = { 
                'kind': 'Secret', 
                'name': name, 
                'controller': False, 
                'apiVersion': 'v1', 
                'uid': secrets[name].get('uid') 
            }
            ownerReferences.append( ownerReference )
        return ownerReferences   

    def get_executeclasse( self, authinfo:AuthInfo, userinfo:AuthUser, executeclassname:str=None)->dict:
        """get_executeclasse

            return a dict like { 
                'nodeSelector':None, 
                'resources':{
                'requests':{'memory':"256Mi",'cpu':"100m"},
                'limits':  {'memory':"1Gi",'cpu':"1000m"} 
            } 


        Args:
            authinfo (AuthInfo): AuthInfo
            userinfo (AuthUser): AuthUser
            executeclassname (str, optional): name of the executeclass. Defaults to None.

        Returns:
            dict: dict executeclasse
        """
        self.logger.debug('')
        executeclass = None
        
        # if executeclassname is set, read it
        if isinstance( executeclassname, str ):
            executeclass = oc.od.settings.executeclasses.get(executeclassname)

        if not isinstance( executeclass, dict ):
            tagexecuteclassname = authinfo.get_labels().get('executeclassname','default')
            if isinstance( tagexecuteclassname, str ) and \
               isinstance( oc.od.settings.executeclasses.get(tagexecuteclassname), dict) :
                    executeclass=oc.od.settings.executeclasses.get(tagexecuteclassname)

        if isinstance( executeclass, dict ):
            if executeclass.get('nodeSelector') is None:
                executeclass['nodeSelector'] = oc.od.settings.desktop.get('nodeselector')

        #
        self.logger.debug(f"executeclass={executeclass}")
        return executeclass


    def get_resources( self, currentcontainertype:str, executeclass:dict )->dict:
        self.logger.debug('')
        resources = {} # resource is a always a dict 
        currentcontainertype_ressources = oc.od.settings.desktop_pod[currentcontainertype].get('resources')
        if isinstance( currentcontainertype_ressources, dict ):
            resources.update(currentcontainertype_ressources)

        executeclass_ressources = executeclass.get('resources')
        if isinstance( executeclass_ressources, dict ):
            resources.update(executeclass_ressources)
 
        self.logger.debug(f" get_resources return {resources}")
        return resources

    def read_pod_resources( self, pod_name:str)->dict:
        """read_pod_resources 
            read resource of graphicalcontainer container

        Args:
            pod_name (str): name of pod

        Returns:
            dict: resource of graphicalcontainer container, None if failed
            example {'limits': {'cpu': '1200m', 'memory': '6Gi'}, 'requests': {'cpu': '300m', 'memory': '56Mi'}}
        """
        resources=None
        # read pod 
        self.logger.debug('read_namespaced_pod creating' )  
        try:
            myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=pod_name)
            if isinstance(myPod, V1Pod ):
                c = self.getcontainerSpecfromPod( self.graphicalcontainernameprefix, myPod )
                if isinstance( c, V1Container ) and isinstance( c.resources, V1ResourceRequirements ):
                    resources = c.resources.to_dict()
        except ApiException as e:
            pass

        return resources

    def notify_user( self, myDesktop:ODDesktop, method:str, data:dict )->bool:
        """notify_user

        Args:
            myDesktop (ODDesktop): ODDesktop
            method (str): string value can be [ 'ocrun', 'logout', 'container', 'download' ] 
            user pod: 
            from abcdesktopio/oc.user container image 
            source code /composer/node/broadcast-service/broadcast-service.js  
            web front:
            call containerNotificationInfo in webModules files js/launcher.js   
            data (dict): data description
            data = {    'type':  'error' 'warning' 'info' 'deny' 'place'
                        'message':  app.get('name'), 
                        'name':     app.get('name'),
                        'icondata': app.get('icondata'),
                        'icon':     app.get('icon'),
                        'image':    app.get('id'),
                        'launch':   app.get('launch')
            }
        """
        self.logger.debug(locals())
        bReturn = False
        if not isinstance( myDesktop, ODDesktop):
            return bReturn
        assert_type( method, str )
        assert_type( data, dict )
        command = [ 'node',  '/composer/node/occall/occall.js', method, json.dumps(data) ]
        result = self.execwaitincontainer( desktop=myDesktop, command=command)
        if isinstance( result, dict):
            bReturn = result.get( 'ExitCode', 1)
        return bReturn


    def addcontainertopod( self, authinfo:AuthInfo, userinfo:AuthUser, currentcontainertype:str, myuuid:str, envlist:list, list_volumeMounts:list, workingdir:str=None, command:str=None ):
        assert_type( authinfo, AuthInfo)
        assert_type( userinfo, AuthUser)
        assert_type( currentcontainertype, str)
        assert_type( myuuid, str)
        assert_type( list_volumeMounts, list )

        self.logger.debug( f"pod container adding {currentcontainertype} to {myuuid}" )
        securityContext = self.updateSecurityContextWithUserInfo( currentcontainertype, authinfo, userinfo )
        image = self.getimagecontainerfromauthlabels( currentcontainertype, authinfo )
        container = { 
            'name': self.get_containername( authinfo, userinfo, currentcontainertype, myuuid ),
            'imagePullPolicy': oc.od.settings.desktop_pod[currentcontainertype].get('imagePullPolicy', 'IfNotPresent' ),
            'image': image,                             
            'env': envlist,
            'volumeMounts': list_volumeMounts,
            'resources': oc.od.settings.desktop_pod[currentcontainertype].get('resources')                      
        }
        if isinstance( workingdir, str):
            container['workingDir'] = workingdir
        if isinstance( command, list):
            container['command'] = command
        if isinstance( oc.od.settings.desktop_pod[currentcontainertype].get('imagePullSecrets'), dict):
            container['imagePullSecrets'] = oc.od.settings.desktop_pod[currentcontainertype].get('imagePullSecrets')
        if isinstance( securityContext, dict ) :
            container['securityContext'] = securityContext

        return container

    def create_vnc_secret( self, authinfo:AuthInfo, userinfo:AuthUser ):
        """create_vnc_secret
            create a random vnc password for a new desktop
            add the vnc password as kubernetes secret

        Args:
            authinfo (AuthInfo): AuthInfo
            userinfo (AuthUser): AuthUser

        Raises:
            ODAPIError: vnc kubernetes secret create failed 
        """
        self.logger.debug('create vnc password as kubernetes secret')
        plaintext_vnc_password = ODVncPassword().getplain()
        vnc_secret = oc.od.secret.ODSecretVNC( self.namespace, self.kubeapi )
        vnc_secret_password = vnc_secret.create( authinfo=authinfo, userinfo=userinfo, data={ 'password' : plaintext_vnc_password } )
        if not isinstance( vnc_secret_password, V1Secret ):
            raise ODAPIError( f"create vnc kubernetes secret {plaintext_vnc_password} failed" )
        self.logger.debug(f"vnc kubernetes secret set to {plaintext_vnc_password}")


    def buildinitcommand(self, authinfo:AuthInfo, userinfo:AuthUser, list_pod_allvolumes:list, list_pod_allvolumeMounts:list )-> list :
        """buildinitcommand
            buildinitcommand to fix volume ownership
            chevronWithUserInfo to replace {} values

        Args:
            authinfo (AuthInfo): AuthInfo
            userinfo (AuthUser): AuthUser
            list_pod_allvolumes (list): list of volumes
            list_pod_allvolumeMounts (list): list of volumeMounts

        Returns:
            list: init command list of str
        """
        self.logger.debug('buildinitcommand to fix volume ownership')
        assert_type( list_pod_allvolumes, list)
        assert_type( list_pod_allvolumeMounts, list)
        default_command_list = [ 'sh', '-c',  'chown {{ uidNumber }}:{{ gidNumber }} ~ || true' ] 
        command_list = oc.od.settings.desktop_pod.get('init', {} ).get('command', default_command_list )
        assert_type( command_list, list )
        chown_command = 'chown {{ uidNumber }}:{{ gidNumber }}'
        # the command to update is the last_element in the list
        command = command_list[-1] + ' '
        for volume in list_pod_allvolumes:
            assert_type( volume, dict )
            if volume.get('persistentVolumeClaim'):
                volume_name = volume.get('name')
                assert_type( volume_name, str )
                for volumemount in list_pod_allvolumeMounts:
                    assert_type( volumemount, dict )
                    if volumemount.get('name') == volume_name:
                        mountPath = volumemount.get('mountPath')
                        volume_chown_command = f" && {chown_command} {mountPath} || true"
                        command = command + volume_chown_command
        command_list[-1] = command
        chevron_command_list = self.chevronWithUserInfo( command_list, authinfo, userinfo )
        return chevron_command_list

    def getPodIPAddress( self, pod_name:str )->str:
        """getPodIPAddress
            return the IP Address of the pod name or None
        Args:
            pod_name (str): name of pod

        Returns:
            str: IP Address of the pod, 
            None if Failed or empty value
        """
        IPAddress = None
        try:
            myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=pod_name)
            if isinstance( myPod, V1Pod ):
                if isinstance( myPod.status, V1PodStatus ):
                    #  myPod.status.pod_ip : Empty if not yet allocated.
                    if isinstance( myPod.status.pod_ip, str) and len(myPod.status.pod_ip) > 0:     
                        IPAddress = myPod.status.pod_ip
        except Exception as e:
            self.logger.error( e )
        self.logger.debug( f"pod_IPAddress is {IPAddress}" ) 
        return IPAddress
        

    def createdesktop(self, authinfo:AuthInfo, userinfo:AuthUser, **kwargs)-> ODDesktop :
        """createdesktop
            create the user pod 

        Args:
            authinfo (AuthInfo): authinfo
            userinfo (AuthUser): userinfo

        Raises:
            ValueError: _description_

        Returns:
            ODDesktop: ( ODDesktop | str ) desktop object or str  
        """
        self.logger.debug('createdesktop start' )
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"

        myDesktop = None # default return object
        env = kwargs.get('env', {} )
        dry_run = kwargs.get('dry_run')

        # get the execute class if user has a executeclassname tag
        executeclasse = self.get_executeclasse( authinfo, userinfo )

        # add a new VNC Password as kubernetes secret
        self.create_vnc_secret( authinfo=authinfo, userinfo=userinfo )

        # create ENV var for pod 
        # XAUTH key
        self.logger.debug('env creating')
        env[ 'XAUTH_KEY' ] = self.generate_xauthkey() # generate XAUTH_KEY
        env[ 'PULSEAUDIO_COOKIE' ] = self.generate_pulseaudiocookie()   # generate PULSEAUDIO cookie
        env[ 'BROADCAST_COOKIE' ] = self.generate_broadcastcookie()     # generate BROADCAST cookie 
        env[ 'HOME'] = self.get_user_homedirectory(authinfo, userinfo)  # read HOME DIR 
        env[ 'USER' ] = userinfo.userid         # add USER
        env[ 'LOGNAME' ] = userinfo.userid      # add LOGNAME 
        env[ 'USERNAME' ] = userinfo.userid     # add USERNAME 
        env[ 'LOCALACCOUNT_PATH'] = oc.od.settings.desktop['secretslocalaccount']
        env[ 'PULSE_SERVER' ] = 'unix:/tmp/.pulse.sock' # for embedded applications
        self.logger.debug( f"HOME={env[ 'HOME']}")
        self.logger.debug('env created')

        # create labels for pod
        self.logger.debug('labels creating')
        # build label dictionnary
        labels = { 
            'abcdesktop/role': self.abcdesktop_role_desktop,
            'access_provider': authinfo.provider,
            'access_providertype': authinfo.providertype,
            'access_userid': userinfo.userid,
            'access_username': self.get_labelvalue(userinfo.name),
            'domain': self.endpoint_domain,
            'netpol/ocuser': 'true',
            'xauthkey': env[ 'XAUTH_KEY' ], 
            'pulseaudio_cookie': env[ 'PULSEAUDIO_COOKIE' ],
            'broadcast_cookie': env[ 'BROADCAST_COOKIE' ]
        }

        # add authinfo labels and env 
        # could also use downward-api https://kubernetes.io/docs/concepts/workloads/pods/downward-api/
        for k,v in authinfo.get_labels().items():
            abcdesktopvarenvname = oc.od.settings.ENV_PREFIX_LABEL_NAME + k.lower()
            env[ abcdesktopvarenvname ] = v
            labels[k] = v

        for currentcontainertype in self.nameprefixdict.keys() :
            if self.isenablecontainerinpod( authinfo, currentcontainertype ):
                abcdesktopvarenvname = oc.od.settings.ENV_PREFIX_SERVICE_NAME + currentcontainertype
                env[ abcdesktopvarenvname ] = 'enabled'
    
        # create a desktop
        # set value as default type x11servertype
        labels['type'] = self.x11servertype
        kwargs['type'] = self.x11servertype
        self.logger.debug('labels created')

        # create pod name
        # pod uuid suffix
        myuuid = oc.lib.uuid_digits()
        pod_name = self.get_podname( authinfo, userinfo, myuuid ) 
        self.logger.debug( f"pod name is {pod_name}" )

        self.logger.debug('envlist creating')
        posixuser = self.alwaysgetPosixAccountUser( authinfo, userinfo )
        # replace  'UID' : '{{ uidNumber }}' by value 
        # expanded chevron value to the user value
        ODOrchestratorKubernetes.expandchevron_envdict( env, posixuser )
        # convert env dictionnary to env list format for kubernetes
        envlist = ODOrchestratorKubernetes.envdict_to_kuberneteslist( env )
        ODOrchestratorKubernetes.appendkubernetesfieldref( envlist )
        self.logger.debug('envlist created')

        # look for desktop rules
        # apply network rules 
        self.logger.debug('rules creating')   
        rules = oc.od.settings.desktop['policies'].get('rules')
        self.logger.debug(f"policies.rules is defined {rules}")
        network_config = ODOrchestrator.applyappinstancerules_network( authinfo, rules )
        fillednetworkconfig = self.filldictcontextvalue(
            authinfo=authinfo, 
            userinfo=userinfo, 
            desktop=None, 
            network_config=copy.deepcopy(network_config), 
            network_name = None, 
            appinstance_id = None 
        )
        self.logger.debug('rules created')

        # new step
        self.on_desktoplaunchprogress('b.Building data storage for your desktop')

        # get secrets_requirement for 'graphical'
        currentcontainertype = 'graphical'
        secrets_requirement = oc.od.settings.desktop_pod.get(currentcontainertype,{}).get('secrets_requirement')
        self.logger.debug(f"secrets_requirement={secrets_requirement} for currentcontainertype={currentcontainertype}")

        # ownerReferences = self.get_ownerReferences(mysecretdict)

        self.logger.debug('volumes creating')
        shareProcessNamespace = oc.od.settings.desktop_pod.get('spec',{}).get('shareProcessNamespace', False)
        tolerations = oc.od.settings.desktop_pod.get('spec',{}).get('tolerations')
        kwargs['shareProcessNamespace'] = shareProcessNamespace
        shareProcessMemory = oc.od.settings.desktop_pod.get('spec',{}).get('shareProcessMemory', False)
        kwargs['shareProcessMemory'] = shareProcessMemory

        # all volumes and secrets
        (pod_allvolumes, pod_allvolumeMounts) = self.build_volumes( authinfo, userinfo, volume_type='pod_desktop', secrets_requirement=['all'], rules=rules,  **kwargs)
        list_pod_allvolumes = list( pod_allvolumes.values() )
        list_pod_allvolumeMounts = list( pod_allvolumeMounts.values() )

        # graphical volumes
        (volumes, volumeMounts) = self.build_volumes( authinfo, userinfo, volume_type='pod_desktop', secrets_requirement=secrets_requirement, rules=rules,  **kwargs)
        list_volumeMounts = list( volumeMounts.values() )
        self.logger.info( 'volumes=%s', volumes.values() )
        self.logger.info( 'volumeMounts=%s', volumeMounts.values() )
        self.logger.debug('volumes created')


        self.logger.debug('websocketrouting creating')
        # check if we have to build X509 certificat
        # need to build certificat if websocketrouting us bridge 
        # bridge can be a L2/L3 level like ipvlan, macvlan
        # use multus config
        websocketrouting = oc.od.settings.websocketrouting # set defautl value, can be overwritten 
        websocketroute = None
        if  fillednetworkconfig.get( 'websocketrouting' ) == 'bridge' :
            # no filter if container ip addr use a bridged network interface
            envlist.append( { 'name': 'DISABLE_REMOTEIP_FILTERING', 'value': 'enabled' })

            # if we need to request an X509 certificat on the fly
            external_dnsconfig = fillednetworkconfig.get( 'external_dns' )
            if  type( external_dnsconfig ) is dict and \
                type( external_dnsconfig.get( 'domain' ))   is str and \
                type( external_dnsconfig.get( 'hostname' )) is str :
                websocketrouting = fillednetworkconfig.get( 'websocketrouting' )
                websocketroute = external_dnsconfig.get( 'hostname' ) + '.' + external_dnsconfig.get( 'domain' )
                envlist.append( { 'name': 'USE_CERTBOT_CERTONLY',        'value': 'enabled' } )
                envlist.append( { 'name': 'EXTERNAL_DESKTOP_HOSTNAME',   'value': external_dnsconfig.get( 'hostname' ) } )
                envlist.append( { 'name': 'EXTERNAL_DESKTOP_DOMAIN',     'value': external_dnsconfig.get( 'domain' ) } )

                labels['websocketrouting']  = websocketrouting
                labels['websocketroute']    = websocketroute
        self.logger.debug('websocketrouting created')

        initContainers = []
        currentcontainertype = 'init'
        if  self.isenablecontainerinpod( authinfo, currentcontainertype ):
            # build the init command 
            command = self.buildinitcommand( authinfo, userinfo, list_pod_allvolumes, list_pod_allvolumeMounts )
            self.logger.debug(f"init command={command}")
            init_container = self.addcontainertopod( 
                authinfo=authinfo, 
                userinfo=userinfo, 
                currentcontainertype=currentcontainertype, 
                command=command,
                myuuid=myuuid,
                envlist=envlist,
                list_volumeMounts=list_pod_allvolumeMounts
            )
            initContainers.append( init_container )
            self.logger.debug( f"pod container added {currentcontainertype}" )


        # default empty dict annotations
        annotations = {}
        # add last login datetime to annotations for garbage collector
        annotations.update( self.get_annotations_lastlogin_datetime() )
        # Check if a network annotations exists 
        network_annotations = network_config.get( 'annotations' )
        if isinstance( network_annotations, dict):
            annotations.update( network_annotations )

        # set default dns configuration 
        dnspolicy = oc.od.settings.desktop['dnspolicy']
        dnsconfig = oc.od.settings.desktop['dnsconfig']

        # overwrite default dns config by rules
        if type(network_config.get('internal_dns')) is dict:
            dnspolicy = 'None'
            dnsconfig = network_config.get('internal_dns')

        for currentcontainertype in oc.od.settings.desktop_pod.keys() :
            if self.isenablecontainerinpod( authinfo, currentcontainertype ):
                label_servicename = 'service_' + currentcontainertype
                # tcpport is a number, convert it as str for a label value
                label_value = str( oc.od.settings.desktop_pod[currentcontainertype].get('tcpport','enabled') )
                labels.update( { label_servicename: label_value } )

        specssecurityContext = self.updateSecurityContextWithUserInfo( 
            currentcontainertype='spec', 
            authinfo=authinfo, 
            userinfo=userinfo )

        # define pod_manifest
        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': pod_name,
                'namespace': self.namespace,
                'labels': labels,
                'annotations': annotations
                # 'ownerReferences': ownerReferences
            },
            'spec': {
                'dnsPolicy' : dnspolicy,
                'dnsConfig' : dnsconfig,
                'automountServiceAccountToken': False,  # disable service account inside pod
                'subdomain': self.endpoint_domain,
                'shareProcessNamespace': shareProcessNamespace,
                'volumes': list_pod_allvolumes,                    
                'nodeSelector': executeclasse.get('nodeSelector'), 
                'initContainers': initContainers,
                'securityContext': specssecurityContext,
                'tolerations': tolerations,
                'containers': []
            }
        }


        # Add graphical servives 
        currentcontainertype='graphical'
        if  self.isenablecontainerinpod( authinfo, currentcontainertype ):
            graphical_container = self.addcontainertopod( 
                authinfo=authinfo, 
                userinfo=userinfo, 
                currentcontainertype=currentcontainertype, 
                myuuid=myuuid,
                envlist=envlist,
                workingdir=env['HOME'],
                list_volumeMounts=list_volumeMounts
            )
            # by default remove anonymous home directory content at preStop 
            # or if oc.od.settings.desktop['removehomedirectory'] is True
            if oc.od.settings.desktop['removehomedirectory'] is True or authinfo.provider == 'anonymous':
                graphical_container['lifecycle'] = {  
                    'preStop': { 'exec': { 'command': oc.od.settings.desktop['prestopexeccommand'] } } 
                } 
                self.logger.debug(f"adding command graphical_container['lifecycle']={graphical_container['lifecycle']}")
            pod_manifest['spec']['containers'].append( graphical_container )
            self.logger.debug(f"pod container created {currentcontainertype}" )

        localaccount_volume_name = self.get_volumes_localaccount_name( authinfo=authinfo, userinfo=userinfo )
        assert isinstance(localaccount_volume_name, str),  f"localaccount_volume_name has invalid type {type(localaccount_volume_name)}"
        containers = {
            'printer':  { 'list_volumeMounts':  [ pod_allvolumeMounts.get('tmp') ] }, # printer uses tmp volume
            'sound':    { 'list_volumeMounts':  [ pod_allvolumeMounts.get(localaccount_volume_name), 
                                                  pod_allvolumeMounts.get('tmp'), 
                                                  pod_allvolumeMounts.get('home'), 
                                                  pod_allvolumeMounts.get('log') ] },
                                                  # sound uses tmp, home, log volumes
            'ssh':      { 'list_volumeMounts':  list_volumeMounts },        # ssh uses default user volumes
            'filer':    { 'list_volumeMounts':  list_volumeMounts },        # filter uses default user volumes
            'storage':  { 'list_volumeMounts':  list_pod_allvolumeMounts }, # storage uses default user volumes
            'rdp':      { 'list_volumeMounts':  [ pod_allvolumeMounts.get('x11socket') ]  } , # rdp uses default user volumes
            'x11overlay':  { 'list_volumeMounts': [ pod_allvolumeMounts.get(localaccount_volume_name), 
                                                    pod_allvolumeMounts.get('x11socket') ] } # x11overlay uses default user volumes
        }

        for currentcontainertype in containers.keys():
            if  self.isenablecontainerinpod( authinfo, currentcontainertype ):
                new_container = self.addcontainertopod( 
                    authinfo=authinfo, 
                    userinfo=userinfo, 
                    currentcontainertype=currentcontainertype, 
                    myuuid=myuuid,
                    envlist=envlist,
                    list_volumeMounts=containers[currentcontainertype].get('list_volumeMounts')
                )
                pod_manifest['spec']['containers'].append( new_container )
                self.logger.debug(f"container added {currentcontainertype} to pod {pod_name}")

        # we are ready to create our Pod 
        myDesktop = None
        self.on_desktoplaunchprogress('b.Creating your desktop')
        jsonpod_manifest = json.dumps( pod_manifest, indent=2 )
        self.logger.info( 'dump yaml %s', jsonpod_manifest )

        pod = None
        try:
            pod = self.kubeapi.create_namespaced_pod( namespace=self.namespace, body=pod_manifest, dry_run=dry_run)
        except ApiException as e:
            self.logger.error( e )
            msg=f"e.Create pod failed {e.reason} {e.body}"
            self.on_desktoplaunchprogress( msg )
            return msg
        except Exception as e:
            self.logger.error( e )
            msg=f"e.Create pod failed {e}"
            self.on_desktoplaunchprogress( msg )
            return msg

        if not isinstance(pod, V1Pod ):
            self.on_desktoplaunchprogress('e.Create pod failed.' )
            raise ValueError( f"Invalid create_namespaced_pod type return {type(pod)} V1Pod is expecting")

        # return json 
        if dry_run == 'All':
            return pod_manifest

        self.on_desktoplaunchprogress(f"b.Watching for events" )
        self.logger.debug('watch list_namespaced_event pod creating' )
        pulled_counter = 0 
        started_counter = 0 
        expected_containers_len = len( pod.spec.containers )
        self.logger.debug( f"expected_containers_len={expected_containers_len}")

        # watch list_namespaced_event
        w = watch.Watch()

        for event in w.stream(  self.kubeapi.list_namespaced_event, 
                                namespace=self.namespace, 
                                timeout_seconds=oc.od.settings.desktop['K8S_CREATE_POD_TIMEOUT_SECONDS'],
                                field_selector=f'involvedObject.name={pod_name}'):
            
            if not isinstance(event, dict ): continue # safe type test event is a dict
            if not isinstance(event.get('object'), CoreV1Event ): continue # safe type test event object is a CoreV1Event
            event_object = event.get('object')
            self.logger.debug(f"{event_object.type} reason={event_object.reason} message={event_object.message}")
            self.on_desktoplaunchprogress( f"b.{event_object.message}" )

            #
            # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Event.md
            # Type of this event (Normal, Warning), new types could be added in the future
            # 'Normal':  Information only and will not cause any problems
            # 'Warning': These events are to warn that something might go wrong

            if event_object.type == 'Warning':  # event Warning
                # something might goes wrong
                self.logger.error(f"{event_object.type} reason={event_object.reason} message={event_object.message}")
                w.stop()
                return f"{event_object.type} {event_object.reason} {event_object.message}"

            elif event_object.type == 'Normal': # event Normal

                if event_object.reason in [ 'Created', 'Pulling', 'Scheduled' ]:
                    continue # nothing to do

                # check reason, read 
                # https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/events/event.go
                # reason should be a short, machine understandable string that gives the reason for the transition 
                # into the object's current status.
                if event_object.reason == 'Pulled':
                    self.logger.debug( f"Event Pulled received pulled_counter={pulled_counter}")
                    pulled_counter = pulled_counter + 1
                    # if all images are pulled 
                    self.logger.debug( f"counter pulled_counter={pulled_counter} expected_containers_len={expected_containers_len}")
                    if pulled_counter >= expected_containers_len :
                        self.logger.debug( f"counter pulled_counter={pulled_counter} >= expected_containers_len={expected_containers_len}")
                        # pod_IPAddress = self.getPodIPAddress( pod.metadata.name )
                        # if isinstance( pod_IPAddress, str ):
                        #    self.logger.debug( f"{pod.metadata.name} has an ip address: {pod_IPAddress}")
                        #    self.on_desktoplaunchprogress(f"b.Your pod {pod.metadata.name} gets ip address {pod_IPAddress} from network plugin")
                        #    self.logger.debug( f"stop watching event list_namespaced_event for pod {pod.metadata.name} ")
                        w.stop()

                elif event_object.reason == 'Started':  
                    self.logger.debug( f"Event Started received started_counter={started_counter}")
                    started_counter = started_counter + 1    
                    self.logger.debug( f"counter started_counter={started_counter} expected_containers_len={expected_containers_len}")
                    #pod_IPAddress = self.getPodIPAddress( pod.metadata.name )
                    #if isinstance( pod_IPAddress, str ):
                    #    self.logger.debug( f"{pod.metadata.name} has an ip address: {pod_IPAddress}")
                    if started_counter >= expected_containers_len :
                        w.stop()
                else:
                    # log the events
                    self.logger.debug(f"{event_object.type} reason={event_object.reason} message={event_object.message}")
                    self.on_desktoplaunchprogress(f"b.Your pod gets event {event_object.message or event_object.reason}")
                    # fix for https://github.com/abcdesktopio/oc.user/issues/52
                    # this is not an error
                    w.stop()
                    # return  f"{event_object.reason} {event_object.message}"
                
            else: 
                # this event is not 'Normal' or 'Warning', unknow event received
                self.logger.error(f"UNMANAGED EVENT pod type {event_object.type}")
                w.stop()
        #
        # list_namespaced_event done
        #

        self.logger.debug( f"watch list_namespaced_event pod created {event_object.type}")
        self.logger.debug('watch list_namespaced_pod creating, waiting for pod quit Pending phase' )
        w = watch.Watch()                 
        for event in w.stream(  self.kubeapi.list_namespaced_pod, 
                                namespace=self.namespace, 
                                timeout_seconds=oc.od.settings.desktop['K8S_CREATE_POD_TIMEOUT_SECONDS'],
                                field_selector=f"metadata.name={pod_name}" ):   
            # event must be a dict, else continue
            if not isinstance(event,dict):
                self.logger.error( f"event type is {type( event )}, and should be a dict, skipping event")
                continue

            event_type = event.get('type')  # event dict must contain a type 
            pod_event = event.get('object') # event dict must contain a pod object 
            if not isinstance( pod_event, V1Pod ): continue  # if podevent type must be a V1Pod
            if not isinstance( pod_event.status, V1PodStatus ): continue
            #
            self.on_desktoplaunchprogress( f"b.Your {pod_event.kind.lower()} is {event_type.lower()}")
            self.logger.debug(f"The pod {pod_event.metadata.name} is in phase={pod_event.status.phase}" )
            #
            # from https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
            #
            # possible values for phase
            # Pending	The Pod has been accepted by the Kubernetes cluster, but one or more of the containers has not been set up and made ready to run. This includes time a Pod spends waiting to be scheduled as well as the time spent downloading container images over the network.
            # Running	The Pod has been bound to a node, and all of the containers have been created. At least one container is still running, or is in the process of starting or restarting.
            # Succeeded	All containers in the Pod have terminated in success, and will not be restarted.
            # Failed	All containers in the Pod have terminated, and at least one container has terminated in failure.
            # Unknown	For some reason the state of the Pod could not be obtained. This phase typically occurs due to an error in communicating with the node where the Pod should be running.
            if pod_event.status.phase == 'Pending' :
                self.on_desktoplaunchprogress( f"b.Your pod {pod_event.metadata.name} is {pod_event.status.phase}"  )
                continue
            elif pod_event.status.phase == 'Running' :
                startedmsg = self.getPodStartedMessage(self.graphicalcontainernameprefix, pod_event, event_object)
                self.on_desktoplaunchprogress( startedmsg )
                w.stop()
            elif pod_event.status.phase == 'Succeeded' or \
                 pod_event.status.phase == 'Failed' :
                # pod data object is complete, stop reading event
                # phase can be 'Running' 'Succeeded' 'Failed' 'Unknown'
                self.logger.debug(f"The pod {pod_event.metadata.name} is not in Pending phase, phase={pod_event.status.phase} stop watching" )
                w.stop()
            else:
                # pod_event.status.phase should be 'Unknow'
                self.logger.error(f"UNMANAGED CASE pod {pod_event.metadata.name} is in unmanaged phase {pod_event.status.phase}")
                self.logger.error(f"The pod {pod_event.metadata.name} is in phase={pod_event.status.phase} stop watching" )
                w.stop()

        self.logger.debug(f"watch list_namespaced_pod created, the pod is no more in Pending phase" )

        # read pod again
        self.logger.debug(f"read_namespaced_pod {pod_name} again" )
        myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=pod_name)   
        assert isinstance(myPod, V1Pod),  f"read_namespaced_pod returns type {type(myPod)} V1Pod is expected"
        assert isinstance(myPod.status, V1PodStatus), f"read_namespaced_pod returns pod.status type {type(myPod.status)} V1PodStatus is expected"
        self.logger.info( f"myPod.metadata.name {myPod.metadata.name} is {myPod.status.phase} with ip {myPod.status.pod_ip}" )

        # The pod is not in Pending
        # read the status.phase, if it's not Running 
        if myPod.status.phase != 'Running':
            # something wrong 
            msg =  f"e.Your pod does not start, status is {myPod.status.phase} reason is {myPod.status.reason} message {myPod.status.message}" 
            self.on_desktoplaunchprogress( msg )
            return msg
        else:
            self.on_desktoplaunchprogress(f"b.Your pod is {myPod.status.phase}.")

        myDesktop = self.pod2desktop( pod=myPod, authinfo=authinfo, userinfo=userinfo)
        self.logger.debug(f"desktop phase:{myPod.status.phase} has interfaces properties {myDesktop.desktop_interfaces}")
        self.logger.debug('watch filldictcontextvalue creating' )
        # set desktop web hook
        # webhook is None if network_config.get('context_network_webhook') is None
        fillednetworkconfig = self.filldictcontextvalue(authinfo=authinfo, 
                                                        userinfo=userinfo, 
                                                        desktop=myDesktop, 
                                                        network_config=network_config, 
                                                        network_name = None, 
                                                        appinstance_id = None )

        myDesktop.webhook = fillednetworkconfig.get('webhook')
        self.logger.debug('watch filldictcontextvalue created' )

        self.logger.debug('createdesktop end' )
        return myDesktop

  
    
    def findPodByUser(self, authinfo:AuthInfo, userinfo:AuthUser )->V1Pod:
        """find a kubernetes pod for the user ( userinfo )
           if args is None, filter add always type=self.x11servertype
           if args is { 'pod_name'=name } add filter metadata.name=name without type selector

           findPodByUser return only Pod in running state 
           'Terminating' or 'Deleting' pod are skipped
            
        Args:
            authinfo (AuthInfo): authentification data
            userinfo (AuthUser): user data 
            args (dict, optional): { 'pod_name'=name of pod }. Defaults to None.

        Returns:
            V1Pod: kubernetes.V1Pod or None if not found
        """
        self.logger.info('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"

        access_userid = userinfo.userid

        try: 
            label_selector = 'access_userid=' + access_userid + ',type=' + self.x11servertype
        
            if isinstance( authinfo, AuthInfo) and oc.od.settings.desktop['authproviderneverchange'] is True:
                label_selector += ',' + 'access_provider='  + authinfo.provider   

            #
            # pod_name = None
            # if type(args) is dict:
            #     pod_name = args.get( 'pod_name' )
            # if pod_name is set, don't care about the type
            # type can be type=self.x11servertype or type=self.x11embededservertype
            # if type( pod_name ) is str :
            #    field_selector =  'metadata.name=' + pod_name
            # else :    
            #    label_selector += ',type=' + self.x11servertype
            #

            myPodList = self.kubeapi.list_namespaced_pod(self.namespace, label_selector=label_selector)

            if isinstance(myPodList, V1PodList) :
                for myPod in myPodList.items:
                    myPhase = myPod.status.phase
                    # keep only Running pod
                    if myPod.metadata.deletion_timestamp is not None:
                       myPhase = 'Terminating'
                    if myPhase in [ 'Running', 'Pending', 'Succeeded' ] :  # 'Init:0/1'
                        return myPod                    
                    
        except ApiException as e:
            self.logger.info("Exception when calling list_namespaced_pod: %s" % e)
        
        return None

    def isPodBelongToUser( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str)->bool:
        """isPodBelongToUser
            return True if pod belongs to userinfo.userid and macth same auth provider
            else False
        Args:
            authinfo (AuthInfo): authinfo
            userinfo (AuthUser): userinfo
            pod_name (str): name of pod

        Returns:
            bool: boolean 
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        assert isinstance(pod_name,  str),      f"pod_name has invalid type {type(pod_name)}"

        belong = False
        myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=pod_name )
        if isinstance( myPod, V1Pod ):
            (pod_authinfo,pod_userinfo) = self.extract_userinfo_authinfo_from_pod(myPod)

        if  authinfo.provider == pod_authinfo.provider and \
            userinfo.userid   == pod_userinfo.userid :
            belong = True

        return belong

    def findDesktopByUser(self, authinfo:AuthInfo, userinfo:AuthUser )->ODDesktop:
        """findDesktopByUser
            find a desktop for authinfo and userinfo 
            return a desktop object
            return None if not found 
        Args:
            authinfo (AuthInfo): authinfo
            userinfo (AuthUser): userinfo

        Returns:
            ODDesktop: ODDesktop object
        """
        self.logger.debug('')
        assert isinstance(authinfo, AuthInfo),  f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo, AuthUser),  f"userinfo has invalid type {type(userinfo)}"
        myDesktop = None  # return Desktop Object
        myPod = self.findPodByUser( authinfo, userinfo )
        if isinstance(myPod, V1Pod ):
            self.logger.debug( f"Pod is found {myPod.metadata.name}" )
            myDesktop = self.pod2desktop( pod=myPod, authinfo=authinfo, userinfo=userinfo )
        return myDesktop

    def getcontainerfromPod( self,  prefix:str, pod:V1Pod ) -> V1ContainerStatus:
        """getcontainerfromPod
            return the v1_container_status of a container inside a pod

        Args:
            prefix (str): container prefix
            pod (V1Pod): pod

        Returns:
            V1ContainerStatus: return v1_container_status, None if unreadable
        """
        assert isinstance(prefix,str), f"prefix invalid type {type(prefix)}"
        assert isinstance(pod,V1Pod) , f"pod invalid type {type(pod)}"
        # get the container id for the desktop object
        if isinstance( pod.status, V1PodStatus):
            if isinstance( pod.status.container_statuses, list):
                for c in pod.status.container_statuses:
                    if hasattr( c, 'name') and isinstance(c.name, str ) and c.name[0] == prefix:
                        return c
        return None

    def getcontainerSpecfromPod( self,  prefix:str, pod:V1Pod ) -> V1Container:
        """getcontainerfromPod
            return the v1_container_status of a container inside a pod

        Args:
            prefix (str): container prefix
            pod (V1Pod): pod

        Returns:
            V1ContainerStatus: return v1_container_status, None if unreadable
        """
        assert isinstance(prefix,str), f"prefix invalid type {type(prefix)}"
        assert isinstance(pod,V1Pod) , f"pod invalid type {type(pod)}"

        # get the container id for the desktop object
        if isinstance( pod.spec.containers, list):
            for c in pod.spec.containers:
                if hasattr( c, 'name') and isinstance(c.name, str ) and c.name[0] == prefix:
                    return c
        return None

    def build_internalPodFQDN( self, myPod: V1Pod )->str:
        """build_internalPodFQDN

        Args:
            myPod (V1Pod): pod

        Returns:
            str: pod internal FQDH
        """
        assert isinstance(myPod,      V1Pod),    f"pod has invalid type {type(myPod)}"
        # From https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#pods:
        # From https://github.com/coredns/coredns/issues/2409 
        # If there exists a headless service in the same namespace as the pod and with the same name
        # as the subdomain, the cluster’s KubeDNS Server also returns an A record for the Pod’s fully
        # qualified hostname. For example, given a Pod with the hostname set to “busybox-1” and the
        # subdomain set to “default-subdomain”, and a headless Service named “default-subdomain” in
        # the same namespace, the pod will see its own FQDN as
        # “busybox-1.default-subdomain.my-namespace.svc.cluster.local
        # 
        defaultFQDN = None
        if oc.od.settings.desktop['useinternalfqdn'] and isinstance(oc.od.settings.kubernetes_default_domain, str ):
            defaultFQDN = myPod.metadata.name + '.' + myPod.spec.subdomain + '.' + oc.od.settings.kubernetes_default_domain
        return defaultFQDN

    def pod2desktop( self, pod:V1Pod, authinfo:AuthInfo=None, userinfo:AuthUser=None )->ODDesktop:
        """pod2Desktop convert a Pod to Desktop Object
        Args:
            myPod ([V1Pod): kubernetes.V1Pod
            userinfo ([]): userinfo set to None by default
                           to obtain vnc_password, defined userinfo context 
        Returns:
            [ODesktop]: oc.od.desktop.ODDesktop Desktop Object
        """
        assert isinstance(pod,V1Pod),    f"pod has invalid type {type(pod)}"

        desktop_container_id   = None
        storage_container_id   = None
        desktop_container_name = None
        desktop_interfaces     = None
        vnc_password           = None

        # read metadata annotations 'k8s.v1.cni.cncf.io/networks-status'
        # to get the ip address of each netwokr interface
        network_status = None
        if isinstance(pod.metadata.annotations, dict):
            network_status = pod.metadata.annotations.get( 'k8s.v1.cni.cncf.io/networks-status' )
            if isinstance( network_status, str ):
                # k8s.v1.cni.cncf.io/networks-status is set
                # load json formated string
                network_status = json.loads( network_status )

            if isinstance( network_status, list ):
                desktop_interfaces = {}
                self.logger.debug( f"network_status is {network_status}" )
                for interface in network_status :
                    self.logger.debug( f"reading interface {interface}" )
                    if not isinstance( interface, dict ): 
                        continue
                    # read interface
                    name = interface.get('interface')
                    if not isinstance( name, str ): 
                        continue
                    # read ips
                    ips = interface.get('ips')
                    if  not isinstance( ips, list ): 
                        continue
                    # read mac
                    mac = interface.get('mac')
                    if not isinstance( mac, str ) :
                         continue
                    # read default ips[0]
                    if len(ips) == 1:   
                        ips = str(ips[0])
                    desktop_interfaces.update( { name : { 'mac': mac, 'ips': ips } } )
 
        desktop_container = self.getcontainerfromPod( self.graphicalcontainernameprefix, pod )
        if isinstance(desktop_container, V1ContainerStatus) :
            desktop_container_id = desktop_container.container_id
            desktop_container_name = desktop_container.name
        
        internal_pod_fqdn = self.build_internalPodFQDN( pod )

        # read the vnc password from kubernetes secret  
        # Authuser can be None if this is a gabargecollector batch
        # then vnc_secret_password is not used 
        if isinstance(userinfo, AuthUser) and isinstance(authinfo, AuthInfo) : 
            vnc_secret = oc.od.secret.ODSecretVNC( self.namespace, self.kubeapi )
            vnc_secret_password = vnc_secret.read( authinfo, userinfo )  
            if isinstance( vnc_secret_password, V1Secret ):
                vnc_password = oc.od.secret.ODSecret.read_data( vnc_secret_password, 'password' )

        storage_container = self.getcontainerfromPod( self.storagecontainernameprefix, pod )
        if isinstance(storage_container, V1ContainerStatus):
           storage_container_id = storage_container.container_id

        # Build the ODDesktop Object 
        myDesktop = oc.od.desktop.ODDesktop(
            nodehostname=pod.spec.node_name, 
            name=pod.metadata.name,
            hostname=pod.spec.hostname,
            ipAddr=pod.status.pod_ip, 
            status=pod.status.phase, 
            desktop_id=pod.metadata.name, 
            container_id=desktop_container_id,                                                   
            container_name=desktop_container_name,
            vncPassword=vnc_password,
            fqdn = internal_pod_fqdn,
            xauthkey = pod.metadata.labels.get('xauthkey'),
            pulseaudio_cookie = pod.metadata.labels.get('pulseaudio_cookie'),
            broadcast_cookie = pod.metadata.labels.get('broadcast_cookie'),
            desktop_interfaces = desktop_interfaces,
            websocketrouting = pod.metadata.labels.get('websocketrouting', oc.od.settings.websocketrouting),
            websocketroute = pod.metadata.labels.get('websocketroute'),
            storage_container_id = storage_container_id,
            labels = pod.metadata.labels,
            uid = pod.metadata.uid
        )
        return myDesktop

    def countdesktop(self)->int:
        """countdesktop
            count the number of desktop label_selector = 'type=' + self.x11servertype
        Returns:
            int: number of desktop
        """
        list_of_desktop = self.list_desktop()
        return len(list_of_desktop)

    def list_desktop(self, phase_filter:list=[ 'Running', 'Pending' ])->list:
        """list_desktop

        Returns:
            list: list of ODDesktop
        """
        myDesktopList = []   
        try:  
            list_label_selector = 'type=' + self.x11servertype
            myPodList = self.kubeapi.list_namespaced_pod(self.namespace, label_selector=list_label_selector)
            if isinstance( myPodList, V1PodList):
                for myPod in myPodList.items:
                    if isinstance( myPod.status, V1PodStatus ):
                        myPhase = myPod.status.phase
                        # keep only Running pod
                        if myPod.metadata.deletion_timestamp is None: 
                            if myPhase in phase_filter :
                                mydesktop = self.pod2desktop( myPod )
                                if isinstance( mydesktop, ODDesktop):
                                    myDesktopList.append( mydesktop.to_dict() )              
        except ApiException as e:
            self.logger.error(e)

        return myDesktopList
            
    def isgarbagable( self, pod:V1Pod, expirein:int, force=False )->bool:
        """isgarbagable

        Args:
            pod (V1Pod): pod
            expirein (int): in seconds
            force (bool, optional): check if user is connected or not. Defaults to False.

        Returns:
            bool: True if pod is garbageable
        """
        self.logger.debug('')
        bReturn = False
        assert isinstance(pod, V1Pod),    f"pod has invalid type {type(pod)}"
        assert isinstance(expirein, int), f"expirein has invalid type {type(expirein)}"
        if pod.status.phase == 'Failed':
            self.logger.warning(f"pod {pod.metadata.name} is in phase {pod.status.phase} reason {pod.status.reason}" )
            return True

        myDesktop = self.pod2desktop( pod=pod )
        if not isinstance(myDesktop, ODDesktop):
            return False

        if force is False:
            nCount = self.user_connect_count( myDesktop )
            if nCount < 0: 
                # if something wrong nCount is equal to -1 
                # do not garbage this pod
                # this is an error, return False
                return bReturn 
            if nCount > 0 : 
                # if a user is connected do not garbage this pod
                # user is connected, return False
                return bReturn 
            #
            # now nCount == 0 continue 
            # the garbage process
            # to test if we can delete this pod

        # read the lastlogin datetime from metadata annotations
        lastlogin_datetime = self.read_pod_annotations_lastlogin_datetime( pod )
        if isinstance( lastlogin_datetime, datetime.datetime):
            # get the current time
            now_datetime = datetime.datetime.now()
            delta_datetime = now_datetime - lastlogin_datetime
            delta_second = delta_datetime.total_seconds()
            # if delta_second is more than expirein in second
            if ( delta_second > expirein  ):
                # this pod is gabagable
                bReturn = True
        return bReturn


    def extract_userinfo_authinfo_from_pod( self, pod:V1Pod )->tuple:
        """extract_userinfo_authinfo_from_pod
            Read labels (authinfo,userinfo) from a pod
        Args:
            myPod (V1Pod): Pod

        Returns:
            (tuple): (authinfo,userinfo) AuthInfo, AuthUser
        """
        assert isinstance(pod,      V1Pod),    f"pod has invalid type {type(pod)}"

        # fake an authinfo object
        authinfo = AuthInfo( 
            provider=pod.metadata.labels.get('access_provider'), 
            providertype=pod.metadata.labels.get('access_providertype') 
        )
        # fake an userinfo object
        userinfo = AuthUser( {
            'userid':pod.metadata.labels.get('access_userid'),
            'name':  pod.metadata.labels.get('access_username')
        } )
        return (authinfo,userinfo)


    def find_userinfo_authinfo_by_desktop_name( self, name:str )->tuple:
        """find_userinfo_authinfo_by_desktop_name

        Args:
            name (str): name of pod

        Returns:
            tuple: (authinfo,userinfo)
        """
        self.logger.debug('')
        assert isinstance(name, str), f"name has invalid type {type(str)}"
        authinfo = None
        userinfo = None
        myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace,name=name )
        if isinstance( myPod, V1Pod ) :  
            (authinfo,userinfo) = self.extract_userinfo_authinfo_from_pod(myPod)
        return (authinfo,userinfo)

    def describe_desktop_byname( self, name:str )->dict:
        """describe_desktop_byname

        Args:
            name (str): name of the pod

        Returns:
            dict: dict of the desktop's pod loaded from json data
        """
        self.logger.debug('')
        assert isinstance(name, str), f"name has invalid type {type(str)}"
        myPod = self.kubeapi.read_namespaced_pod(namespace=self.namespace, name=name, _preload_content=False)
        if isinstance( myPod, urllib3.response.HTTPResponse ) :  
            myPod = json.loads( myPod.data )
        return myPod

    def garbagecollector( self, expirein:int, force=False )-> list :
        """garbagecollector

        Args:
            expirein (int): garbage expired in millisecond 
            force (bool, optional): force event if user is connected. Defaults to False.

        Returns:
            list: list of str, list of pod name garbaged
        """
        self.logger.debug('')
        assert isinstance(expirein, int), f"expirein has invalid type {type(expirein)}"

        garbaged = [] # list of garbaged pod
        list_label_selector = [ 'type=' + self.x11servertype ]
        for label_selector in list_label_selector:
            myPodList = self.kubeapi.list_namespaced_pod(self.namespace, label_selector=label_selector)
            if isinstance( myPodList, V1PodList):
                for pod in myPodList.items:
                    try: 
                        if self.isgarbagable( pod, expirein, force ) is True:
                            # pod is garbageable, remove it
                            self.logger.info( f"{pod.metadata.name} is garbageable, remove it" )
                            # fake an authinfo object
                            (authinfo,userinfo) = self.extract_userinfo_authinfo_from_pod(pod)
                            # remove desktop
                            self.removedesktop( authinfo, userinfo, pod )
                            # log remove desktop
                            self.logger.info( f"{pod.metadata.name} is removed" )
                            # add the name of the pod to the list of garbaged pod
                            garbaged.append( pod.metadata.name )
                        else:
                            self.logger.info( f"{pod.metadata.name} isgarbagable return False, keep it running" )

                    except ApiException as e:
                        self.logger.error(e)
        return garbaged


@oc.logging.with_logger()
class ODAppInstanceBase(object):
    def __init__(self,orchestrator):
        self.orchestrator = orchestrator
        self.type=None # default value overwrited by class instance 
        self.executeclassename='default' # default value overwrited by class instance 

    def findRunningAppInstanceforUserandImage( self, authinfo, userinfo, app):
        raise NotImplementedError('%s.build_volumes' % type(self))

    @staticmethod
    def isinstance( app ):
        raise NotImplementedError('isinstance' % type(app))

    def get_DISPLAY( self, desktop_ip_addr:str='' ):
        raise NotImplementedError('get_DISPLAY')

    def get_PULSE_SERVER( self, desktop_ip_addr:str=None ):
        raise NotImplementedError('get_PULSE_SERVER')

    def get_CUPS_SERVER( self, desktop_ip_addr:str=None ):
        raise NotImplementedError('get_CUPS_SERVER')

    def get_env_for_appinstance(self, myDesktop, app, authinfo, userinfo={}, userargs=None, **kwargs ):
        assert isinstance(myDesktop,  ODDesktop),  f"desktop has invalid type {type(myDesktop)}"
        assert isinstance(authinfo,   AuthInfo),   f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo,   AuthUser),   f"userinfo has invalid type {type(userinfo)}"

        posixuser = self.orchestrator.alwaysgetPosixAccountUser( authinfo, userinfo )

        # make sure env DISPLAY, PULSE_SERVER,CUPS_SERVER exist
        # read the desktop (oc.user) ip address
        desktop_ip_addr = myDesktop.get_default_ipaddr('eth0')
        self.logger.debug( f"desktop_ip_addr={desktop_ip_addr}" )
        # clone env 
        env = oc.od.settings.desktop['environmentlocal'].copy()
        # update env with desktop_ip_addr if need
        env['DISPLAY'] = self.get_DISPLAY(desktop_ip_addr)
        env['CONTAINER_IP_ADDR'] = desktop_ip_addr   # CONTAINER_IP_ADDR is used by ocrun node js command
        env['XAUTH_KEY'] = myDesktop.xauthkey
        env['BROADCAST_COOKIE'] = myDesktop.broadcast_cookie
        env['PULSEAUDIO_COOKIE'] = myDesktop.pulseaudio_cookie
        env['PULSE_SERVER'] = self.get_PULSE_SERVER(desktop_ip_addr)
        env['CUPS_SERVER'] = self.get_CUPS_SERVER(desktop_ip_addr)
        env['UNIQUERUNKEY'] = app.get('uniquerunkey')
        env['HOME'] = posixuser.get('homeDirectory')
        env['LOGNAME'] = posixuser.get('uid')
        env['USER'] = posixuser.get('uid')
    
        #
        # update env with cuurent http request user LANG values
        # read locale language from USER AGENT
        language = userinfo.get('locale', 'en_US')
        # LC_ALL is the environment variable that overrides all the other localisation settings 
        # (except $LANGUAGE under some circumstances).
        env['LANGUAGE'] = language
        env['LANG'] = language + '.UTF-8'
        env['LC_ALL']= language + '.UTF-8'

        # add PARENT_ID PARENT_HOSTNAME for ocrun nodejs script 
        env['PARENT_ID']=myDesktop.id
        env['PARENT_HOSTNAME']=myDesktop.nodehostname

        # update env APP to run command in /composer/apply-docker-entrypoint.sh
        env['APP'] = app.get('path')
        # Add specific vars
        if isinstance( kwargs, dict ):
            timezone = kwargs.get('timezone')
            if isinstance(timezone, str) and len(timezone) > 1:
                env['TZ'] = timezone
        if isinstance(userargs, str) and len(userargs) > 0:
            env['APPARGS'] = userargs
        if isinstance( app.get('args'), str) and len(app.get('args')) > 0:
            env['ARGS'] = app.get('args')
        if hasattr(authinfo, 'data') and isinstance( authinfo.data, dict ):
            env.update(authinfo.data.get('identity', {}))

        # convert env dictionnary to env list format for kubernetes
        envlist = ODOrchestratorKubernetes.envdict_to_kuberneteslist( env )
        ODOrchestratorKubernetes.appendkubernetesfieldref( envlist )
        
        return envlist

    def get_securitycontext(self, authinfo:AuthInfo, userinfo:AuthUser, app:dict  ):
        assert isinstance(authinfo,   AuthInfo),   f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo,   AuthUser),   f"userinfo has invalid type {type(userinfo)}"
        assert isinstance(app,  dict),             f"desktop has invalid type  {type(app)}"
        securitycontext = {}
        user_securitycontext = self.orchestrator.updateSecurityContextWithUserInfo( self.type, authinfo, userinfo )
        app_securitycontext = app.get('securitycontext',{}) or {} 
        securitycontext.update( user_securitycontext )
        securitycontext.update( app_securitycontext )
        self.logger.debug( f"securitycontext={securitycontext}")
        return securitycontext

    def get_resources( self, authinfo:AuthInfo, userinfo:AuthUser, app:dict ):
        assert isinstance(authinfo,   AuthInfo),   f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo,   AuthUser),   f"userinfo has invalid type {type(userinfo)}"
        assert isinstance(app,        dict),       f"desktop has invalid type  {type(app)}"
       
        executeclassname =  app.get('executeclassname')
        self.logger.debug( f"app name={app.get('name')} has executeclassname={executeclassname}")
        executeclass = self.orchestrator.get_executeclasse( authinfo, userinfo, executeclassname )
        self.logger.debug( f"executeclass={executeclass}")
        resources = self.orchestrator.get_resources( self.type, executeclass )
        self.logger.debug( f"resources={resources}")

        return resources



    def get_default_affinity( self, authinfo:AuthInfo, userinfo:AuthUser, app:dict, desktop:ODDesktop )->dict:
        assert isinstance(desktop, ODDesktop), f"invalid desktop type {type(desktop)}"
        affinity = {
            'nodeAffinity': {
                'preferredDuringSchedulingIgnoredDuringExecution': [
                    {   'weight': 1,
                        'preference': {
                            'matchExpressions': [
                                {   'key': 'kubernetes.io/hostname',
                                    'operator': 'In',
                                    'values': [ desktop.nodehostname ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return affinity

    def get_affinity( self, authinfo:AuthInfo, userinfo:AuthUser, app:dict, desktop:ODDesktop )->dict:
        assert isinstance(desktop, ODDesktop), f"invalid desktop type {type(desktop)}"
        affinity = self.get_default_affinity(authinfo, userinfo, app, desktop)
        default_config_affinity = oc.od.settings.desktop_pod[self.type].get('affinity', {}) or {}
        affinity.update(default_config_affinity)
        return affinity
  
@oc.logging.with_logger()
class ODAppInstanceKubernetesEphemeralContainer(ODAppInstanceBase):

    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        self.type = self.orchestrator.ephemeral_container

    @staticmethod
    def isinstance( ephemeralcontainer ):
        bReturn =   isinstance( ephemeralcontainer, V1Pod ) or \
                    isinstance( ephemeralcontainer, V1ContainerState ) or \
                    isinstance( ephemeralcontainer, V1ContainerStatus )
        return bReturn

    def get_DISPLAY(  self, desktop_ip_addr:str=None ):
        return ':0.0'

    def get_PULSE_SERVER(  self, desktop_ip_addr:str='' ):
        return  'unix:/tmp/.pulse.sock'

    def get_CUPS_SERVER( self, desktop_ip_addr:str ):
        return desktop_ip_addr + ':' + str(DEFAULT_CUPS_TCP_PORT)

    def envContainerApp(self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str )->dict:
        """get_env
            return a dict of env VAR of an ephemeral container

        Args:
            pod_name (str): name of the pod
            container_name (str): name of the container

        Raises:
            ValueError: ValueError( 'Invalid read_namespaced_pod_ephemeralcontainers')
            if pod_ephemeralcontainers can not be read

        Returns:
            dict: VAR_NAME : VAR_VALUE
            or None if failed
        """
        assert isinstance(pod_name, str),    f"pod_name has invalid type {type(pod_name)}"
        assert isinstance(containerid, str), f"containerid has invalid type {type(containerid)}"
        env_result = None
        pod_ephemeralcontainers = self.orchestrator.kubeapi.read_namespaced_pod_ephemeralcontainers(
            name=pod_name, 
            namespace=self.orchestrator.namespace )
        if not isinstance(pod_ephemeralcontainers, V1Pod ):
            raise ValueError( 'Invalid read_namespaced_pod_ephemeralcontainers')

        if isinstance(pod_ephemeralcontainers.spec.ephemeral_containers, list):
            for c in pod_ephemeralcontainers.spec.ephemeral_containers:
                if c.name == containerid :
                    env_result = {}
                    #  convert name= value= to dict
                    for e in c.env:
                        if isinstance( e, V1EnvVar ):
                            env_result[ e.name ] =  e.value
                    break
        return env_result

    def logContainerApp(self, pod_name:str, container_name:str)->str:
        assert isinstance(pod_name,  str),  f"pod_name has invalid type  {type(pod_name)}"
        assert isinstance(container_name,  str),  f"container_name has invalid type {type(container_name)}"
        strlogs = 'no logs read'
        try:
            strlogs = self.orchestrator.kubeapi.read_namespaced_pod_log( 
                name=pod_name, 
                namespace=self.orchestrator.namespace, 
                container=container_name, 
                pretty='true' )
        except ApiException as e:
            self.logger.error( e )
        except Exception as e:
            self.logger.error( e )
        return strlogs
        

    def get_status( self, pod_ephemeralcontainers:V1Pod, container_name:str ):
        """get_status

        Args:
            pod_ephemeralcontainers (V1Pod): pod_ephemeralcontainers
            container_name (str): name of the container to return

        Returns:
            _type_: _description_
        """
        assert isinstance(pod_ephemeralcontainers, V1Pod), f"pod_ephemeralcontainers has invalid type  {type(pod_ephemeralcontainers)}"
        assert isinstance(container_name,  str),  f"container_name has invalid type  {type(container_name)}"
        pod_ephemeralcontainer = None

        if isinstance( pod_ephemeralcontainers.status, V1PodStatus ) and \
           isinstance( pod_ephemeralcontainers.status.ephemeral_container_statuses, list):
                for c in pod_ephemeralcontainers.status.ephemeral_container_statuses :
                    if c.name == container_name:
                        pod_ephemeralcontainer = c
                        break
        return pod_ephemeralcontainer

    def get_phase( self, ephemeralcontainer:V1ContainerStatus ):
        """get_phase
            return a Phase like as pod for ephemeral_container
            string 'Terminated' 'Running' 'Waiting' 'Error'
        Args:
            ephemeralcontainer (V1ContainerStatus): V1ContainerStatus

        Returns:
            str: str phase of ephemeral_container status can be one of 'Terminated' 'Running' 'Waiting' 'Error'
        """
        text_state = 'Error' # defalut value shoud never be return

        if isinstance( ephemeralcontainer, V1ContainerStatus ):
            if  isinstance(ephemeralcontainer.state.terminated, V1ContainerStateTerminated ):
                text_state = 'Terminated'
            elif isinstance(ephemeralcontainer.state.running, V1ContainerStateRunning ):
                text_state = 'Running'
            elif isinstance(ephemeralcontainer.state.waiting, V1ContainerStateWaiting):
                text_state = 'Waiting'
        return text_state


    def stop(self, pod_name:str, container_name:str)->bool:
        self.logger.debug('')
        assert isinstance(pod_name,  str),  f"pod_name has invalid type  {type(pod_name)}"
        assert isinstance(container_name,  str),  f"container_name has invalid type  {type(container_name)}"

        pod_ephemeralcontainers =  self.orchestrator.kubeapi.read_namespaced_pod_ephemeralcontainers(
            name=pod_name, 
            namespace=self.namespace )
        if not isinstance(pod_ephemeralcontainers, V1Pod ):
            raise ValueError( 'Invalid read_namespaced_pod_ephemeralcontainers')

        if isinstance(pod_ephemeralcontainers.spec.ephemeral_containers, list):
            for i in range( len(pod_ephemeralcontainers.spec.ephemeral_containers) ):
                if pod_ephemeralcontainers.spec.ephemeral_containers[i].name == container_name :
                    pod_ephemeralcontainers.spec.ephemeral_containers.pop(i)
                    break

        # replace ephemeralcontainers
        pod=self.orchestrator.kubeapi.patch_namespaced_pod_ephemeralcontainers(
            name=pod_name, 
            namespace=self.namespace, 
            body=pod_ephemeralcontainers )
        if not isinstance(pod, V1Pod ):
            raise ValueError( 'Invalid patch_namespaced_pod_ephemeralcontainers')

        stop_result = True

        return stop_result


    def list( self, authinfo, userinfo, myDesktop, phase_filter=[ 'Running', 'Waiting'], apps:ODApps=None )->list:
        self.logger.debug('')
        assert isinstance(myDesktop,  ODDesktop),  f"desktop has invalid type  {type(myDesktop)}"
        assert isinstance(authinfo,   AuthInfo),   f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo,   AuthUser),   f"userinfo has invalid type {type(userinfo)}"
        assert isinstance(phase_filter, list),     f"phase_filter has invalid type {type(phase_filter)}"

        result = []
        pod_ephemeralcontainers =  self.orchestrator.kubeapi.read_namespaced_pod_ephemeralcontainers(name=myDesktop.id, namespace=self.orchestrator.namespace )
        if not isinstance(pod_ephemeralcontainers, V1Pod ):
            raise ValueError( 'Invalid read_namespaced_pod_ephemeralcontainers')

        if isinstance(pod_ephemeralcontainers.spec.ephemeral_containers, list):
            for c_spec in pod_ephemeralcontainers.spec.ephemeral_containers:
                app = {}
                c_status = self.get_status( pod_ephemeralcontainers, c_spec.name )
                if isinstance( c_status, V1ContainerStatus ):
                    phase = self.get_phase( c_status )
                    if phase in phase_filter:
                        if isinstance(apps, ODApps):
                            app = apps.find_app_by_id( c_status.image ) or {}

                        # convert an ephemeralcontainers container to json by filter entries
                        mycontainer = {}
                        mycontainer['podname']  = myDesktop.id
                        mycontainer['id']       = c_status.name # myPod.metadata.uid
                        mycontainer['short_id'] = c_status.container_id
                        mycontainer['status']   = c_status.ready
                        mycontainer['image']    = c_status.image
                        mycontainer['oc.path']  = c_spec.command
                        mycontainer['nodehostname'] = myDesktop.nodehostname
                        mycontainer['architecture'] = app.get('architecture')
                        mycontainer['os']           = app.get('os')
                        mycontainer['oc.icondata']  = app.get('icondata')
                        mycontainer['oc.args']      = app.get('args')
                        mycontainer['oc.icon']      = app.get('icon')
                        mycontainer['oc.launch']    = app.get('launch')
                        # mycontainer['oc.displayname'] = c_status.name
                        mycontainer['oc.displayname'] = app.get('displayname')
                        mycontainer['runtime']        = 'kubernetes'
                        mycontainer['type']           = 'ephemeralcontainer'
                        mycontainer['status']         = phase

                        # add the object to the result array
                        result.append( mycontainer )

        return result



    def create(self, myDesktop, app, authinfo, userinfo={}, userargs=None, **kwargs ):
        self.logger.debug('')
        assert isinstance(myDesktop,  ODDesktop),  f"desktop has invalid type  {type(myDesktop)}"
        assert isinstance(authinfo,   AuthInfo),   f"authinfo has invalid type {type(authinfo)}"

        #
        # shareProcessNamespace and shareProcessMemory do not exist for EphemeralContainer
        #
        # self.logger.debug("create {self.type} getting shareProcessNamespace and shareProcessMemory options from desktop config")
        # shareProcessNamespace = oc.od.settings.desktop_pod.get('spec',{}).get('shareProcessNamespace', False)
        # shareProcessMemory = oc.od.settings.desktop_pod.get('spec',{}).get('shareProcessMemory', False)
        # self.logger.debug(f"shareProcessNamespace={shareProcessNamespace} shareProcessMemory={shareProcessMemory}")

        app_container_name = self.orchestrator.get_normalized_username(userinfo.get('name', 'name')) + \
                            '-' + app['name'] + '-' + oc.lib.uuid_digits()
        self.logger.debug( f"app_container_name={app_container_name}" )
        app_container_name = oc.auth.namedlib.normalize_name_dnsname( app_container_name )
        self.logger.debug( f"normalized app_container_name={app_container_name}" )

        desktoprules = oc.od.settings.desktop['policies'].get('rules', {})
        rules = copy.deepcopy( desktoprules )
        apprules = app.get('rules', {} ) or {} # app['rules] can be set to None
        rules.update( apprules )

        self.logger.debug( f"reading pod desktop desktop.id={myDesktop.id} myDesktop.container_name={myDesktop.container_name} app_container_name={app_container_name}")

        # resources = self.get_resources( authinfo, userinfo, app )
        envlist = self.get_env_for_appinstance(  myDesktop, app, authinfo, userinfo, userargs, **kwargs )
        # add EXECUTION CONTEXT env var inside the container
        envlist.append( { 'name': 'ABCDESKTOP_EXECUTE_RUNTIME',   'value': self.type} )
        resources = self.orchestrator.read_pod_resources(myDesktop.name)
        envlist.append( { 'name': 'ABCDESKTOP_EXECUTE_RESOURCES', 'value': json.dumps(resources) } )

        gpu_file= '/tmp/gpu_uuid'

        if os.path.exists(gpu_file):
            with open(gpu_file, 'r') as f:
                gpu_uuid = f.read()
            envlist.append( { 'name': 'NVIDIA_VISIBLE_DEVICES',   'value': gpu_uuid} )

        kwargs['uid'] = myDesktop.uid
        kwargs['container_name'] = myDesktop.container_name
        (volumeBinds, volumeMounts) = self.orchestrator.build_volumes( 
            authinfo,
            userinfo,
            volume_type=self.type,
            secrets_requirement=app.get('secrets_requirement'),
            rules=rules,
            **kwargs
        )
        list_volumeBinds = list( volumeBinds.values() )
        list_volumeMounts = list( volumeMounts.values() )
        self.logger.debug( f"list volume binds pod desktop {list_volumeBinds}")
        self.logger.debug( f"list volume mounts pod desktop {list_volumeMounts}")

        workingDir = self.orchestrator.get_user_homedirectory( authinfo, userinfo )
        self.logger.debug( f"user workingDir={workingDir}")

        # remove subPath
        # Pod volumes to mount into the container's filesystem.
        # Subpath mounts are not allowed for ephemeral containers.
        # Can not be updated.
        #
        # Forbidden: can not be set for an Ephemeral Container",
        # "reason":"FieldValueForbidden",
        # "message":"Forbidden: can not be set for an Ephemeral Container",
        # "field":"spec.ephemeralContainers[8].volumeMounts[0].subPath"}]},
        # "code":422}
        # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1EphemeralContainer.md
        # Pod volumes to mount into the container's filesystem. Subpath mounts are not allowed for ephemeral containers
        assert oc.od.settings.desktop['persistentvolumeclaimforcesubpath'] is False, \
            f"desktop.persistentvolumeclaimforcesubpath is {oc.od.settings.desktop['persistentvolumeclaimforcesubpath']} \
            Subpath mounts are not allowed for ephemeral containers"

        securitycontext = self.get_securitycontext( authinfo, userinfo, app )

        # apply network rules
        # network_config = self.applyappinstancerules_network( authinfo, rules )
        # apply homedir rules
        # homedir_disabled = self.applyappinstancerules_homedir( authinfo, rules )
        
        # Fix python kubernetes
        # Ephemeral container not added to pod #1859
        # https://github.com/kubernetes-client/python/issues/1859
        #
        ephemeralcontainer = V1EphemeralContainer(  
            name=app_container_name,
            security_context=securitycontext,
            env=envlist,
            image=app['id'],
            command=app.get('cmd'),
            target_container_name=myDesktop.container_name,
            image_pull_policy=oc.od.settings.desktop_pod[self.type].get('imagePullPolicy','IfNotPresent'),
            volume_mounts = list_volumeMounts,
            working_dir = workingDir
        )

        # This succeeds and the ephemeral container is added but without any volume mounts or messages
        # because its sending the dictionary as snake_case and k8s is expecting camelCase, 
        # solved this by just making a raw dictionary with the proper casing
        ephemeralcontainer_dict = ephemeralcontainer.to_dict()
        #  snake_case to camelCase entries
        ephemeralcontainer_dict_CamelCase = oc.auth.namedlib.dictSnakeCaseToCamelCase( ephemeralcontainer_dict )
        # create ther request fixed body
        body = {
            'spec': {
                'ephemeralContainers': [
                    ephemeralcontainer_dict_CamelCase
                ]
            }
        }
        # patch_namespaced_pod_ephemeralcontainers 
        pod = self.orchestrator.kubeapi.patch_namespaced_pod_ephemeralcontainers(   
            name=myDesktop.id,
            namespace=self.orchestrator.namespace, 
            body=body)
        
        if not isinstance(pod, V1Pod ):
            raise ValueError( 'Invalid patch_namespaced_pod_ephemeralcontainers')

        pod_name = myDesktop.id
        # watch list_namespaced_event
        w = watch.Watch()                 
        # read_namespaced_pod

        for event in w.stream(  self.orchestrator.kubeapi.list_namespaced_pod, 
                                namespace=self.orchestrator.namespace, 
                                field_selector=f"metadata.name={pod_name}" ):  

            # event must be a dict, else continue
            if not isinstance(event,dict):  continue
            self.logger.debug( f"{event.get('type')} object={type(event.get('object'))}" )
            pod = event.get('object')
            # if podevent type must be a V1Pod, we use kubeapi.list_namespaced_pod
            if not isinstance( pod, V1Pod ): continue
            if not isinstance( pod.status, V1PodStatus ): continue
            if not isinstance( pod.status.ephemeral_container_statuses, list): continue

            for c in pod.status.ephemeral_container_statuses:
                if isinstance( c, V1ContainerStatus ) and c.name == app_container_name:
                    send_previous_pulling_message = False
                    self.logger.debug( f"{app_container_name} is found in ephemeral_container_statuses {c}")
                    appinstancestatus = oc.od.appinstancestatus.ODAppInstanceStatus( id=c.name, type=self.type )
                    if isinstance( c.state, V1ContainerState ):
                        if  isinstance(c.state.terminated, V1ContainerStateTerminated ):
                            appinstancestatus.message = 'Terminated'
                            w.stop()
                        elif isinstance(c.state.running, V1ContainerStateRunning ):
                            appinstancestatus.message = 'Running'
                            w.stop()
                        elif isinstance(c.state.waiting, V1ContainerStateWaiting):
                            self.logger.debug( f"V1ContainerStateWaiting reason={c.state.waiting.reason}" )
                            data = {    'message':  app.get('name'), 
                                        'name':     app.get('name'),
                                        'icondata': app.get('icondata'),
                                        'icon':     app.get('icon'),
                                        'image':    app.get('id'),
                                        'launch':   app.get('launch')
                            }
                            if c.state.waiting.reason in [ 'PodInitializing' ]:
                                break 
                            if  c.state.waiting.reason == 'Pulling':
                                send_previous_pulling_message = True
                                data['message'] = f"{c.state.waiting.reason} {app.get('name')}, please wait"
                                self.orchestrator.notify_user( myDesktop, 'container', data )
                            elif c.state.waiting.reason == 'Pulled':
                                if send_previous_pulling_message is True:
                                    data['message'] = f"{app.get('name')} is {c.state.waiting.reason}"
                                    self.orchestrator.notify_user( myDesktop, 'container', data )
                            else:
                                if send_previous_pulling_message is True:
                                    data['message'] = c.state.waiting.reason
                                    self.orchestrator.notify_user( myDesktop, 'container', data )

            if event.get('type') == 'ERROR':
                self.logger.error( f"{event.get('type')} object={type(event.get('object'))}")
                w.stop()
        
        """

            # Valid values for event types (new types could be added in future)
            #    EventTypeNormal  string = "Normal"     // Information only and will not cause any problems
            #    EventTypeWarning string = "Warning"    // These events are to warn that something might go wrong
            # self.logger.info( f"object_type={event_object.type} reason={event_object.reason}")
            # message = f"b.{event_object.reason} {event_object.message.lower()}"

        
        send_previous_pulling_message = False
        # watch list_namespaced_event
        w = watch.Watch()                 
        for event in w.stream(  self.orchestrator.kubeapi.list_namespaced_event, 
                                namespace=self.orchestrator.namespace, 
                                timeout_seconds=self.orchestrator.DEFAULT_K8S_CREATE_TIMEOUT_SECONDS,
                                field_selector=f'involvedObject.name={pod_name}' ):  
            if not isinstance(event, dict ): continue
            if not isinstance(event.get('object'), CoreV1Event ): continue

            # Valid values for event types (new types could be added in future)
            #    EventTypeNormal  string = "Normal"     // Information only and will not cause any problems
            #    EventTypeWarning string = "Warning"    // These events are to warn that something might go wrong

            event_object = event.get('object')

            self.logger.debug(f"{event_object.type} reason={event_object.reason} message={event_object.message}")
            data = { 
                    'message':  app.get('name'), 
                    'name':     app.get('name'),
                    'icondata': app.get('icondata'),
                    'icon':     app.get('icon'),
                    'image':    app.get('id'),
                    'launch':   app.get('launch')
            }
            if event_object.type == 'Normal':
                if event_object.reason == 'Pulling':
                    send_previous_pulling_message = True
                    data['message'] =  f"Installing {app.get('name')}, please wait"
                    self.orchestrator.notify_user( myDesktop, 'container', data )
                elif event_object.reason == 'Pulled':
                    if send_previous_pulling_message is True:
                        data['message'] =  f"{app.get('name')} is installed"
                        self.orchestrator.notify_user( myDesktop, 'container', data )
                elif event_object.reason in [ 'Created', 'Scheduled' ]:
                    pass # nothing to do
                elif event_object.reason == 'Started':
                    # w.stop()
                    pass
                else:
                    data['message'] =  f"{app.get('name')} is {event_object.reason}"
                    self.orchestrator.notify_user( myDesktop, 'container', data )
                    self.logger.error(f"{event_object.type} reason={event_object.reason} message={event_object.message}")
                    w.stop()
                
            else: # event_object.type == 'Warning':
                # an error occurs
                data['name'] = event_object.type
                data['message'] = event_object.reason
                self.orchestrator.notify_user( myDesktop, 'container', data )
                w.stop()
            
        """
  
        return appinstancestatus

    def findRunningAppInstanceforUserandImage( self, authinfo:AuthInfo, userinfo:AuthUser, app):
        self.logger.info('')
        assert isinstance(authinfo,   AuthInfo),   f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo,   AuthUser),   f"userinfo has invalid type {type(userinfo)}"

        myephemeralContainerList = []
        uniquerunkey = app.get('uniquerunkey')

        # if the applicattion does nit set the uniquerunkey value
        # find result is always an empty list
        if not isinstance( uniquerunkey ,str):
            return myephemeralContainerList

        myDesktop = self.orchestrator.findDesktopByUser(authinfo, userinfo)
        if not isinstance(myDesktop, ODDesktop):
            self.logger.error('Desktop not found')
            raise ValueError( 'Desktop not found')

        pod_ephemeralcontainers =  self.orchestrator.kubeapi.read_namespaced_pod_ephemeralcontainers(name=myDesktop.id, namespace=self.orchestrator.namespace )
        if not isinstance(pod_ephemeralcontainers, V1Pod ):
            self.logger.error(f"Invalid read_namespaced_pod_ephemeralcontainers {myDesktop.id} not found: pod_ephemeralcontainers is not a V1Pod")
            raise ValueError("Invalid read_namespaced_pod_ephemeralcontainers {myDesktop.id} not found")

        if isinstance(pod_ephemeralcontainers.spec.ephemeral_containers, list):
            for spec_ephemeralcontainer in pod_ephemeralcontainers.spec.ephemeral_containers:
                for v in spec_ephemeralcontainer.env:
                    if isinstance( v, V1EnvVar ):
                        if v.name == 'UNIQUERUNKEY' and v.value == uniquerunkey:
                            # check if the ephemeralcontainer is running
                            ephemeralcontainer = self.get_status( pod_ephemeralcontainers, spec_ephemeralcontainer.name )
                            if isinstance( ephemeralcontainer, V1ContainerStatus) and ephemeralcontainer.state.running:
                                # append it
                                myephemeralContainerList.append( spec_ephemeralcontainer )
                                break

        return myephemeralContainerList



@oc.logging.with_logger()
class ODAppInstanceKubernetesPod(ODAppInstanceBase):
    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        self.type = self.orchestrator.pod_application

    @staticmethod
    def isinstance( pod:V1Pod ):
        bReturn =  isinstance( pod, V1Pod )
        return bReturn

    def get_DISPLAY( self, desktop_ip_addr:str ):
        return desktop_ip_addr + ':0'
    
    def get_PULSE_SERVER( self, desktop_ip_addr:str ):
        return desktop_ip_addr + ':' + str(DEFAULT_PULSE_TCP_PORT)

    def get_CUPS_SERVER( self, desktop_ip_addr:str ):
        return desktop_ip_addr + ':' + str(DEFAULT_CUPS_TCP_PORT)

    def get_nodeSelector( self ):
        """get_nodeSelector

        Returns:
            dict: dict of nodeSelector for self.type 

        """
        nodeSelector = oc.od.settings.desktop_pod.get(self.type, {}).get('nodeSelector',{})
        return nodeSelector
    
    def get_appnodeSelector( self, authinfo:AuthInfo, userinfo:AuthUser,  app:dict ):
        """get_appnodeSelector
            get the node selector merged data from 
            desktop.pod['pod_application'] + app['nodeSelector']
        Args:
            app (dict): application dict 

        Returns:
            dict: dict 
        """
        assert isinstance(app, dict),  f"app has invalid type {type(app)}"
        nodeSelector = {}
        executeclassname =  app.get('executeclassname')
        self.logger.debug( f"app name={app.get('name')} has executeclassname={executeclassname}")
        executeclass = self.orchestrator.get_executeclasse( authinfo, userinfo, executeclassname )
        executeclass_nodeSelector = executeclass.get('nodeSelector',{}) or {}
        nodeSelector.update(executeclass_nodeSelector)
        self.logger.debug( f"nodeSelector for name={app.get('name')} is nodeSelector={nodeSelector}")
        return nodeSelector

    def list( self, authinfo, userinfo, myDesktop, phase_filter=[ 'Running', 'Waiting'], apps=None ):
        self.logger.info('')

        assert isinstance(authinfo,   AuthInfo),   f"authinfo has invalid type {type(authinfo)}"
        assert isinstance(userinfo,   AuthUser),   f"userinfo has invalid type {type(userinfo)}"
        assert isinstance(myDesktop, ODDesktop),   f"invalid desktop parameter {type(myDesktop)}"
        assert isinstance(phase_filter,  list),    f"invalid phase_filter parameter {type(phase_filter)}"

        result = []
        access_userid = userinfo.userid
        access_provider = authinfo.provider
        try:
            field_selector = ''
            label_selector = 'access_userid=' + access_userid + ',type=' + self.type
            label_selector += ',access_provider='  + access_provider

            # use list_namespaced_pod to filter user pod
            myPodList = self.orchestrator.kubeapi.list_namespaced_pod(self.orchestrator.namespace, label_selector=label_selector, field_selector=field_selector)
            if isinstance( myPodList, V1PodList ):
                for myPod in myPodList.items:
                    phase = myPod.status.phase
                    # keep only Running pod
                    if myPod.metadata.deletion_timestamp is not None:
                        phase = 'Terminating'

                    app = {}
                    if isinstance(apps, ODApps):
                        if isinstance( myPod.spec.containers, list):
                            if isinstance( myPod.spec.containers[0], V1Container ):
                                app = apps.find_app_by_id( myPod.spec.containers[0].image ) or {}

                    mycontainer = {}
                    if phase in phase_filter:
                        #
                        # convert a container to json by filter entries
                        mycontainer['podname']  = myPod.metadata.name
                        mycontainer['id']       = myPod.metadata.name # myPod.metadata.uid
                        mycontainer['short_id'] = myPod.metadata.name
                        mycontainer['status']   = myPod.status.phase
                        mycontainer['image']    = myPod.spec.containers[0].image
                        mycontainer['oc.path']  = myPod.spec.containers[0].command
                        mycontainer['nodehostname'] = myPod.spec.node_name
                        mycontainer['architecture'] = app.get('architecture')
                        mycontainer['os']           = app.get('os')
                        mycontainer['oc.icondata']  = app.get('icondata')
                        mycontainer['oc.args']      = app.get('args')
                        mycontainer['oc.icon']      = app.get('icon')
                        mycontainer['oc.launch']    = app.get('launch')
                        mycontainer['oc.displayname'] = app.get('displayname')
                        mycontainer['runtime']      = 'kubernetes'
                        mycontainer['type']         = self.type
                        mycontainer['status']       = phase
                        # add the object to the result array
                        result.append( mycontainer )
        except ApiException as e:
            self.logger.info(f"Exception when calling list_namespaced_pod:{e}")
        return result


    def envContainerApp( self, authinfo:AuthInfo, userinfo:AuthUser, pod_name:str, containerid:str )->dict:
        '''get the environment vars exec for the containerid '''
        env_result = None

        # define filters
        access_userid = userinfo.userid
        access_provider = authinfo.provider
        field_selector = f"metadata.name={pod_name}"
        label_selector = f"access_userid={access_userid},type={self.type},access_provider={access_provider}"

        myPodList = self.orchestrator.kubeapi.list_namespaced_pod(
            self.orchestrator.namespace, 
            label_selector=label_selector, 
            field_selector=field_selector)

        if isinstance( myPodList, V1PodList ) and len(myPodList.items) > 0 :
            local_env = myPodList.items[0].spec.containers[0].env
            env_result = {}
            #  convert name= value= to dict
            for e in local_env:
                if isinstance( e, V1EnvVar ):
                    env_result[ e.name ] =  e.value
        return env_result

    def logContainerApp(self, pod_name:str, container_name:str)->str:
        assert isinstance(pod_name,  str),  f"pod_name has invalid type  {type(pod_name)}"
        assert isinstance(container_name,  str),  f"container_name has invalid type {type(container_name)}"
        strlogs = 'no logs read'
        try:
            strlogs = self.orchestrator.kubeapi.read_namespaced_pod_log( 
                name=pod_name, 
                namespace=self.orchestrator.namespace, 
                container=container_name, 
                pretty='true' )
        except ApiException as e:
            self.logger.error( e )
        except Exception as e:
            self.logger.error( e )
        return strlogs

    def stop( self, pod_name, container_name:None ):
        '''get the user's containerid stdout and stderr'''
        result = None
        propagation_policy = 'Foreground'
        grace_period_seconds = 0
        delete_options = V1DeleteOptions(
            propagation_policy = propagation_policy, 
            grace_period_seconds=grace_period_seconds )

        v1status = self.orchestrator.kubeapi.delete_namespaced_pod(  
            name=pod_name,
            namespace=self.orchestrator.namespace,
            body=delete_options,
            propagation_policy=propagation_policy )

        result = isinstance( v1status, V1Pod ) or isinstance(v1status,V1Status)

        return result


    def removeAppInstanceKubernetesPod( self, authinfo, userinfo ):
        '''get the user's containerid stdout and stderr'''
        result = True
        access_userid = userinfo.userid
        access_provider = authinfo.provider
        label_selector = f"access_userid={access_userid},type={self.type},access_provider={access_provider}"

        myPodList = self.orchestrator.kubeapi.list_namespaced_pod(self.orchestrator.namespace, label_selector=label_selector)
        if isinstance( myPodList, V1PodList ) and len(myPodList.items) > 0 :
            for pod in myPodList.items:
                # propagation_policy = 'Background'
                propagation_policy = 'Foreground'
                grace_period_seconds = 0
                delete_options = V1DeleteOptions( 
                    propagation_policy = propagation_policy, 
                    grace_period_seconds=grace_period_seconds )
                try:
                    v1status = self.orchestrator.kubeapi.delete_namespaced_pod(  
                        name=pod.metadata.name,
                        namespace=self.orchestrator.namespace,
                        body=delete_options,
                        propagation_policy=propagation_policy )
                    result = isinstance( v1status, V1Pod ) and result
                except Exception as e:
                    self.logger.error( e )

        return result

    def list_and_stop( self, authinfo, userinfo, pod_name ):
        '''get the user's containerid stdout and stderr'''
        result = None
        access_userid = userinfo.userid
        access_provider = authinfo.provider
        field_selector = f"metadata.name={pod_name}"
        label_selector = f"access_userid={access_userid},type={self.type},access_provider={access_provider}"

        myPodList = self.orchestrator.kubeapi.list_namespaced_pod(self.orchestrator.namespace, label_selector=label_selector, field_selector=field_selector)
        if isinstance( myPodList, V1PodList ) and len(myPodList.items) > 0 :
            # propagation_policy = 'Background'
            propagation_policy = 'Foreground'
            grace_period_seconds = 0
            delete_options = V1DeleteOptions( 
                propagation_policy = propagation_policy, 
                grace_period_seconds=grace_period_seconds )

            v1status = self.kubeapi.delete_namespaced_pod(  
                name=pod_name,
                namespace=self.orchestrator.namespace,
                body=delete_options,
                propagation_policy=propagation_policy )

            result = isinstance( v1status, V1Pod ) or isinstance(v1status,V1Status)

        return result

    def findRunningPodforUserandImage( self, authinfo, userinfo, app):
        self.logger.info('')

        myrunningPodList = []
        access_userid = userinfo.userid
        access_provider = authinfo.provider
        try: 
            field_selector = ''
            label_selector = f"access_userid={access_userid},type={self.type}"
            if isinstance(app.get('uniquerunkey'), str ):
                label_selector += f",uniquerunkey={app.get('uniquerunkey')}"

            if oc.od.settings.desktop['authproviderneverchange'] is True:
                label_selector += f",access_provider={access_provider}"

            myPodList = self.orchestrator.kubeapi.list_namespaced_pod(
                self.orchestrator.namespace, 
                label_selector=label_selector, 
                field_selector=field_selector
            )

            if len(myPodList.items)> 0:
                for myPod in myPodList.items:
                    myPhase = myPod.status.phase
                    # keep only Running pod
                    if myPod.metadata.deletion_timestamp is not None:
                       myPhase = 'Terminating'
                    if myPhase != 'Running':
                       continue # This pod is Terminating or not Running, skip it
                    myrunningPodList.append(myPod)
        except ApiException as e:
            self.logger.info(f"Exception when calling list_namespaced_pod: {e}")
        return myrunningPodList


    def findRunningAppInstanceforUserandImage( self, authinfo, userinfo, app):
        pod = None
        podlist = self.findRunningPodforUserandImage( authinfo, userinfo, app)
        if len(podlist) > 0:
            pod = podlist[0]
            pod.id = pod.metadata.name # add an id for container compatibility
        return pod

    def create(self, myDesktop, app, authinfo, userinfo={}, userargs=None, **kwargs ):
        self.logger.debug('')

        rules = app.get('rules', {}) or {} # app['rules] can be set to None
        desktop_rules = oc.od.settings.desktop['policies'].get('rules')
        if isinstance( desktop_rules, dict ):
            rules.update( desktop_rules )
        network_config = self.orchestrator.applyappinstancerules_network( authinfo, rules )

        (volumeBinds, volumeMounts) = self.orchestrator.build_volumes(   
            authinfo,
            userinfo,
            volume_type='pod_application',
            secrets_requirement=app.get('secrets_requirement'),
            rules=rules,
            **kwargs)

        list_volumeBinds = list( volumeBinds.values() )
        list_volumeMounts = list( volumeMounts.values() )
        self.logger.debug( f"list volume binds pod desktop {list_volumeBinds}")
        self.logger.debug( f"list volume mounts pod desktop {list_volumeMounts}")

        # apply network rules
        # network_config = self.applyappinstancerules_network( authinfo, rules )
        # apply homedir rules
        # homedir_disabled = self.applyappinstancerules_homedir( authinfo, rules )
        envlist = self.get_env_for_appinstance( myDesktop, app, authinfo, userinfo, userargs, **kwargs )

        command = [ '/composer/appli-docker-entrypoint.sh' ]
        labels = {
            'access_providertype':  authinfo.providertype,
            'access_provider':  authinfo.provider,
            'access_userid':    userinfo.userid,
            'access_username':  self.orchestrator.get_labelvalue(userinfo.name),
            'type':             self.type,
            'uniquerunkey':     app.get('uniquerunkey')
        }

        myuuid = oc.lib.uuid_digits()
        pod_sufix = 'app_' + app['name'] + '_' +  myuuid
        app_pod_name = self.orchestrator.get_podname( authinfo, userinfo, pod_sufix)

        # default empty dict annotations
        annotations = {}
        # Check if a network annotations exists
        network_annotations = network_config.get( 'annotations' )
        if isinstance( network_annotations, dict):
            annotations.update( network_annotations )

        # get the node selector merged data from desktop.pod['pod_application'] and app['nodeSelector']
        nodeSelector = self.get_appnodeSelector( authinfo, userinfo, app)
        securitycontext = self.get_securitycontext( authinfo, userinfo, app )
        workingDir = self.orchestrator.get_user_homedirectory( authinfo, userinfo )
        resources = self.get_resources( authinfo, userinfo, app )
        affinity = self.get_affinity( authinfo, userinfo, app, myDesktop )

        # init container for the pod apps 
        # to fix ownership of the homedir like desktop does
        initContainers = []
        currentcontainertype = 'init'
        init_command = self.orchestrator.buildinitcommand( authinfo, userinfo, list_volumeBinds, list_volumeMounts )
        self.logger.debug(f"init command={init_command}")
        init_container = self.orchestrator.addcontainertopod( 
            authinfo=authinfo, 
            userinfo=userinfo, 
            currentcontainertype=currentcontainertype, 
            command=init_command,
            myuuid=myuuid,
            envlist=envlist,
            list_volumeMounts=list_volumeMounts
        )
        initContainers.append( init_container )
        self.logger.debug( f"pod container added {currentcontainertype}" )


        # update envlist
        # add EXECUTION CONTEXT env var inside the container
        envlist.append( { 'name': 'ABCDESKTOP_EXECUTE_RUNTIME',   'value': self.type} )
        envlist.append( { 'name': 'ABCDESKTOP_EXECUTE_RESOURCES', 'value': json.dumps(resources) } )

        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name':         app_pod_name,
                'namespace':    self.orchestrator.namespace,
                'labels':       labels,
                'annotations':  annotations
            },
            'spec': {
                'terminationGracePeriodSeconds': 0,  # Time to wait before moving from a TERM signal to the pod's main process to a KILL signal.
                'restartPolicy' : 'Never',
                'securityContext': securitycontext,
                'affinity': affinity,
                'automountServiceAccountToken': False,  # disable service account inside pod
                'volumes': list_volumeBinds,
                'nodeSelector': nodeSelector,
                'initContainers': initContainers,
                'tolerations': oc.od.settings.desktop_pod[self.type].get('tolerations'),
                'containers': [ {   
                    'imagePullSecrets': oc.od.settings.desktop_pod[self.type].get('imagePullSecrets'),
                    'imagePullPolicy':  oc.od.settings.desktop_pod[self.type].get('imagePullPolicy','IfNotPresent'),
                    'image': app['id'],
                    'name': app_pod_name,
                    'command': command,
                    'env': envlist,
                    'volumeMounts': list_volumeMounts,
                    'resources': resources,
                    'workingDir' : workingDir
                } ]
            }
        }

        self.logger.info( 'dump yaml %s', json.dumps( pod_manifest, indent=2 ) )
        try:
            pod = self.orchestrator.kubeapi.create_namespaced_pod(
                namespace=self.orchestrator.namespace,
                body=pod_manifest )
        except ApiException as e:
            self.logger.error('== ApiException ==')
            self.logger.error(e)
            message = oc.lib.try_to_read_json_entry( 'message', e.body )
            self.logger.debug(f"message={message}")
            raise ODError( status=500, message=message )
        except Exception as e:
            self.logger.error('== Exception ==')
            self.logger.error(e)
            raise ODError( status=500, message=str(e) )
        
        if not isinstance(pod, V1Pod ):
            raise ValueError( f"Invalid create_namespaced_pod type return {type(pod)} V1Pod is expecting")
        
        send_previous_pulling_message = False
        # watch list_namespaced_event
        w = watch.Watch()                 
        for event in w.stream(  self.orchestrator.kubeapi.list_namespaced_event, 
                                namespace=self.orchestrator.namespace, 
                                timeout_seconds=oc.od.settings.desktop['K8S_CREATE_POD_TIMEOUT_SECONDS'],
                                field_selector=f'involvedObject.name={app_pod_name}' ):  
            # safe type check 
            if not isinstance(event, dict ): continue
            if not isinstance(event.get('object'), CoreV1Event ): continue

            # Valid values for event types (new types could be added in future)
            #    EventTypeNormal  string = "Normal"     // Information only and will not cause any problems
            #    EventTypeWarning string = "Warning"    // These events are to warn that something might go wrong

            event_object = event.get('object')
            self.logger.debug(f"{event_object.type} reason={event_object.reason} message={event_object.message}")

            # data for notify_user
            data = { 
                'message':  app.get('name'), 
                'name':     app.get('name'),
                'icondata': app.get('icondata'),
                'icon':     app.get('icon'),
                'image':    app.get('id'),
                'launch':   app.get('launch')
            }
            if event_object.type == 'Normal':
                if event_object.reason == 'Pulling':
                    send_previous_pulling_message = True
                    data['message'] =  f"{event_object.reason} {app.get('name')}, please wait"
                    self.orchestrator.notify_user( myDesktop, 'container', data )
                elif event_object.reason == 'Pulled':
                    if send_previous_pulling_message is True:
                        data['message'] =  f"{app.get('name')} is {event_object.reason.lower()}"
                        self.orchestrator.notify_user( myDesktop, 'container', data )
                elif event_object.reason == 'Started': 
                    w.stop()
                elif event_object.reason in [ 'Scheduled', 'Created' ]:
                    pass
                else:
                    data['message'] =  f"{event_object.reason} {event_object.message}"
                    self.orchestrator.notify_user( myDesktop, 'container', data )
                    self.logger.error(f"{event_object.type} reason={event_object.reason} message={event_object.message}")
                    w.stop()
                
            else: # event_object.type == 'Warning':
                # an error occurs
                data['name'] = event_object.type
                data['message'] = event_object.reason
                self.orchestrator.notify_user( myDesktop, 'container', data )
                w.stop()
        

        self.logger.debug('watch list_namespaced_pod creating, waiting for pod quit Pending phase' )
        w = watch.Watch()                 
        for event in w.stream(  self.orchestrator.kubeapi.list_namespaced_pod, 
                                namespace=self.orchestrator.namespace, 
                                timeout_seconds=oc.od.settings.desktop['K8S_CREATE_POD_TIMEOUT_SECONDS'],
                                field_selector=f"metadata.name={app_pod_name}" ):   
            # event must be a dict, else continue
            if not isinstance(event,dict):
                self.logger.error( f"event type is {type( event )}, and should be a dict, skipping event")
                continue

            self.logger.debug( f"event type is {event.get('type')}")
            # event dict must contain a pod object 
            pod_event = event.get('object')
            # if podevent type must be a V1Pod, we use kubeapi.list_namespaced_pod
            if not isinstance( pod_event, V1Pod ): continue
            if not isinstance( pod_event.status, V1PodStatus ): continue
           
            self.logger.info( f"event_object.type={event_object.type} pod_event.status.phase={pod_event.status.phase} event_object.reason={event_object.reason}")
            #
            # from https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
            # possible values for phase
            # Pending	The Pod has been accepted by the Kubernetes cluster, but one or more of the containers has not been set up and made ready to run. This includes time a Pod spends waiting to be scheduled as well as the time spent downloading container images over the network.
            # Running	The Pod has been bound to a node, and all of the containers have been created. At least one container is still running, or is in the process of starting or restarting.
            # Succeeded	All containers in the Pod have terminated in success, and will not be restarted.
            # Failed	All containers in the Pod have terminated, and at least one container has terminated in failure.
            # Unknown	For some reason the state of the Pod could not be obtained. This phase typically occurs due to an error in communicating with the node where the Pod should be running.
            if pod_event.status.phase == 'Running' :
                w.stop()
                continue

            # pod data object is complete, stop reading event
            # phase can be 'Running' 'Succeeded' 'Failed' 'Unknown'
            data = { 
                'message':  app.get('name'), 
                'name':     app.get('name'),
                'icondata': app.get('icondata'),
                'icon':     app.get('icon'),
                'image':    app.get('id'),
                'launch':   app.get('launch')
            }

            '''
            if pod_event.status.phase == 'Pending':
                if event_object.reason not in ['Created', 'Pulling', 'Pulled', 'Scheduled', 'Started' ]:
                    data['name'] = event_object.type
                    data['message'] = event_object.reason
                    self.orchestrator.notify_user( myDesktop, 'container', data )
                    w.stop()
            '''

            if event_object.type == 'Warning':
                data['name'] = event_object.type
                data['message'] = event_object.reason
                self.orchestrator.notify_user( myDesktop, 'container', data )
                w.stop()
            elif pod_event.status.phase in [ 'Failed', 'Unknown'] :
                # pod data object is complete, stop reading event
                # phase can be 'Running' 'Succeeded' 'Failed' 'Unknown'
                # an error occurs
                data['name'] = event_object.type
                data['message'] = event_object.reason
                self.orchestrator.notify_user( myDesktop, 'container', data )
                self.logger.debug(f"The pod is not in Pending phase, phase={pod_event.status.phase} stop watching" )
                w.stop()

        pod = self.orchestrator.kubeapi.read_namespaced_pod(namespace=self.orchestrator.namespace,name=app_pod_name)
        if not isinstance( pod, V1Pod ):
            raise ODError( status=500, message='Can not create pod')
                        
        # set desktop web hook
        # webhook is None if network_config.get('context_network_webhook') is None
        fillednetworkconfig = self.orchestrator.filldictcontextvalue(   
            authinfo=authinfo,
            userinfo=userinfo,
            desktop=myDesktop,
            network_config=network_config,
            network_name = None,
            appinstance_id = None )

        appinstancestatus = oc.od.appinstancestatus.ODAppInstanceStatus(
            id=pod.metadata.name,
            message=pod.status.phase,
            webhook = fillednetworkconfig.get('webhook'),
            type=self.type
        )
        
        return appinstancestatus
