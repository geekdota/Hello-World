#coding:utf-8
#Ver 20170908
import time
import sys
import re
import urllib2
import urllib
import cookielib
#from socket import *
import socket  
import os
import re
import subprocess
import threading
import ssl
import gzip, binascii, os
import signal
from cStringIO import StringIO

reload(sys)  
sys.setdefaultencoding("utf8")

ssl._create_default_https_context = ssl._create_unverified_context
#####################################################

loginurl = 'http://localhost/cgi-bin/luci/'

IntervalFlag=0

def gzip_compress(raw_data):
    buf = StringIO()
    f = gzip.GzipFile(mode='wb', fileobj=buf)
    try:
        f.write(raw_data)
    finally:
        f.close()
    return buf.getvalue()

def gzip_uncompress(c_data):
    buf = StringIO(c_data)
    f = gzip.GzipFile(mode = 'rb', fileobj = buf)
    try:
        r_data = f.read()
    finally:
        f.close()
    return r_data



def GetContent(Lines,Split1,Split2):
    for Line in Lines:
        Temp=Line.split(Split1)
#        print Temp
        if len(Temp)==1:
            continue
        else:
            Temp=Temp[1].split(Split2)
#            print Temp
            return Temp[0] 

def LogSave(FileName,LogSource):
	file_object = open(FileName,'w')                                                                   
	file_object.writelines(LogSource)                                                                   
	file_object.close()
	#print FileName+LogSource

		
def LogApluse(FileName,LogSource):
	file_object=None
	try:
		filesize = os.path.getsize(FileName)
		if(filesize>=10240):                                                                                                                                                                   
			os.remove(FileName)     
	except Exception, e:
		print 'LogApluse false: '+str(e)
	try:
		temptime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))                                        
        	file_object = open(FileName,'a+')                          
        	file_object.writelines(temptime+' '+LogSource+'\n')
	except Exception, e:
		print 'LogApluse false: '+str(e)
	finally: 
		if(file_object!=None):                        
        		file_object.close()
	#temptime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	#print temptime+' '+FileName+' '+LogSource

def GetBootTime():
	TimeStemp=float(time.time())
	#print TimeStemp
	f = open("/proc/uptime")
	con = f.read().split()
	f.close()
	UpSec = float(con[0])
#	print UpSec
	#LogApluse('/root/HeartBeat/BootTime','UpSec: '+str(UpSec))
	if(UpSec > 120):
		try:
			file_object = None                                        
                	file_object = open('/root/HeartBeat/BootTime','r')                     
                	TempBoot=file_object.read()                    
                	TempBoot=TempBoot.split('\n')                           
                	TempBoot=TempBoot[0]
			BootTime=float(TempBoot)
		except Exception, e: 
			print 'error'
			LogApluse('/root/HeartBeat/RawLog','BootTime Read Fail  '+str(e))
			BootTime=TimeStemp-UpSec
			#LogSave('/root/HeartBeat/BootTime',str(BootTime))
		finally:                                                
			if(file_object!=None):                          
				file_object.close()
		BootTime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(BootTime))
		#LogApluse('/root/HeartBeat/BootTime','BootTime: '+BootTime)
	else:
		print 'first'
		BootTime=TimeStemp-UpSec
		LogSave('/root/HeartBeat/BootTime',str(BootTime))
		LogApluse('/root/HeartBeat/BootTimeLog','FirstBootTime: '+BootTime)
		BootTime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(BootTime))


	LogApluse('/root/HeartBeat/BootTimeLog','BootTime: '+BootTime)
	return  BootTime





class ParamSelf(object):                                                          
	def __init__(self):                                                        
        	self.IPSelf    ='192.168.1.1'                                       
        	self.MacSelf   ='11:22:33:44:55:66'
		self.ClientName='client1'
		self.BootTime=''
	def GetParam(self,ClientName):
		self.ClientName=ClientName

		TempPipe=os.popen('ifconfig br-lan |grep HWaddr')                                                                               
		MeshMac=TempPipe.readlines()                                                                                                   
		Temp= GetContent(MeshMac,'HWaddr ','\n')
		if(Temp!=None):
			self.MacSelf= Temp
   
		TempPipe=os.popen("ifconfig br-lan |grep 'inet addr'")                                                                               
		MeshMac=TempPipe.readlines()                                                                                                   
		Temp= GetContent(MeshMac,'inet addr:',' ')
		if(Temp!=None):
			self.IPSelf= Temp
		self.BootTime=GetBootTime()
    	def PrintParam(self):
		print 'self.IPSelf: '+self.IPSelf
		print 'self.MacSelf: '+self.MacSelf
		print 'self.ClientName: '+self.ClientName
		print 'self.BootTime: '+self.BootTime 
	def CoverSelfMess(self,Message,InfoType):
