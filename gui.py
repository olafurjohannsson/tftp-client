import tkinter, os
from tkinter import *
from tkinter.filedialog import askopenfilename
from tftp_client import TFTPClient

class Tftp_gui(object):

    def __init__(self, root):
        self.host = tkinter.StringVar(root)
        self.browse_value = tkinter.StringVar()
        
        #labels
        self._label1 = tkinter.LabelFrame(root, text = "Host:" )
        self._label2 = tkinter.LabelFrame(root, text = "Port:" )
        self._label3 = tkinter.LabelFrame(root, text = "Browse for file:" )
        self._label4 = tkinter.LabelFrame(root, text = "Remote file name:" )
        self._label5 = tkinter.LabelFrame(root, text = "Alternate file name:" )
        
        #entry's
        self._host = tkinter.Entry(self._label1, takefocus = 1, width = 30 )
        self._port = tkinter.Entry(self._label2, width = 8 )
        self.remote_file = tkinter.Entry(self._label4, width = 30 )
        self.local_file = tkinter.Entry(self._label3, width = 30, textvariable=self.browse_value)
        self.alt_filename = tkinter.Entry(self._label5, width = 30 )

        #buttons
        self.write = tkinter.Button(root, text = "Write", padx = 15, pady = 15, command = self.write_command  )
        self.read = tkinter.Button(root, text = "Read", padx = 15, pady = 15, command = self.read_command )
        self.browse = tkinter.Button(self._label3, text = "Browse", command = self.browse_command)
        
        #layout
        self._label1.grid( in_ = root, column = 1, row = 1, columnspan = 1, rowspan = 1, sticky = "news", padx=5, pady=5)
        self._label2.grid( in_ = root, column = 2, row = 1, columnspan = 1, rowspan = 1, sticky = "news", padx=5, pady=5 )
        self._label3.grid( in_ = root, column = 1, row = 2, columnspan = 1, rowspan = 1, sticky = "news", padx=5, pady=5 )
        self._label4.grid( in_ = root, column = 1, row = 3, columnspan = 1, rowspan = 1, sticky = "news", padx=5, pady=5 )
        self._label5.grid( in_ = root, column = 1, row = 4, columnspan = 1, rowspan = 1, sticky = "news", padx=5, pady=5 )

        self._host.grid( in_ = self._label1, column = 1, row = 1, columnspan = 1, padx = 5, pady = 5, rowspan = 1, sticky = "ew")
        self._port.grid( in_ = self._label2, column = 1, row = 1, columnspan = 1, padx = 5, pady = 5, rowspan = 1, sticky = "ew" )
        self.write.grid( in_ = root, column = 2, row = 2, columnspan = 1, padx = 5, pady = 5, rowspan = 1, sticky = "s" )
        self.read.grid( in_ = root, column = 2, row = 3, columnspan = 1, padx = 5, pady = 5, rowspan = 1, sticky = "s" )
        self.remote_file.grid( in_ = self._label4, column = 1, row = 1, padx = 5, pady = 5, columnspan = 1, rowspan = 1, sticky = "ew")
        self.local_file.grid( in_ = self._label3, column = 1, row = 1, padx = 5, pady = 5, columnspan = 1, rowspan = 1, sticky = "ew")
        self.browse.grid( in_ = self._label3, column = 1, row = 1, padx = 5, pady = 5, columnspan = 1, rowspan = 1, sticky = "e" )
        self.alt_filename.grid( in_ = self._label5, column = 1, row = 1, columnspan = 1, padx = 5, pady = 5, rowspan = 1, sticky = "ew")
        
        root.grid_rowconfigure(1, weight = 0, minsize = 40, pad = 0)
        root.grid_rowconfigure(2, weight = 0, minsize = 73, pad = 0)
        root.grid_rowconfigure(3, weight = 0, minsize = 25, pad = 0)
        root.grid_rowconfigure(4, weight = 0, minsize = 25, pad = 0)
        root.grid_columnconfigure(1, weight = 0, minsize = 100, pad = 0)
        root.grid_columnconfigure(2, weight = 0, minsize = 15, pad = 0)
        #root.grid_columnconfigure(3, weight = 0, minsize = 70, pad = 0)
        self._label1.grid_rowconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label1.grid_columnconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label2.grid_rowconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label2.grid_columnconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label3.grid_rowconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label3.grid_columnconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label4.grid_rowconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label4.grid_columnconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label5.grid_rowconfigure(1, weight = 0, minsize = 40, pad = 0)
        self._label5.grid_columnconfigure(1, weight = 0, minsize = 40, pad = 0)
        

    def write_command(self):
        c, file_name, alt_filename = TFTPClient(self._host.get(), self._port.get()), self.local_file.get(), self.alt_filename.get()
        if not os.path.isfile(file_name):
            raise Exception('File %s does not exist!' % file_name)
        else:
            if c.write(file_name, os.path.basename(file_name) if len(alt_filename) is 0 else alt_filename):
                print('Success')

    def read_command(self):
        c,file_name, alt_filename = TFTPClient(self._host.get(), self._port.get()), self.remote_file.get(), self.alt_filename.get()
        if c.read(file_name, file_name if len(alt_filename) is 0 else alt_filename):
            if os.path.isfile(file_name):
                print('Success')

    def browse_command(self):
        self.browse_value.set(askopenfilename())



def main():
    try: 
        userinit()
    except NameError: 
        pass
    
    root = Tk()
    window = Tftp_gui(root)
    root.title('TftpClient')
    root.resizable(width=FALSE, height=FALSE)
    
    try: 
        run()
    except NameError: 
        pass
    
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.mainloop()

if __name__ == '__main__': 
    main()
