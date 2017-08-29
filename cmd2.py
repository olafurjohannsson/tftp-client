from client import TFTPClient
from socket import gethostname, gethostbyname
import os

def main():
    try:
        flag = True
        buffer = []

        host_name = gethostname()
        addr = (gethostbyname(host_name), host_name)

        (host, port) = input('Enter host:port --> ').split(':')
                      
        c = TFTPClient(host, port)

        if c:
            buffer.append('Connecting from host: {0} to host: {1}:{2}, mode: {3}'.format(addr, host, port, 'octet'))

            for p in range(len(buffer)):
                print(buffer.pop())
        else:
            flag = False
            print("Could not create TFTPClient() with: {0}:{1}".format(host, port))
        
        while flag:

            method = input('\nEnter read/r, write/w, quit/q --> ').lower()

            if method in ['quit', 'q']:
                buffer.append("Flag off")
                flag = False
                
            else:
                remote_file, local_file = input('Enter remote filename --> '), input('Enter local filename --> ')
            
                if method in ['read', 'r']:
                    if not remote_file:
                        raise Exception("Remote file is invalid!");
                    else:
                        if not local_file:
                            local_file = remote_file
                        if c.read(remote_file, local_file):
                            if '.' in os.path.splitext(local_file)[-1]:
                                if os.path.isfile(local_file):
                                    buffer.append("Successfully read file {0} from server {1}:{2} to path {3}/{4}".format(remote_file, host, port, os.getcwd(), local_file))
                    
                elif method in ['write', 'w']:
                    
                    if not os.path.isfile(local_file):
                        raise Exception("File %s does not exist!" % local_file)
                    else:
                        if not remote_file:
                            remote_file = local_file
                        if c.write(local_file, remote_file):
                            buffer.append("Successfully wrote file {0} from path {1} to server {2}:{3}/{4}".format(local_file, os.getcwd(), host, port, remote_file))
                        

            for i in range(len(buffer)):
                print(buffer.pop())
            
    except Exception as err:
        print("main.err: %s" % err)
        
    finally:
        print("Leaving. . .")


if __name__ == '__main__':
    main()
