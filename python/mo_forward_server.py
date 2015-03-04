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
        self.sbd_client = None
        self.hayes_client = None
        self.addr = addr
	self.initial_data = ""

    def handle_read(self):
	for line in self.makefile('r'):
            print(line)

    def handle_close(self):
        print 'Connection closed from %s' % repr(self.addr)
        sys.stdout.flush()
        self.close()


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
