from datetime import datetime
import os, traceback

DEV = True
LOG = True
LOG_FILE = 'tftp_log.txt'

TFTP_MODES = {
              'unknown'  : 0, 
              'netascii' : 1,
              'octet'    : 2,
              'mail'     : 3 }
              
TFTP_OPCODES = {
                'unknown' : 0,
                'read'    : 1,  # RRQ
                'write'   : 2,  # WRQ
                'data'    : 3,  # DATA
                'ack'     : 4,  # ACKNOWLEDGMENT
                'error'   : 5 } # ERROR


class TFTPPackets(object):

    def __init__(self):
        self.log = TFTPLog
        self.opcodes = TFTP_OPCODES
        self.modes = TFTP_MODES
        self.to_int = lambda args: [ord(a) for a in args]
        self.to_bytes = bytearray                            # lazy-invoking of bytearray ctor

    def join(self, *arrs):
        res=[]
        
        try:
            for arr in arrs:
                if not isinstance(arr, list):
                    arr = [arr]
                res += arr
        except Exception as err:
            print("join", err)
        return res
    
    def request_packet(self, filename, mode, opcode):                                                        # RRQ and WRQ packets (opcode 1 and 2)
        try:
            return self.to_bytes(self.join(0, opcode, self.to_int(filename), 0, self.to_int(mode), 0))           # 2 bytes for opcode string as filename(as sequence of bytes terminated by zero-byte mode (netascii, octet) and terminated by a zero byte  
        except Exception as err:
            print("request_packet", err)
            self.log("request_packet", params=(filename, mode, opcode), msg="Err: %s" % err)

    def ack_packet(self, packetnr):
        try:
            return self.to_bytes(self.join(0, self.opcodes['ack'], ((packetnr >> 8) & 0xff), (packetnr & 0xff))) # ack packet with zero_byte, ack status code, (shift 8 bites and AND with 0xff(255)
        except Exception as err:
            print("ack_packet", err)
            print(self.join(0, self.opcodes['ack'], ((packetnr >> 8) & 0xff), (packetnr & 0xff)))
            self.log("ack_packet", params=(packetnr), msg="Creating ack packet: {0}\nErr: {1}".format(buffer, err))

    def data_packet(self, packetnr, buffer):
        try:
            # utf-8 default with latin1 as backup
            encoding = 'latin1'
            return self.to_bytes(self.join(0, self.opcodes['data'], (packetnr >> 8) & 0xff, packetnr & 0xff, self.to_int(buffer.decode(encoding))))
        except Exception as err:
            print("data_packet", err)
            try:
                print(self.join(0, self.opcodes['data'], (packetnr >> 8) & 0xff, packetnr & 0xff, self.to_int(buffer.decode(encoding))))
            except:
                pass
            self.log("data_packet", params=(packetnr, buffer), msg="Calling data packet, data: {0}\nErr: {1}, traceback: {2}".format(buffer, err, traceback.format_exc()))
    

class TFTPException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class TFTPLog():

    def __init__(self, action, msg=None, params=None):
        self.log(action, msg, params)
    
    # can be called without instatiating an instance of <TFTPClient>
    @staticmethod
    def log(action, msg=None, params=None):
        self.log(action, msg, params)

    # helper function to log behavior
    def log(self, action, msg=None, params=None):
        if LOG:
            try:
                ft_message = "Logged action: {0}\nDate: {1}\nParams: {2}\nMessage: {3}\n\n".format(action, datetime.today(), params, msg)
                if DEV:
                    print(ft_message)
                
                with open(LOG_FILE, 'a+') as logfile:
                    logfile.write(ft_message)

            except Exception as logex:
                print("Logex: %s" % (logex))



#obsolete
class TFTPTest():


    def __init__(self, c, remote_file, local_file, transfer_mode):
        self.buffer = []

        '''  
        do_append = lambda func, message, err: self.buffer.append(message) if func else self.buffer.append(err)

        do_append(c.read(remote_file, local_file, transfer_mode),
        "Successfully created file {0} from {1}/{2} using {3} mode.".format(os.path.join(os.getcwd(), local_file), str(c), remote_file, transfer_mode),
         "Could not finish read() file {0} from {1}/{2} using {3} mode.".format(local_file, str(c), remote_file, transfer_mode))
        '''
        do = lambda func, msg : buffer.append(msg) if func else buffer.append("Not work!")
        
        ### tftpclient.read() ###
        if(c.read(remote_file, local_file, transfer_mode)):
            self.buffer.append("Successfully created file {0} from {1}/{2} using {3} mode.".format(os.path.join(os.getcwd(), local_file), str(c), remote_file, transfer_mode))
        else:
            self.buffer.append("Could not finish read() file {0} from {1}/{2} using {3} mode.".format(local_file, str(c), remote_file, transfer_mode))

        ### tftpclient.write() ###
        if (c.write(remote_file, local_file, transfer_mode)):
            self.buffer.append("Successfully sent file {0} to {1}/{2} using {3} mode.".format(local_file, str(c), remote_file, transfer_mode))
        else:
            self.buffer.append("Could not finish write() {0} to {1}/{2} using {3} mode.".format(local_file, str(c), remote_file, transfer_mode))


        ack_packet, request_packet = c.ack_packet(0xff), c.request_packet('file.txt', 'octet', c.opcodes['read'])

        ### tftppackets.ack_packet ###
        if ack_packet == bytearray([0, c.opcodes['ack'], 0, 0xff]):
            self.buffer.append("Success in creating ack packet: {0}".format(ack_packet))
        else:
            self.buffer.append("Err in creating ack packet: {0}".format(ack_packet))

        ### tftpackets.request_packet ###
        if request_packet == bytearray(b'\x00\x01file.txt\x00octet\x00'):
            self.buffer.append("Success in creating request packet: {0}".format(request_packet))
        else:
            self.buffer.append("Err in creating request packet: {0}".format(request_packet))
        

    

    def __str__(self):
        return "%s" % ( "\n".join(self.buffer) )


