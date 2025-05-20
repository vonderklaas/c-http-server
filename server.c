#include "stdio.h"
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <errno.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdbool.h>

const char *CRLF = "\r\n";
const char *SP = " ";

typedef struct
{
    char *method;
    char *uri;
    char *version;
} http_req_line;

typedef enum
{
    HTTP_RESULT_OK,
    HTTP_RESULT_INTERNAL_SERVER_ERR,
} http_result;

typedef struct
{
    // string_view *splits;
    size_t count;
} string_splits;

static string_splits split_string(const char *str, size_t len, char split_by) {
    //
};

http_req_line
http_req_line_init()
{
    http_req_line line;
    line.method = NULL;
    line.uri = NULL;
    line.version = NULL;
    return line;
}

http_result parse_request_line(http_req_line *req_line, const char *buf, size_t len)
{
    if (!buf || !req_line)
    {
        return HTTP_RESULT_INTERNAL_SERVER_ERR;
    }

    req_line->method = "GET";
    req_line->version = "HTTP/1.1";

    return HTTP_RESULT_OK;
}

int handle_client(int client_socket)
{
    ssize_t n = 0;
    char buffer[1024];
    const char *hello = "HTTP/1.1 200 OK\r\n\r\nHello, World!\n";

    while (1)
    {
        memset(&buffer, 0, sizeof(buffer));

        // Read HTTP request, first 200 bytes
        n = read(client_socket, buffer, sizeof(buffer) - 1);

        if (n < 0)
        {
            perror("read(client)");
            return -1;
        }

        if (n == 0)
        {
            printf("connection closed gracefull.\n");
            break;
        }

        printf("REQUEST:\n%s\n", buffer);

        // Write a response
        (void)write(client_socket, hello, strlen(hello));
        close(client_socket);
        break;
    }

    printf("\n----\n");

    return 0;
}

int main(void)
{

    // Declarations
    int rc = 0;
    struct sockaddr_in bind_addr;
    int tcp_socket = 0;
    int ret = 0;
    int client_socket = 0;
    int enabled = true;

    // Initialize
    memset(&bind_addr, 0, sizeof(bind_addr));
    tcp_socket = socket(
        AF_INET,     /* IPv4 */
        SOCK_STREAM, /* TCP */
        0            /* Protocol */
    );

    if (tcp_socket < 0)
    {
        perror("socket()");
        return 1;
    }

    // I do not care if this fails for now
    (void)setsockopt(tcp_socket, SOL_SOCKET, SO_REUSEADDR, &enabled, sizeof(enabled));

    bind_addr.sin_port = htons(6969);
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_addr.s_addr = INADDR_ANY;

    // Return code
    rc = bind(tcp_socket, (const struct sockaddr *)&bind_addr, sizeof(bind_addr));

    if (rc < 0)
    {
        perror("bind()");
        return 1;
    }

    printf("bind succeeded\n");

    rc = listen(tcp_socket, SOMAXCONN);

    if (rc < 0)
    {
        perror("listen()");
        goto exit;
    }

    printf("listen succeeded\n");

    while (1)
    {
        printf("waiting for connections\n");
        client_socket = accept(tcp_socket, NULL, NULL);

        printf("got for connection\n");

        // Lets read the connection
        rc = handle_client(client_socket);

        if (rc < 0)
        {
            // Do not care for now.
        }
    }

exit:
    close(tcp_socket);
    return ret;
};