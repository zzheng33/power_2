CC=gcc
LIBS=-lm
SRCS= RaplSetPower.c RaplPowerMonitor_serverID.c RaplPowerMonitor.c
#OBJS= $(SRCS:.c=)
all: RaplSetPower RaplPowerMonitor_serverID RaplPowerMonitor

RaplSetPower: RaplSetPower.c
	$(CC) $(CFLAGS) -g -o RaplSetPower RaplSetPower.c $(LIBS)
RaplPowerMonitor_serverID: RaplPowerMonitor_serverID.c
	$(CC) $(CFLAGS) -g -o RaplPowerMonitor_serverID RaplPowerMonitor_serverID.c $(LIBS)
RaplPowerMonitor: RaplPowerMonitor.c
	$(CC) $(CFLAGS) -g -o RaplPowerMonitor RaplPowerMonitor.c $(LIBS)
clean:
	rm -f RaplSetPower RaplPowerMonitor_serverID RaplPowerMonitor
