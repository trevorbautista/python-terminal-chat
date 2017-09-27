#!/usr/bin/env python3

# This is a simple socket experiment 
# chat for peer-to-peer.
#
# Version 0.1 as of 27 September 2017
#
# Created by Trevor Bautista
#
#########################################

# import the socket module 
import socket
# import system and getopt module for parsing arguments in CLI
import sys
import getopt

# import threading tools for multithreading
import threading
# import curses windowing system
import curses


# class for a thread to listen for messages
class ListenThread(threading.Thread):
    def __init__(self, threadID, name, socket, input_window, display_window):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.display_window = display_window
        self.input_window = input_window

    def run(self):
        # get max coordinates of display window
        self.DISP_Y, self.DISP_X = self.display_window.getmaxyx()
        while True:
            # get new message from socket
            new_message = self.socket.recv(1024).decode('ascii')
            # for each previous line in the display window,
            for i in range(2,self.DISP_Y-1):
                # store line
                old_strs = self.display_window.instr(i,1,self.DISP_X)
                # rewrite previous line with next line
                self.display_window.addstr(i-1,1,old_strs)
            # move cursor to bottom of display window
            self.display_window.move(self.DISP_Y-2,1)
            # clear old message here
            self.display_window.addstr(self.DISP_Y-2,1," "*(self.DISP_X-1))
            # place new message here
            self.display_window.addstr(self.DISP_Y-2,1,new_message)
            # redraw border for diplay window
            self.display_window.border()
            # refresh display window
            self.display_window.refresh(0,0,0,0,self.DISP_Y,self.DISP_X)

            #new_msg = self.socket.recv(1024).decode('ascii')
            #print(new_msg)

# class for a thread to send messages
class SendThread(threading.Thread):
    def __init__(self, threadID, name, socket, input_window, display_window):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.display_window = display_window
        self.input_window = input_window
        

    def run(self):
        # get max coordinates of display window
        self.DISP_Y, self.DISP_X = self.display_window.getmaxyx()
        while True:
            # get user input at prompt (wait for return key)
            self.input_window.getstr(1,1)
            # store message
            message = self.input_window.instr(1,1,self.DISP_X)
            # clear prompt
            self.input_window.clear()
            # redraw input window border
            self.input_window.border()
            # replace cursor at prompt
            self.input_window.move(1,1)
            # refresh input window
            self.input_window.refresh()
            # for each previous line in the display window,
            for i in range(2,self.DISP_Y-1):
                # store line
                old_strs = self.display_window.instr(i,1,self.DISP_X)
                # rewrite previous line with next line
                self.display_window.addstr(i-1,1,old_strs)
            # move cursor to bottom of display window
            self.display_window.move(self.DISP_Y-2,1)
            # place new message here
            self.display_window.addstr(self.DISP_Y-2,1,message)
            # redraw border for diplay window
            self.display_window.border()
            # refresh display window
            self.display_window.refresh(0,0,0,0,self.DISP_Y,self.DISP_X)
            # send message
            self.socket.send(message)




