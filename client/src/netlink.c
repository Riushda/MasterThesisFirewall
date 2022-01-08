#include "netlink.h"

struct sockaddr_nl src_addr;
struct sockaddr_nl dest_addr;
struct nlmsghdr *nlh;
struct msghdr msg;
struct iovec iov;
int sock_fd;
unsigned char payload[MAX_PAYLOAD];

int open_netlink()
{
    sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_FW);
    if (sock_fd < 0)
    {
        printf("socket: %s\n", strerror(errno));
        return -1;
    }

    /* client address */
    memset(&src_addr, 0, sizeof(src_addr));
    src_addr.nl_family = AF_NETLINK;
    src_addr.nl_pid = getpid();
    src_addr.nl_groups = 0;

    /* kernel address */
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.nl_family = AF_NETLINK;
    dest_addr.nl_pid = 0;
    dest_addr.nl_groups = 0;

    /* bind socket */
    bind(sock_fd, (struct sockaddr *)&src_addr, sizeof(src_addr));

    /* Fill the netlink message header */
    nlh = (struct nlmsghdr *)malloc(NLMSG_SPACE(MAX_PAYLOAD));
    nlh->nlmsg_len = NLMSG_SPACE(MAX_PAYLOAD);
    nlh->nlmsg_pid = getpid();
    nlh->nlmsg_flags = 0;

    memset(&iov, 0, sizeof(iov));
    iov.iov_base = (void *)nlh;
    iov.iov_len = nlh->nlmsg_len;

    memset(&msg, 0, sizeof(msg));
    msg.msg_name = (void *)&dest_addr;
    msg.msg_namelen = sizeof(dest_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    return 0;
}

void close_netlink()
{
    close(sock_fd);
    free(nlh);
}

void set_payload(uint8_t code, void *data, short data_len)
{
    int offset;

    offset = 0;

    memset(payload, 0, MAX_PAYLOAD);

    memcpy(payload + offset, &code, sizeof(code));
    offset += sizeof(code);

    memcpy(payload + offset, &data_len, sizeof(data_len));
    offset += sizeof(data_len);

    memcpy(payload + offset, data, data_len);
}

int send_msg(uint8_t code, void *data, short data_len)
{

    set_payload(code, data, data_len);
    strcpy(NLMSG_DATA(nlh), payload);

    if (!sendmsg(sock_fd, &msg, 0))
    {
        printf("sendmsg(): %s\n", strerror(errno));
        close(sock_fd);
        return -1;
    }

    return 0;
}