#!/usr/bin/python

# splits traffic to Hayes Modem emulator and to an Iridium9602 simulator

import asyncore
import socket

# this script listens (binds) on this port
forward_address = '0.0.0.0'
forward_port = 4002

# connections that send "goby" as the first four characters gets
# forwarded to a server listening on this server at this port
hayes_server = "127.0.0.1"
hayes_port = 4001

# connections that send "~" as the first character gets
# forwarded to a server listening on localhost at this port
sbd_server = "127.0.0.1"
sbd_port = 4003

class ConditionalForwardClient(asyncore.dispatcher_with_send):

    def __init__(self, server, host, port):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )
        self.server = server
           
    def handle_read(self):
        data = self.recv(64)
        if data:
           self.server.send(data)


class ConditionalForwardHandler(asyncore.dispatcher_with_send):

    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.identified_protocol = False
        self.addr = addr
	self.initial_data = ""
        self.buf = ""
        self.hayes_client = ConditionalForwardClient(self, hayes_server, hayes_port)
        self.sbd_client = ConditionalForwardClient(self, sbd_server, sbd_port)
        self.sbd_write = False
        self.sbd_bytes_remaining = 0

    def handle_read(self):
        data = self.recv(256)
        
        print data.encode("hex")

        if not data:
            return
        elif self.sbd_write: # not line mode - raw data
            self.sbd_send_bytes(data)
        else: # line based Command data
            self.buf += data
            line_list = self.buf.split('\r')
            # partial line
            self.buf = line_list[-1]
        
            for line in line_list[0:-1]:
                self.line_process(line)

    def handle_close(self):
        print 'Connection closed from %s' % repr(self.addr)
        sys.stdout.flush()
        self.close()

    def line_process(self, line):
        line_cr = line + '\r'
        
        if line.strip().upper() in ['ATE']:
            self.hayes_client.send(line_cr)
            self.sbd_client.send(line_cr)
        else:
            if len(line) >= 6 and line[2:6].upper() == "+SBD":
                self.sbd_client.send(line_cr)
                if len(line) >= 8 and line[2:8].upper() == "+SBDWB":
                    parts = line.split('=')
                    self.sbd_bytes_remaining = int(parts[1]) + 2 # 2 checksum bytes
                    self.sbd_write = True
            else:
                self.hayes_client.send(line_cr)
    
    def sbd_send_bytes(self, bytes):
        self.sbd_bytes_remaining -= len(bytes)
        self.sbd_client.send(bytes)
        print self.sbd_bytes_remaining
        if self.sbd_bytes_remaining <= 0:
            self.sbd_write = False

class ConditionalForwardServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            sys.stdout.flush()
        try:
            handler = ConditionalForwardHandler(sock, addr)
        except: 
            print "Unexpected error:", sys.exc_info()[0]
            
import sys
print "Iridium Port forwarder starting up ..."
print "Listening on port: %d" % forward_port
print "Connecting for Iridium9602 SBD on %s:%d" % (sbd_server, sbd_port)
print "Connecting for Hayes (ATDuck) on %s:%d" % (hayes_server, hayes_port)
sys.stdout.flush()

server = ConditionalForwardServer(forward_address, forward_port)
asyncore.loop()
