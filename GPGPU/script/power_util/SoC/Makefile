CC = gcc
CFLAGS = -O2 -Wall
TARGET = SoC

all: $(TARGET)

$(TARGET): SoC.c
	$(CC) $(CFLAGS) -o $(TARGET) SoC.c

clean:
	rm -f $(TARGET)
