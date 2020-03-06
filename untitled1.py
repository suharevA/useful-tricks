import subprocess

partition = "/"
threshold = 80

df = subprocess.Popen(["df", '-h'], stdout=subprocess.PIPE, encoding='utf-8')  # look at the drive, I have /dev/sda


def check_disk():
    for line in df.stdout:
        splittings = line.split()
        if splittings[5] == partition:  # contact by number and make a cut
            if int(splittings[4][:-1]) > threshold:  # contact by number and make a cut
                result = subprocess.run(["docker system prune -f"])  # you can add any command
                print('complete docker prune')


check_disk()

               
   

              
                
                
    
    

            
            
    
    
    
 