#		print Message
		NewMessage='{"Version":"'+'V20170822'+'",'
		NewMessage=NewMessage+'"ClientName":"'+self.ClientName+'",'
		NewMessage=NewMessage+'"InfoType":"'+InfoType+'",'
		NewMessage=NewMessage+'"IPSelf":"'+self.IPSelf+'",'
		NewMessage=NewMessage+'"MacSelf":"'+self.MacSelf+'",'
		NewMessage=NewMessage+'"BootTime":"'+self.BootTime+'",'
		NewMessage=NewMessage+'"JsonContent":'+Message+'}\n'
		return NewMessage
		
	

                                                                                    
	
		
	  	
	                   

class ParamC(object):
    def __init__(self):
        self.ServiceIP   = '192.168.4.9'
        self.ServicePort = 8080
	self.ProInterval = 5
	self.MeshInterval= 5
	self.NdpiInterval= 5
	self.CompressAlg=0
	self.ClientName='Client1'
	self.Renable=0
    def PrintParam(self):
	print 'self.ServiceIP'+self.ServiceIP  
        print 'self.ServicePort'+str(self.ServicePort)           
        print 'self.ProInterval'+str(self.ProInterval)              
        print 'self.MeshInterval'+str(self.MeshInterval)
	print 'self.NdpiInterval'+str(self.NdpiInterval)              
	print 'self.CompressAlg'+str(self.CompressAlg)              
	print 'self.ClientName'+self.ClientName
	print 'self.Renable '+self.Renable              
    def GetParam(self):
        try:
            file_object = open('/etc/config/HeartBeat','r')
            FileLines=file_object.readlines()
            Temp=GetContent(FileLines,'ServiceIP \'','\'\n')
            if Temp!=None:
                self.ServiceIP=Temp
            else:
		LogApluse('/root/HeartBeat/RawLog','Param IP Wrong')

            Temp=GetContent(FileLines,'ClientName \'','\'\n')
            if Temp!=None:
                self.ClientName=Temp
            else:
		LogApluse('/root/HeartBeat/RawLog','ClientName Wrong')

            Temp=GetContent(FileLines,'ServicePort \'','\'\n')
            if Temp!=None:
                self.ServicePort=int(Temp)
            else:
		LogApluse('/root/HeartBeat/RawLog','Param Port Wrong')

            Temp=GetContent(FileLines,'ProInterval \'','\'\n')
            if Temp!=None:
                self.ProInterval=int(Temp)
            else:
		LogApluse('/root/HeartBeat/RawLog','Param ProInterval Wrong')

            Temp=GetContent(FileLines,'MeshInterval \'','\'\n')
            if Temp!=None:
                self.MeshInterval=int(Temp)
            else:
		LogApluse('/root/HeartBeat/RawLog','Param MeshInterval Wrong')
	     
            Temp=GetContent(FileLines,'NdpiInterval \'','\'\n')
            if Temp!=None:
                self.NdpiInterval=int(Temp)
            else:
		LogApluse('/root/HeartBeat/RawLog','Param NdpiInterval Wrong')
	     
            Temp=GetContent(FileLines,'CompressAlg \'','\'\n')
            if Temp!=None:
                self.CompressAlg=int(Temp)
	    else:
		LogApluse('/root/HeartBeat/RawLog','Param CompressAlg Wrong')

            Temp=GetContent(FileLines,'Renable \'','\'\n')
            if Temp!=None:
                self.Renable=int(Temp)
	    else:
		LogApluse('/root/HeartBeat/RawLog','Param Renable Wrong')
		
#If file not exist
        except IOError,e:
            if e.errno==2:
#                print 'match'
                file_object = open('/etc/config/HeartBeat','w')
                file_object.writelines('config interface \'HeartBeat_Setting\'\n')
                file_object.writelines('	option ServiceIP \''+self.ServiceIP+'\'\n')
                file_object.writelines('	option ServicePort \''+str(self.ServicePort)+'\'\n')
		LogApluse('/root/HeartBeat/RawLog','Do not have configer text '+str(e))
            else:
		LogApluse('/root/HeartBeat/RawLog','FileOpen Fail  '+str(e))
