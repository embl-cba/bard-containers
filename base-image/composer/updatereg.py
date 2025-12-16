#!/usr/bin/python3

def updateservice( sourcefilename, service, lookforline, replaceline, targetfilename=None ):
  f = open(sourcefilename)
  content = f.readlines()
  f.close()
  maxline = len(content)
  i=0
  while(i<maxline):
      if content[i].startswith(service):
        while(i < maxline):
            if content[i].startswith(lookforline):
                content[i] = replaceline
                break
            i = i + 1
      i = i + 1
  if targetfilename is None:
      targetfilename = sourcefilename
  f = open(targetfilename, 'w+')
  for line in content:
   f.write(line)
  f.close()
  

def main():
    targetfilename= 'toto.reg'
    systemreg = '/composer/PlayOnLinux/wineprefix/putty/system.reg' 
    disableservices = [  
             '[System\\\\CurrentControlSet\\\\Services\\\\MSIServer]',
             '[System\\\\CurrentControlSet\\\\Services\\\\MountMgr]',
             '[System\\\\CurrentControlSet\\\\Services\\\\PlugPlay]',
             '[System\\\\CurrentControlSet\\\\Services\\\\Schedule]',
             '[System\\\\CurrentControlSet\\\\Services\\\\StiSvc]',
             '[System\\\\CurrentControlSet\\\\Services\\\\TermService]',
             '[System\\\\CurrentControlSet\\\\Services\\\\winebus]',
             '[System\\\\CurrentControlSet\\\\Services\\\\Winmgmt]',
             '[System\\\\CurrentControlSet\\\\Services\\\\wuauserv]'] 

    for service in disableservices:
        updateservice( systemreg, service, '"Start"=dword:00000003', '"Start"=dword:00000004\n' )

if __name__ == "__main__":
    main()
