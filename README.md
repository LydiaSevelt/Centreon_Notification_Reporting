Quick and dirty script to generate a report on all hosts and services and who they notify.  
  
Enter the password to your mysql database at the start of the script:  
DBPASSWD=""  
  
The script has four options:  
  
-h = display help  
-H = host report in csv format  
-S = service report in csv format  
no options = print out hosts and services in a human readable format  
  
Known Issues:  
	Currently assumes that any host/service with a template will inhert contacts and contact groups.  
