from socket import socket, setdefaulttimeout, AF_INET, SOCK_DGRAM, gethostname, gethostbyname
from tftp import *
import os, traceback, time


class TFTPClient(object):
    ''' Client that uses TFTP protocol to interface with a given server. GET and PUT are implemented (called read() and write() respectively.) '''


    NOT_FOUND = 'Could not find file'
    TIME_OUT = 'timed out'
    MAX_RETRY_COUNT = 0xff # 255 max retry count during transmission
    MAX_RUNS = 0xffffffff # 4294967295 total write() runs before shutting down prog
    MAX_TRANSFER = 2 << 14 # 32768 bytes is max transfer
    HEADER_SIZE = 2 << 1 # 4 bytes for header
    DATA_SIZE = 2 << 8 # 512 bytes for data
    BLK_SIZE = DATA_SIZE + HEADER_SIZE # 516 bytes
    
    
    def __init__(self, host, port=None):
        self.modes, self.opcodes = (TFTP_MODES, TFTP_OPCODES)
        setdefaulttimeout(3)                                    # default timeout=2seconds
        self.addr = (host, int(port) if port else 69)                # addrinfo (host, port)
        self.socket = socket(AF_INET, SOCK_DGRAM)              # create socket that uses datagrams for UDP
        self.log = TFTPLog                                      # lazy-load ctor without any args (are populated in later lifetime of obj)

        tftp_packets = TFTPPackets()                            # create instance of TFTPpackets class
        self.ack_packet = tftp_packets.ack_packet               # get unbound instance of function without invoking(i.e. just assign object, since functions are objects)
        self.request_packet = tftp_packets.request_packet       # get unbound instance of function without invoking(i.e. just assign object, since functions are objects)
        self.data_packet = tftp_packets.data_packet             # get unbound instance of function without invoking(i.e. just assign object, since functions are objects)


    def __str__(self):
        return "%s:%s" % (self.addr)                            # tostring formatting (if instance is called as str)


    def __del__(self):
        ''' tftpclient.desctructor '''

        if hasattr(self, 'log'):
            self.log("__del__", params=self, msg="Calling tftpclient.destructor and closing socket.")
        
        if hasattr(self, 'socket'):
            self.socket.close()

    def read(self, remote, local=None, mode='octet'):
        ''' Create a RRQ request to a server on open up a connectionless delivery of packets via udp datagrams. '''

        try:
            if not self.socket:
                self.socket = socket(AF_INET, SOCK_DGRAM)
            
            success = False

            if not remote:
                raise TFTPException("Remote file name cannot be empty.")

            if not local:
                local = remote                                                                          # If no local file name supplied, just use the same on we are getting from the server

            self.log("read", params=(remote, local, mode), msg="Initiating RRQ request to: %s port: %s" % (self.addr))

            opcode, packetnr = self.opcodes['read'], 1                                              # get RRQ opcode and start with packet nr 1 
            snd_buffer = self.request_packet(remote, mode, opcode)                                  # create RRQ packet

            # send first RRQ packet
            self.socket.sendto(snd_buffer, self.addr)                               # open a connection and send a udp datagram to a given host
            (rcv_buffer, (host, port)) = self.socket.recvfrom(self.BLK_SIZE)             # get response and addr_info
            rcv_total, retry_count = len(rcv_buffer), 0
            
            # Exec time of program
            start_time = time.time()

            # open a stream to write
            with open(local, 'wb+') as f:
                while True:
                    try:
                        if packetnr % 5000 == 0:
                                print("Total {0} received: {1}, execution time: {2} sec".format('KB', rcv_total / 1024, time.time() - start_time))
                            
                        if not host and port:
                            raise TFTPException("Host and port are invalid: %s:%s" % (host, port))
                        
                        if rcv_buffer[1] == self.opcodes['error']:
                            raise TFTPException(rcv_buffer[4:])

                        elif (((rcv_buffer[2] << 8) & 0xff00) + rcv_buffer[3]) == packetnr & 0xffff:
                            f.write(rcv_buffer[4:])                                                     # write our byte data, without the header

                            # Last packet was sent
                            if self.BLK_SIZE > len(rcv_buffer):                                         
                                break                                                                   

                            # Normal, continue to read from server
                            else:

                                # Create ACK packet
                                snd_buffer = self.ack_packet(packetnr)                                  
                                packetnr += 1
                                
                                # Send ACK packet
                                self.socket.sendto(snd_buffer, (host, port))                               # open a connection and send a udp datagram to a given host

                                # Get DATA packet and new TID
                                (rcv_buffer, (host, port)) = self.socket.recvfrom(self.BLK_SIZE)             # get response and addr_info
                                rcv_total += len(rcv_buffer)
                           
                    except Exception as err:
                        message = "Packetnr: {0}, retry count: {1}, header: {2}, error: {3}\ntraceback: {4}"
                        self.log("read: exception", params=(remote, local, mode), msg=message.format(packetnr, retry_count, rcv_buffer[:4], err,  traceback.format_exc()))
                        
                        if self.TIME_OUT in err.args:
                            retry_count += 1
                            
                            if retry_count >= self.MAX_RETRY_COUNT:
                                print("Retried max {0} times... leaving".format(retry_count))
                                break
                            else:
                                self.log("read: timeout exception", params=(remote, local, mode), msg=message.format(packetnr, retry_count, rcv_buffer[:4], err,  traceback.format_exc()))

                        elif self.NOT_FOUND in err.args:
                            print("File %s does not exist!" % remote)

                        # Unknown exception
                        else:
                            self.log("read", params=(local, remote, mode), msg="Unknown exception: %s" % err)


            success = True
            self.log("read finished", msg="Success in reading file {0} from host {1}, total bytes received: {2}, total retry counts: {3}, execution time: {4} seconds".format(remote, self.addr, rcv_total, retry_count, time.time() - start_time))


        except TFTPException as terr: # only catch TFTP specific err
            self.log("read: tftpexception", params=(remote, local, mode), msg="Error: {0}, traceback: {1}".format(err, traceback.format_exc()))
            
        except Exception as err:
            self.log("read: outerexception", params=(remote, local, mode), msg="Error: {0}, traceback: {1}".format(err, traceback.format_exc()))
        
        finally:
            pass

        return success


    # WRQ
    def write(self, local, remote=None, mode='octet'):
        ''' Create a WRQ request to a server  '''
        try:
            if not self.socket:
                self.socket = socket(AF_INET, SOCK_DGRAM)
                
            success = False
            
            if not local:
                raise TFTPException("Local file cannot be empty.")
            
            if not remote:
                remote = local

            # Get buffer from file handle
            file = open(local, 'rb+')
            file_buffer = file.read()

            self.log('write', params=(remote, local, mode), msg="Initiating WRQ request {0}/{1} of size {2} KB.".format(self.addr, remote, round(len(file_buffer)/1024)))

            # WRQ opcode and packet init
            opcode, packetnr = self.opcodes['write'], 0

            # Create a WRQ packet
            snd_buffer = self.request_packet(remote, mode, opcode)
            
            # Send WRQ packet
            self.socket.sendto(snd_buffer, self.addr)

            # Get back TID and first ACK packet
            (rcv_buffer, (host, port)) = self.socket.recvfrom(self.BLK_SIZE)
            
            start, retry_count, total_runs, start_time, timeout = 0, 0, 0, time.time(), False
            while True:
                try:
                    if total_runs == self.MAX_RUNS:
                        print("Max run count reached!")
                        break
                        
                    if packetnr % 5000 == 0:
                        print("Total {0} sent: {1}, execution time: {2} sec".format('KB', self.DATA_SIZE * total_runs , time.time() - start_time))

                    if not host and port:
                        raise TFTPException("Host and port are invalid: %s:%s" % (host, port))
                    
                    if rcv_buffer[1] == self.opcodes['error']:
                        raise TFTPException(rcv_buffer[4:].decode(), '')

                    # Verify ACK packet(4)                                                          # 0xffff - 0xff00 == 0xff
                    if rcv_buffer[1] == self.opcodes['ack'] and (((rcv_buffer[2] << 8) & 0xff00) + rcv_buffer[3]) == packetnr & 0xffff: # mask first 4 bytes
                        if not timeout:
                            # Get next DATA block to send
                            buffer = file_buffer[ start : (self.DATA_SIZE + start) ]
                            packetnr += 1

                        # Create DATA packet
                        snd_buffer = self.data_packet(packetnr, buffer)
                        
                        # Send DATA packet on new TID
                        self.socket.sendto(snd_buffer, (host, port))
                        
                        # Get ACK packet
                        (rcv_buffer, (host, port)) = self.socket.recvfrom(self.BLK_SIZE)
                        
                        timeout = False
                        start += self.DATA_SIZE

                    # If our DATA block is less than 516 bytes, then that was the last packet
                    if len(snd_buffer) < self.BLK_SIZE:
                        self.log("write end", msg="Ending write()");
                        break

                    total_runs += 1

                # Handle errors
                except Exception as err:
                    message = "Packetnr: {0}, retry count: {1}, header: {2}, error: {3}\ntraceback: {4}"
                    self.log("write exception", params=(remote, local, mode), msg=message.format(packetnr, retry_count, rcv_buffer[:4], err,  traceback.format_exc()))

                    # Handle timeouts
                    if self.TIME_OUT in err.args:
                        timeout = True
                        retry_count += 1

                        if retry_count >= self.MAX_RETRY_COUNT:
                            print("Max retried sends... leaving")
                            break
                        else:
                            self.log("writetimeout exception", params=(remote, local, mode), msg=message.format(packetnr, retry_count, rcv_buffer[:4], err,  traceback.format_exc()))

            success = True
            self.log("write success", params=(remote, local, mode), msg = "Success in writing file {0} to host {1}, total bytes sent: {2}, total retry counts: {3}, execution time: {4} seconds".format(remote, self.addr, len(file_buffer), retry_count, time.time() - start_time))
            

        # Handle TFTP specific errors
        except TFTPException as terr:
            self.log("write: tftpexception", params=(remote, local, mode), msg="Error: {0}, traceback: {1}".format(err, traceback.format_exc()))

        # Handle all other errors        
        except Exception as err:
            self.log("write: outerexception", params=(remote, local, mode), msg="Error: {0}, traceback: {1}".format(err, traceback.format_exc()))

        # Close resources
        finally:
            if file:
                file.close()

        return success
    

