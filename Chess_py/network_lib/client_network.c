// client_network.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <errno.h>

// Connect to server
int connect_to_server(const char *host, int port)
{
    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        return -1;
    }

    // Set timeout
    struct timeval timeout;
    timeout.tv_sec = 5;
    timeout.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout, sizeof(timeout));

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, host, &serv_addr.sin_addr) <= 0)
    {
        close(sock);
        return -2;
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        close(sock);
        return -3;
    }

    return sock;
}

// Disconnect from server
void disconnect_server(int sock)
{
    if (sock > 0)
    {
        close(sock);
    }
}

// Send message (appends newline)
int send_message(int sock, const char *message)
{
    if (sock <= 0) return -1;

    size_t len = strlen(message);
    char *buffer = malloc(len + 2);
    if (!buffer) return -1;

    strcpy(buffer, message);
    buffer[len] = '\n';
    buffer[len + 1] = '\0';

    int sent = send(sock, buffer, len + 1, 0);
    free(buffer);

    return (sent == len + 1) ? 0 : -1;
}

// Receive message (reads until newline)
int receive_message(int sock, char *buffer, int size)
{
    if (sock <= 0) return -1;

    // Clear buffer
    memset(buffer, 0, size);

    int total = 0;
    char c;
    
    // Read 1 byte at a time to avoid over-reading next message
    while (total < size - 1)
    {
        int n = recv(sock, &c, 1, 0);
        
        if (n <= 0) {
            // Error or connection closed
            if (total > 0) {
                buffer[total] = '\0';
                return total;
            }
            return -1;
        }
        
        buffer[total++] = c;
        
        if (c == '\n') {
            break; // Message complete
        }
    }

    buffer[total] = '\0';
    return total;
}