#The last thing to do
        finally:
                file_object.close()#pay attention
    def SaveParam(self):
                file_object = open('/root/HeartBeat/HeartBeat','w')
                file_object.writelines('config interface \'HeartBeat_Setting\'\n')
                file_object.writelines('	IP: '+self.ServiceIP+'\n')
                file_object.writelines('	Port: '+str(self.ServicePort)+'\n')
                file_object.close()

class Login(object):
    def __init__(self):
        self.name = ''
        self.passwprd = ''
	self.Stok=''
        self.cj = cookielib.LWPCookieJar()            
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)) 
        urllib2.install_opener(self.opener)    

    def setLoginInfo(self,username,password):
        '''设置用户登录信息'''
        self.name = username
        self.pwd = password
 
    def login(self):
	try:
            loginparams = {'luci_username':self.name,'luci_password':self.pwd}
            headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Cache-Control':'max-age=0',
                    'Connection':'keep-alive',
                    'Content-Length':'37',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':'localhost',
                    'Origin':'http://localhost',
                    'Referer':'http://localhost/cgi-bin/luci',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
	    req = urllib2.Request(loginurl, urllib.urlencode(loginparams),headers=headers)
            response = self.opener.open(req)
            thePage = response.read()
	    self.Stok=response.geturl()
            self.Stok=self.Stok.split(loginurl)
            self.Stok=self.Stok[1]
        except urllib2.URLError, e: 
		LogApluse('/root/HeartBeat/RawLog','Login Request Error   '+str(len))
		return 7
#		exit()

def GetEntry(Command):
    SomeDump=[]                                                                                                              
    TempPipe=os.popen(Command)                                                                                  
    Templine=TempPipe.readline()                                                                                              
    TitlList=re.split('\t+|  +|\n',Templine)                                                                                  
    while True:                                                                                                               
        Templine=TempPipe.readline()                                                                                          
        if not Templine:                                                                                                      
                break                                                                                                         
        TempList=Templine.split()                                                                                             
#        print TempList                                                                                                        
        for i in range(len(TempList)):                                                                                        
                TempList[i]='"'+TempList[i]+'"'                                                                               
                TempList[i]='"'+TitlList[i]+'"'+':'+TempList[i]                                                                                                                      
        Templine=','.join(TempList)
#	print Templiine                                                                                           
        SomeDump.append(Templine)
    TempPipe.close()
    return SomeDump                                                                                             
#    print SomeDump              	                                                                                        
	