def main(argv):

    # text to display if wrong parameters
    usage = """
    Usage: python chat_server [-h][-p PORT]

        Parameters:
        ------------------------------------
        -c, --clients=  maximum number of peers to allow connection (default 5)
        -h              display this help
        -n, --name=     set name of peer
        -q, --host=     hostname/IP to connect to (default is 0.0.0.0)
        -p, --port=     specify a port to use (default 12345)
        -t, --type=     specify a protocol to use (default tcp)
    """

    # exit codes
    SUCCESS           = 0
    GENERAL_FAILURE   = 1
    INVALID_PARAMETER = 2
    CONNECTION_ERROR  = 3

    # host
    HOST = "" # optional: can be just server
    # local host
    LOCALHOST = "0.0.0.0" # '0.0.0.0' binds to all interfaces
    # port (set to default)
    PORT = 12345
    # protocol (TCP or UDP)
    PROTOCOL="tcp"
    # name of peer
    NAME="Anonymous"
    # number of peers to allow connection
    PEERS=5
    # sockets
    peersocket = ""
    hostsocket = "";

    # peer names
    peer_names = []

    # try to get argument list
    try:
        opts, args = getopt.getopt(argv,"c:hn:p:q:t:",["clients=","name=","host=","port=","type="])
    # if error in getting arguments,
    except getopt.GetoptError:
        # print usage and exit with exit code for general failure
        print(usage)
        sys.exit(GENERAL_FAILURE)

    # for each option in option list,
    for opt, arg in opts:
        # if help option,
        if (opt == '-h'):
            # print usage and exit successfuly
            print(usage)
            sys.exit(SUCCESS)
        # if clients option,
        elif (opt in ("-c","--clients")):
            # test if integer
            try:
                val = int(arg)
            # if not integer,
            except ValueError:
                # notify user and exit with exit code for invalid parameter
                print("Invalid client number:", arg)
                print(usage)
                sys.exit(INVALID_PARAMETER)
            # set port
            PEERS = int(arg) 
        # if name option,
        elif (opt in ("-n","--name")):
            # try to assign name
            try:
                NAME = arg
            # if type exception, let user know and exit with exit code for invalid parameter
            except (TypeError, ValueError):
                print("Invalid name.")
                print(usage)
                sys.exit(INVALID_PARAMETER)
        # if port option,
        elif (opt in ("-p","--port")):
            # test if integer
            try:
                val = int(arg)
            # if not integer,
            except ValueError:
                # notify user and exit with exit code for invalid parameter
                print("Invalid port", arg)
                print(usage)
                sys.exit(INVALID_PARAMETER)
            # set port
            PORT = int(arg) 
        # if port option,
        elif (opt in ("-q","--host")):
            # try to assign host
            try:
                HOST = arg
            # if type exception, let user know and exit with exit code for invalid parameter
            except (TypeError, ValueError):
                print("Invalid host.")
                print(usage)
                sys.exit(INVALID_PARAMETER)
        # if protocol option,
        elif (opt in ("-t","--protocol")):
            # if 'tcp' option, set protocol to tcp
            if (arg.lower() == "tcp"):
                PROTOCOL="tcp"
            # if 'udp' option, set protocol to udp
            elif (arg.lower() == "udp"):
                PROTOCOL="udp"
            # if invalid option, print usage and exit with exit code for invalid parameter
            else:
                print("Invalid protocol:", arg)
                print(usage)
                sys.exit(INVALID_PARAMETER) 
        # if anything else,
        else:
            # let user know and exit with exit code for invalid parameter
            print("Invalid argument(s):", arg)
            sys.exit(INVALID_PARAMETER)

    print("Host:", HOST, "Port:", PORT, "Protocol:", PROTOCOL, "Max Peers:", PEERS)

    if (PROTOCOL == "tcp"):
        # try to initialize socket
        try:
            # if the host,
            if (HOST == ""):
                # socket initialization for local host
                print("\nCreating local host socket...")
                hostsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
                print("Getting local hostname...")
                print("Local hostname", LOCALHOST)
                print("Binding to port", PORT, "...")
                hostsocket.bind( (LOCALHOST,PORT) )                             # bind to the port
                print("Local host:\t", LOCALHOST, "\nPort:\t", PORT)
                # listen for client connection (up to 5 requests)
                print("Listening for peer (max " + str(PEERS) + ")...")
                hostsocket.listen(PEERS)
            # if the peer,
            else:
                # socket initialization for peer(s) if HOST specified
                print("\nCreating peer(s) socket...")
                peersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create a socket object
                print("Connecting to peer", HOST, "with port", PORT, "...")
                peersocket.connect( (HOST,PORT) )                                 # actively initiate TCP connection with host and port
        except (OSError) as err:
            print("Error in connecting:", err)
            sys.exit(CONNECTION_ERROR)

        while True:
            # if the host,
            if (HOST == ""):
                # establish connection to client
                peersocket, addr = hostsocket.accept()
                print("Connection established to", addr)
                # send message to client
                msg = "Connection to server established."
                peersocket.send(msg.encode('ascii'))
                # receive name from client
                new_name = peersocket.recv(1024).decode('ascii')
                print("New client connected:", new_name)
                peer_names.append(new_name)
            # if the peer,
            # else:
            #     # establish connection to host
            #     hostsocket, addr = peersocket.accept()
            #     print("Connection established to", addr)
            #     # send message to client
            #     msg = "Connection to server established."
            #     peersocket.send(msg.encode('ascii'))
            #     # receive name from client
            #     new_name = peersocket.recv(1024).decode('ascii')
            #     print("New client connected:", new_name)
            #     peer_names.append(new_name)
            
            # close connection to client
            #peersocket.close()
            #print("Connection closed")
            break

        # create new main window
        stdscr = curses.initscr()
        # get max coordinates of main window
        Y,X = stdscr.getmaxyx()
        # create window to display chat content
        disp_win = curses.newpad(Y-3,X)
        # get max coordinates of display window
        DISP_Y, DISP_X = disp_win.getmaxyx()
        # draw border around display window
        disp_win.border()
        # create input window for inputting chat
        input_win = curses.newwin(3,X,Y-3,0)
        # get max coordinates of input window
        INPUT_Y, INPUT_X = input_win.getmaxyx()
        # draw border around input window
        input_win.border()
        # move cursor to prompt of input window
        input_win.move(1,1)
        # refresh display window
        disp_win.refresh(0,0,0,0,DISP_Y,DISP_X)
        # refresh input window
        input_win.refresh()


        # create send and receive threads
        send_thread = SendThread(1, "Send-Thread", peersocket,input_win, disp_win)
        listen_thread = ListenThread(2, "Listen-Thread", peersocket,input_win, disp_win)
        # start threads
        send_thread.start()
        listen_thread.start()

    elif (PROTOCOL == "udp"):
        print("udp")
    else:
        print("unrecognized protocol")





if __name__ == "__main__":
    main(sys.argv[1:])

