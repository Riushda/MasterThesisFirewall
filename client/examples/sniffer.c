#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <getopt.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/ip.h>
#include <linux/netlink.h>
#include <errno.h>
#include "htable.h"

#define MAX_PAYLOAD 1024
#define NETLINK_FW 17

struct rule
{
    __be32 src;
    __be32 dst;
    __be16 sport;
    __be16 dport;
};

void print_bits(size_t const size, void const *const ptr);

int set_payload(unsigned char *payload, uint8_t code, uint16_t data_len, void *data)
{
    u_int32_t offset;

    offset = 0;

    memset(payload, 0, MAX_PAYLOAD);

    memcpy(payload + offset, &code, sizeof(code));
    offset += sizeof(code);

    memcpy(payload + offset, &data_len, sizeof(data_len));
    offset += sizeof(data_len);

    memcpy(payload + offset, data, data_len);

    return 0;
}

int main(int argc, char *argv[])
{
    struct sockaddr_nl src_addr;
    struct sockaddr_nl dest_addr;
    struct nlmsghdr *nlh;
    struct msghdr msg;
    struct iovec iov;
    int sock_fd;
    int err;
    struct rule *r;
    unsigned char payload[MAX_PAYLOAD];

    sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_FW);
    if (sock_fd < 0)
    {
        printf("socket: %s\n", strerror(errno));
        return 1;
    }

    /* client address */
    memset(&src_addr, 0, sizeof(src_addr));
    src_addr.nl_family = AF_NETLINK;
    src_addr.nl_pid = getpid();
    src_addr.nl_groups = 0;
    bind(sock_fd, (struct sockaddr *)&src_addr, sizeof(src_addr));

    /* kernel address */
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.nl_family = AF_NETLINK;
    dest_addr.nl_pid = 0;
    dest_addr.nl_groups = 0;

    /* Fill the netlink message header */
    nlh = (struct nlmsghdr *)malloc(NLMSG_SPACE(MAX_PAYLOAD));
    nlh->nlmsg_len = NLMSG_SPACE(MAX_PAYLOAD);
    nlh->nlmsg_pid = getpid();
    nlh->nlmsg_flags = 0;

    /* Input the rule */
    r = (struct rule *)malloc(sizeof(struct rule));
    parse_ip("127.0.0.1", &r->src);
    parse_ip("127.0.0.1", &r->dst);
    parse_port("22", &r->sport);
    parse_port("22", &r->dport);
    err = set_payload(payload, 0, sizeof(r), (void *) &r);

    /* Fill in the netlink message payload */
    strcpy(NLMSG_DATA(nlh), payload);

    memset(&iov, 0, sizeof(iov));
    iov.iov_base = (void *)nlh;
    iov.iov_len = nlh->nlmsg_len;

    memset(&msg, 0, sizeof(msg));
    msg.msg_name = (void *)&dest_addr;
    msg.msg_namelen = sizeof(dest_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    err = sendmsg(sock_fd, &msg, 0);
    if (!err)
    {
        printf("sendmsg(): %s\n", strerror(errno));
        close(sock_fd);
        return 1;
    }

    close(sock_fd);
    free(nlh);
    free(r);

    return 0;
}

/*int c;

    while (1)
    {
        int option_index = 0;
        static struct option long_options[] =
            {
                {"src", required_argument, NULL, 0},
                {"dst", required_argument, NULL, 0},
                {"sport", required_argument, NULL, 0},
                {"dport", required_argument, NULL, 0},
                {NULL, 0, NULL, 0}};

        c = getopt_long(argc, argv, "", long_options, &option_index);
        if (c == -1)
            break;

        switch (c)
        {
        case 0:
            printf("long option %s", long_options[option_index].name);
            if (optarg)
                printf(" with arg %s", optarg);
            printf("\n");
            break;

        case 1:
            printf("regular argument '%s'\n", optarg);
            break;

        case '?':
            printf("unknown option %c\n", optopt);
            break;

        case ':':
            printf("missing argument\n");
            break;

        default:
            printf("?? getopt returned character code 0%o ??\n", c);
        }
    }*/