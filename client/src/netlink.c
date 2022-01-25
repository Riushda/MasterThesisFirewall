#include "netlink.h"
#include <inttypes.h>

struct nlmsghdr *nlh;
struct msghdr msg;
struct iovec iov;
unsigned char payload[MAX_PAYLOAD];

int open_netlink()
{
    sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_USERSOCK); // NETLINK_FW 
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
    connect(sock_fd, (struct sockaddr *)& dest_addr, sizeof(dest_addr));

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

int receive_msg(volatile int *keeprunning){
    if (open_netlink())
    {
        return -1;
    }

    fd_set rset;
    int nready;
    struct timeval tv = {2, 0};

    char decision[200];

    struct nlmsghdr *nl_msghdr = (struct nlmsghdr*) malloc(NLMSG_SPACE(256));

    while (*keeprunning) {
        memset(nl_msghdr, 0, NLMSG_SPACE(256));
        memset(decision, 0, 200);

        iov.iov_base = (void*) nl_msghdr;
        iov.iov_len = NLMSG_SPACE(256);

        msg.msg_name = (void*) &src_addr;
        msg.msg_namelen = sizeof(src_addr);
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;

        FD_SET(sock_fd, &rset);

        int max_fd = sock_fd + 1;

        nready = select(max_fd, &rset, NULL, NULL, &tv);
        if (nready == -1)
        {
            free(nl_msghdr);
            return -1;
        }

        if (!FD_ISSET(sock_fd, &rset) || !keeprunning)
            continue;

        recvmsg(sock_fd, &msg, 0);

        char *kernel_msg = (char*)NLMSG_DATA(nl_msghdr);
        //printf("Kernel message: %s\n", kernel_msg); 

        memcpy(decision, take_decision(kernel_msg), strlen(kernel_msg));
        
        //send_msg(*decision, (void *) decision+1);
    }
    
    free(nl_msghdr);
    close(sock_fd);
    free(nlh);

    printf("netlink thread closing gracefully\n");

    return 0;
}

int set_payload(uint8_t code, void *data)
{
    int offset;

    offset = 0;

    memset(payload, 0, MAX_PAYLOAD);

    memcpy(payload + offset, &code, sizeof(code));
    offset += sizeof(code);

    memcpy(payload + offset, data, sizeof(rule_t));
    offset += sizeof(rule_t);

    return offset;
}

int send_msg(uint8_t code, void *data)
{
    int msg_len = set_payload(code, data);
    memcpy(NLMSG_DATA(nlh), payload, msg_len);

    memset(&iov, 0, sizeof(iov));
    iov.iov_base = (void *)nlh;
    iov.iov_len = nlh->nlmsg_len;
    msg.msg_iov = &iov;

    if (!sendmsg(sock_fd, &msg, 0))
    {
        printf("sendmsg(): %s\n", strerror(errno));
        close(sock_fd);
        return -1;
    }

    return 0;
}