class CommandJson(object):	
	def GetMeshMessage(self):
		TempPipe=subprocess.Popen('ifconfig wlan1 | grep HWaddr',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		err=TempPipe.stderr.readlines()
		MeshMac=TempPipe.stdout.readlines()

		if(len(err)==0):
			MeshMac= GetContent(MeshMac,'HWaddr ','\n')
			if(len(MeshMac)==0):
				MeshMac='00:00:00:00:00:00'
		else:
			MeshMac='FF:FF:FF:FF:FF:FF'
			LogApluse('/root/HeartBeat/RawLog','Do not have wlan1')
			MeshInfo='MeshInfo: {"MeshSelfMac":'+MeshMac+'}'
			return MeshInfo

		MeshMac='"'+MeshMac+'"'
    		MpathDump=GetEntry('iw wlan1 mpath dump')                                                                                      
                
    		ProxyDump=GetEntry('iw wlan1 mpp dump')
                
		if(len(MpathDump)==0):
			LogApluse('/root/HeartBeat/RawLog','Do not have Mpath')
			MeshInfo='MeshInfo: {"MeshSelfMac":'+MeshMac+'}'
			return	MeshInfo                                                                                        
    		MeshInfo='{"MeshSelfMac":'+MeshMac+','
	                                                                        
	#    print MeshInfo                                                                                                                
                                                                                                                                
    		MeshInfo=MeshInfo+'"MeshMpath": ['                                                                                             
    		for i in range(len(MpathDump)-1):                                                                                              
        		MeshInfo=MeshInfo+'{'+MpathDump[i]+'},'
		if(len(ProxyDump)==0):
			MeshInfo=MeshInfo+'{'+MpathDump[i]+'}]}'
			return MeshInfo                                                                                    
    		MeshInfo=MeshInfo+'{'+MpathDump[i+1]+'}],'
                                                                                                                                                                                                          
    		MeshInfo=MeshInfo+'"MeshProxy": ['                                                                                             
    		for i in range(len(ProxyDump)-1):                                                                                              
        		MeshInfo=MeshInfo+'{'+ProxyDump[i]+'},'                                                                                    
    		MeshInfo=MeshInfo+'{'+ProxyDump[i+1]+'}]'                                                                                        
                                                                                                                                   
    		MeshInfo= MeshInfo+'}'                                                                                                         
                                                                                                                                   
    		return MeshInfo
	def SendMeshJson(self,sock,flag,sfparam):
		try:
			Message=self.GetMeshMessage()                                                                                                                                                                   
			if (flag==1):
				Message = gzip_compress(Message)
				#f = open("/root/HeartBeat/Meshtemp.gz",'wb')
    				#f.write(Message)
				#f.close()
			Message=sfparam.CoverSelfMess(Message,'MeshInfo')
			sock.sendall(Message)                                                                                                                                                                   
                        LogApluse('/root/HeartBeat/Log','Success sending MeshPath')
			return 0                                                                                                 
                except Exception, e:
#			print str(e)                                                                                                                                                                                               
                        LogApluse('/root/HeartBeat/RawLog','Send MeshJson fail'+str(e))                                                                                               
                        return 1                                                                                                                                               
				 
	
class ProfileJson(object):
	def __init__(self):
		self.HitList=['?status=1','/admin/status/realtime/bandwidth_status/br-lan']
		self.InsList=['Profile: ','Brlan: ']
		self.UrlList=[]
		self.userlogin=Login()
    		self.userlogin.setLoginInfo('root','root')
    		res=self.userlogin.login()
		#if(res==7):
	    		#LogSave('/root/HeartBeat/projson','7Login Exception  '+str(e)+'\n')

    		for element in self.HitList:                                                                                                                                                
    			self.UrlList.append(loginurl+self.userlogin.Stok+element)                                                                                                                               
	def JsonSend(self,sock,flag,sfparam):
		for i in range(len(self.UrlList)):
			try:
				#print self.UrlList[i]
				response=self.userlogin.opener.open(self.UrlList[i])
#				ThePage = self.InsList[i]
                    		ThePage = response.read()
				ThePage = sfparam.CoverSelfMess(ThePage,self.InsList[i])
#		   		ThePage = ThePage+'\r\n'
				if (flag==1):
					ThePage = gzip_compress(ThePage)
					#f = open("/root/HeartBeat/"+str(i)+"temp.gz",'wb')
    					#f.write(ThePage)
    					#f.close()
		    		try:                                                                                                                                     
                    			sock.sendall(ThePage)
#					print self.UrlList[i]                                                                                                                                 
	    				LogApluse('/root/HeartBeat/Log','Success sending ProfileJson'+self.UrlList[i])
                    		except Exception, e:
#					print str(e)                                                                                                                         
	    				LogApluse('/root/HeartBeat/RawLog','Send projson Exception  '+str(e))                                                                                                                         
					return 1
			except Exception,e:
	            		LogApluse('/root/HeartBeat/Log','Send Profile request err '+str(e))
				try:
                    			if e.code==403:
                        			self.userlogin.login()
						return 3
                    		except Exception, e:
					return 2
		return 0
		
		
class FileJson(object):
	def __init__(self):
		self.FileList=['/root/HeartBeat/ndpitemp']
		self.FreshNdpiFile(1)
		self.child
	def JsonSend(self,sock,flag,sfparam):
		for i in range(len(self.FileList)):
			try:    
				file_object = None
				file_object = open(self.FileList[i],'r')
				TempMess=file_object.read()
				TempMess=TempMess.split('\n')
				TempMess=TempMess[0]
				TempMessSend=sfparam.CoverSelfMess(TempMess,'nDPI')
				if (flag==1):
					TempFile = gzip_compress(TempMessSend)
					#f = open("/root/HeartBeat/ndpitemp.gz",'wb')
    					#f.write(TempFile)
    					#f.close()
                	except Exception, e:
#				print str(e)                                                                                                                                                                                               
                        	LogApluse('/root/HeartBeat/RawLog','File not exit '+str(e))                                                                                               
                        	return 2
			finally:
				if(file_object!=None):
					file_object.close()
			try:   
#				print TempMessSend 
				re=sock.sendall(TempMessSend)
#				print str(len(TempMessSend))
#				print str(re)                                                                                                                                                                   
				LogApluse('/root/HeartBeat/Log','Success sending File')
				return 0                                                                                                 
                	except Exception, e:
				print str(e)                                                                                                                                                                                               
                        	LogApluse('/root/HeartBeat/RawLog','Send FileJson Exception  '+str(e))                                                                                               
                        	return 1
	def FreshNdpiFile(self,second):
		nDPIcom='ndpiReader -i br-lan -v 2 -j /root/HeartBeat/ndpitemp -s '
		nDPIcom=nDPIcom+str(second)+' > /root/HeartBeat/ndpilog 2>>/root/HeartBeat/ndpilog'
#		print nDPIcom
		self.child=subprocess.Popen(nDPIcom,shell=True)		


class RecvState:
    def __init__(self): 
        self.RecvRun=0
        self.RecvRunning=1
        self.RecvQuiting=2
        self.RecvQuit=3

RecvEnmu=RecvState()

T1State=RecvEnmu.RecvQuit
Command=False
BUFSIZ = 1024
COMLEN = 20
IntervalTime = 0

def Recv_Thread(sock,test):
    global T1State
    global Command
    global IntervalTime
    Data=''  
    while True: 
#	print 'recv '+str(T1State)
        if(T1State==RecvEnmu.RecvRun):
#            print 'RecvRun'
            T1State=RecvEnmu.RecvRunning
        elif(T1State==RecvEnmu.RecvRunning):
            try:
#                print 'RecvRuning'
                Data=Data+sock.recv(BUFSIZ)
                DataLine=Data.split('\n')
#                print DataLine
                Data=DataLine[len(DataLine)-1]
                if(len(Data)>COMLEN):
                    Data=''
                for i in range(len(DataLine)-1):
                    if(Command==False):
                        if 'Command' in DataLine[i]:
                            Command=True
                            time.sleep(2)
                            sock.send('Ok\n')
                        else:   
                            LogSave('/root/HeartBeat/logRecvThread','In the wrong Position\n')                                                                                               
                    elif(Command==True): 
                            if 'Exit' in DataLine[i]:
                                Command=False
                                sock.send('Ok\n')  
                                sock.close()
                            	LogSave('/root/HeartBeat/logRecvThread','Exit by Reset\n')                                                                                               
				T1State=RecvEnmu.RecvQuit     
                                exit()
			    elif 'Sync' in DataLine[i]:  
				IntervalTime = 0
				sock.send('Ok\n')   
                            	LogSave('/root/HeartBeat/logRecvThread','Command Sync\n')                                                                                               
                            elif 'Decommand' in DataLine[i]:
                                sock.send('Ok\n')
                            	LogSave('/root/HeartBeat/logRecvThread','Exit Command mode\n')                                                                                               
                                Command=False
                            else:
                                #sock.send('You sent wrong conmmand'+DataLine[i])                  
                            	LogSave('/root/HeartBeat/logRecvThread','Wrong Command\n')                                                                                               
            except Exception,e: #recv can not catch break pipe
#                print str(e)
                LogSave('/root/HeartBeat/logRecvThread','Exit by Exception\n')                                                                                               
		T1State=RecvEnmu.RecvQuit     
                exit()
        elif(T1State==RecvEnmu.RecvQuiting):
            T1State=RecvEnmu.RecvQuit 
            LogSave('/root/HeartBeat/logRecvThread','Exit by Main\n')
#	    print 'exit by main'                                                                                               
            exit()


def GetByUCI(Command):
	res=None
	TempPipe=subprocess.Popen(Command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	Templine=TempPipe.stdout.read()
	if len(Templine)==0:
		print 'param wrong 0'
	else:
		res=Templine
		res=res.split('\n')
#	print res
	return res[0]


class WatchDog(object):
	def __init__(self):                              
        	self.Child=None             
        	self.TargetIp = '192.168.4.1'
		self.StartDelay=5
		self.FailTimes=10
		self.TargetTimes=10
		self.Counter=0
		self.State=0
		self.Enabled=0
		self.InterTime=10
	def GetParam(self):
		res=GetByUCI('uci get HeartBeat.WatchDog_Setting.Wenable')
		if res!=None:
			self.Enabled=int(res)
			#print self.Enabled
		else:
			LogApluse('/root/HeartBeat/WatchDog.txt','param Enabled  error ')

		res=GetByUCI('uci get HeartBeat.WatchDog_Setting.Wipaddress')
		if res!=None:
			self.TargetIp=res
			#print self.TargetIp
		else:
			LogApluse('/root/HeartBeat/WatchDog.txt','param TargetIp  error ')

		
		res=GetByUCI('uci get HeartBeat.WatchDog_Setting.Wintertime')
		if res!=None:
			self.InterTime=int(res)
			if(self.InterTime<10):
				self.InterTime=10
				LogApluse('/root/HeartBeat/WatchDog.txt','InterTime Lower than 10 ')
			#print self.InterTime
		else:
			LogApluse('/root/HeartBeat/WatchDog.txt','param InterTime  error ')
		
		
		res=GetByUCI('uci get HeartBeat.WatchDog_Setting.Wstartde')
		if res!=None:
			self.StartDelay=int(res)
			if(self.StartDelay<300):
				self.StartDelay=300
				LogApluse('/root/HeartBeat/WatchDog.txt','StartDelay Lower than 300 ')
			#print self.StartDelay
		else:
			LogApluse('/root/HeartBeat/WatchDog.txt','param DelayTime  error ')

		res=GetByUCI('uci get HeartBeat.WatchDog_Setting.Wfailtime')
		if res!=None:
			self.FailTimes=int(res)
			self.TargetTimes=int(res)
			if(self.FailTimes<5):
				self.FailTimes=5
				self.TargetTimes=5
				LogApluse('/root/HeartBeat/WatchDog.txt','FailTimes Lower than 5 ')

			#print self.FailTimes
		else:
			LogApluse('/root/HeartBeat/WatchDog.txt','param FailTimes  error ')
		
        	LogApluse('/root/HeartBeat/WatchDog.txt','WatchDogLog Enable='+str(self.Enabled)+'  ')                                                         

	def WatchDog(self):
		if(self.Enabled==0):	
			#print 'doing noting enable =0'
			return
		self.Counter=self.Counter + 1
#		print 'Counter:'+str(self.Counter)
#		print 'State:'+str(self.State)
		if(self.Counter<self.StartDelay):
#			print 'doing nothing Delay'
			return
		if(self.State==0):
#			print 'Start Child'
			#TempString="ping  -w "+str(self.InterTime)+' '+self.TargetIp+"|grep '100% packet loss'|wc -l"
			TempString="ping  -w "+str(self.InterTime)+' '+self.TargetIp
#			print TempString
			self.Child = subprocess.Popen(TempString,shell=True,stdout=subprocess.PIPE)
			self.State=1
		elif(self.State==1):
			#	child.wait()
                        if((self.Counter-self.StartDelay)<=self.InterTime):
#				print 'doing nothing WaitPingOver'
				return 
        		StrResult = self.Child.stdout.read()
			if '100% packet loss' in StrResult:
				result=1
			else:
				result=0
			try:
				result=int(result)
			except Exception, e:
		 		LogApluse('/root/HeartBeat/WatchDog.txt','Command exe fail  ')
				result=0
			#print result
			if(result==1):
		 		LogApluse('/root/HeartBeat/WatchDog.txt','Ping '+self.TargetIp+' Fail  ')
				self.FailTimes=self.FailTimes-1
				if(self.FailTimes==0):
					LogApluse('/root/HeartBeat/WatchDog.txt','rebooting   ')
					Child = subprocess.Popen('reboot',shell=True,stdout=subprocess.PIPE)
			else:
				StrResult=StrResult.split('\n')
				for i in range(len(StrResult)):
					#print StrResult[i]
					if 'round-trip' in StrResult[i]:
						#print 'find'
						LogApluse('/root/HeartBeat/WatchDogDelay.txt',StrResult[i])
				StrResult=''
				self.FailTimes=self.TargetTimes
			self.State=0
			self.Counter=self.StartDelay-1
			print 'FailTimes: '+str(self.FailTimes)

def Watch_Thread():
	watchdog=WatchDog() 
	watchdog.GetParam()
	while True:
		watchdog.WatchDog()
		time.sleep(1)


def Detect_Client():
	TempPipe=subprocess.Popen('ps | grep "python /root/HeartBeat/Client7.py"|grep -v "grep"|wc -l',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        Templine=TempPipe.stdout.read()
	Templine=int(Templine)
	if(Templine>1):
		 LogApluse('/root/HeartBeat/RawLog','Client overnumber :'+str(Templine))
	         exit()		

if __name__ == '__main__':

    Detect_Client()    
    param=ParamC()
    param.GetParam()
#   param.PrintParam()
    chat=None

    WatchTh = threading.Thread(target = Watch_Thread)                                                                  
    WatchTh.start()
    if(param.Renable==1):
	LogApluse('/root/HeartBeat/RawLog','Renable=1 ')
    else:
	LogApluse('/root/HeartBeat/RawLog','Renable==0 ')
	WatchTh.join()
	exit()
        

    projson=ProfileJson()
    commjson=CommandJson()
    filejson=FileJson()
    selfparam=ParamSelf()
    selfparam.GetParam(param.ClientName)
#    selfparam.PrintParam()

    arrayint=[param.MeshInterval,param.ProInterval,param.NdpiInterval]
    MaxInterval=1
    for i in range(len(arrayint)):
        if (arrayint[i]!=0):
            MaxInterval=MaxInterval*arrayint[i]
    MaxInterval=MaxInterval*10
#    print 'MaxIntercal is '+str(MaxInterval)

    while True:
        try:
	    LogApluse('/root/HeartBeat/RawLog','Start out Loop Again')
	    if(T1State!=RecvEnmu.RecvQuit):
		T1State=RecvEnmu.RecvQuiting
		if(chat!=None):
	    		chat.join()		
            Service=  (param.ServiceIP,param.ServicePort)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	    LogApluse('/root/HeartBeat/RawLog','Try connecting with '+param.ServiceIP+':'+str(param.ServicePort))
            s.connect(Service)
#	    print 'connect succeed'
            LogApluse('/root/HeartBeat/RawLog','Connect success')

#            chat = threading.Thread(target = Recv_Thread, args = (s,None))
            T1State=RecvEnmu.RecvRun    
#            chat.start()

            while True:
		if(Command==False):
			if param.ProInterval!=0:
				if IntervalTime%(param.ProInterval*10)==0:
#					print str(IntervalTime)+'   PRO'
					res=projson.JsonSend(s,param.CompressAlg,selfparam)
					if(res==1):
	    					LogApluse('/root/HeartBeat/RawLog','ProJson Send Socket Break')
#						print 'ProJson Send Socket break'
					        T1State=RecvEnmu.RecvQuiting
						s.shutdown(socket.SHUT_RDWR)
						s.close()
						time.sleep(5)
						break
			if param.MeshInterval!=0:
				if IntervalTime%(param.MeshInterval*10)==0:
#					print str(IntervalTime)+'   Mesh'
					res=commjson.SendMeshJson(s,param.CompressAlg,selfparam)
					if(res==1):
#						print 'CommJson Send Socket break'
	    					LogApluse('/root/HeartBeat/RawLog','CommJsoni Send Socket Break')
					        T1State=RecvEnmu.RecvQuiting
						s.shutdown(socket.SHUT_RDWR)
						s.close()
						time.sleep(5)
						break
			if param.NdpiInterval!=0:
				if IntervalTime%(param.NdpiInterval*10)==0:
#					print str(IntervalTime)+'   nDPI'
					filejson.child.send_signal(signal.SIGINT)
					filejson.child.wait()
					res=filejson.JsonSend(s,param.CompressAlg,selfparam)
					if(res==1):
#						print 'CommJson Send Socket break'
	    					LogApluse('/root/HeartBeat/RawLog','nDPI Send Socket Break')
					        T1State=RecvEnmu.RecvQuiting
						s.shutdown(socket.SHUT_RDWR)
						s.close()
						time.sleep(5)
						break
					filejson.FreshNdpiFile(param.NdpiInterval-1)			
		time.sleep(0.1)			
		IntervalTime=IntervalTime+1
	        if IntervalTime>=MaxInterval:
			IntervalTime=0

		#if(T1State!=RecvEnmu.RecvQuit):
			#s.shutdown(socket.SHUT_RDWR)    
			#s.close()
			#T1State=RecvEnmu.RecvQuiting
			#print 'exting1 '+str(T1State)		    
	    		#chat.join()
			#print 'exting'+str(T1State)		    
			#exit()

		
        except Exception, e:
#	    print str(e)
	    LogApluse('/root/HeartBeat/RawLog','Outer  '+str(e))
            time.sleep(20) 
	    s.close()
            continue 
