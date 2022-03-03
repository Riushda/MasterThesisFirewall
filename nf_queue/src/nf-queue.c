#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <arpa/inet.h>
#include <linux/ip.h>
#include <netinet/ip6.h>
#include <netinet/in.h>
#include <stddef.h>
//#include <netinet/ip.h>

#include <sys/socket.h>
#include <netinet/in.h>

#include <libmnl/libmnl.h>
#include <linux/netfilter.h>
#include <linux/netfilter/nfnetlink.h>
#include <linux/netfilter/nf_nat.h>
#include <linux/netfilter/nf_tables.h>
#include <libnftnl/table.h>
#include <libnftnl/chain.h>
#include <libnftnl/rule.h>
#include <libnftnl/expr.h>

#include <linux/types.h>
#include <linux/netfilter/nfnetlink_queue.h>
#include <libnetfilter_queue/libnetfilter_queue.h>
#include <libnetfilter_queue/pktbuff.h>
#include <libnetfilter_queue/libnetfilter_queue_ipv4.h>
#include <libnetfilter_queue/libnetfilter_queue_ipv6.h>

#include <linux/if.h>
#include <linux/if_link.h>
#include <linux/rtnetlink.h>
 
/* only for NFQA_CT, not needed otherwise: */
#include <linux/netfilter/nfnetlink_conntrack.h>

static struct mnl_socket *nl;

static void
nfq_send_verdict(int queue_num, uint32_t id)
{
        char buf[MNL_SOCKET_BUFFER_SIZE];
        struct nlmsghdr *nlh;

        nlh = nfq_nlmsg_put(buf, NFQNL_MSG_VERDICT, queue_num);
        nfq_nlmsg_verdict_put(nlh, id, NF_ACCEPT);

        if (mnl_socket_sendto(nl, nlh, nlh->nlmsg_len) < 0) {
                perror("mnl_socket_send");
                exit(EXIT_FAILURE);
        }
}

static int queue_cb(const struct nlmsghdr *nlh, void *data)
{
        struct nfqnl_msg_packet_hdr *ph = NULL;
        struct nlattr *attr[NFQA_MAX+1] = {};
        uint32_t id = 0;
        struct nfgenmsg *nfg;
        uint16_t plen;

        if (nfq_nlmsg_parse(nlh, attr) < 0) {
                perror("problems parsing");
                return MNL_CB_ERROR;
        }

        nfg = mnl_nlmsg_get_payload(nlh);

        if (attr[NFQA_PACKET_HDR] == NULL) {
                fputs("metaheader not set\n", stderr);
                return MNL_CB_ERROR;
        }

        ph = mnl_attr_get_payload(attr[NFQA_PACKET_HDR]);

        plen = mnl_attr_get_payload_len(attr[NFQA_PAYLOAD]);
        void *payload = mnl_attr_get_payload(attr[NFQA_PAYLOAD]);

        /* GET PACKET INFORMATION HERE */
        
        struct pkt_buff *pktb = pktb_alloc(nfg->nfgen_family, payload, plen, 0);

        if(nfg->nfgen_family==AF_INET){
                struct iphdr *iph = nfq_ip_get_hdr(pktb);
                struct in_addr addr;

                memcpy(&(addr), &iph->saddr, sizeof(struct in_addr));
                printf("ip: %s\n", inet_ntoa(addr));
        }
        else if(nfg->nfgen_family==AF_INET6){
                
                struct ip6_hdr *iph6 = nfq_ip6_get_hdr(pktb);
                struct in6_addr addr6;
                
                memcpy(&addr6, &iph6->ip6_src, sizeof(struct in6_addr));

                char ip6_string[INET6_ADDRSTRLEN];
                inet_ntop(AF_INET6, &addr6, ip6_string, INET6_ADDRSTRLEN);
                printf("ip: %s\n", ip6_string);
        }
        
        pktb_free(pktb);

        id = ntohl(ph->packet_id);

        /* printf("packet received (id=%u hw=0x%04x hook=%u, payload len %u",
        id, ntohs(ph->hw_protocol), ph->hook, plen); */


        /* DECIDE TO ACCEPT OR DROP */
        nfq_send_verdict(ntohs(nfg->res_id), id);

        if(attr[NFQA_MARK]){
                printf("mark=%u \n", ntohl(mnl_attr_get_u32(attr[NFQA_MARK])));
        }
        else {
                printf("no mark !\n");
        }

        return MNL_CB_OK;
}

int main(int argc, char *argv[])
{ 
        char *buf;
        /* largest possible packet payload, plus netlink data overhead: */
        size_t sizeof_buf = 0xffff + (MNL_SOCKET_BUFFER_SIZE/2);
        struct nlmsghdr *nlh;
        int ret;
        unsigned int portid, queue_num;

        if (argc != 2) {
                printf("Usage: %s [queue_num]\n", argv[0]);
                exit(EXIT_FAILURE);
        }
        queue_num = atoi(argv[1]);

        nl = mnl_socket_open(NETLINK_NETFILTER);
        if (nl == NULL) {
                perror("mnl_socket_open");
                exit(EXIT_FAILURE);
        }

        if (mnl_socket_bind(nl, 0, MNL_SOCKET_AUTOPID) < 0) {
                perror("mnl_socket_bind");
                exit(EXIT_FAILURE);
        }
        portid = mnl_socket_get_portid(nl);

        buf = malloc(sizeof_buf);
        if (!buf) {
                perror("allocate receive buffer");
                exit(EXIT_FAILURE);
        }

        nlh = nfq_nlmsg_put(buf, NFQNL_MSG_CONFIG, queue_num);
        nfq_nlmsg_cfg_put_cmd(nlh, AF_INET, NFQNL_CFG_CMD_BIND);

        if (mnl_socket_sendto(nl, nlh, nlh->nlmsg_len) < 0) {
                perror("mnl_socket_send");
                exit(EXIT_FAILURE);
        }

        nlh = nfq_nlmsg_put(buf, NFQNL_MSG_CONFIG, queue_num);
        nfq_nlmsg_cfg_put_params(nlh, NFQNL_COPY_PACKET, 0xffff);

        mnl_attr_put_u32(nlh, NFQA_CFG_FLAGS, htonl(NFQA_CFG_F_GSO));
        mnl_attr_put_u32(nlh, NFQA_CFG_MASK, htonl(NFQA_CFG_F_GSO));

        if (mnl_socket_sendto(nl, nlh, nlh->nlmsg_len) < 0) {
                perror("mnl_socket_send");
                exit(EXIT_FAILURE);
        }

        /* ENOBUFS is signalled to userspace when packets were lost
        * on kernel side.  In most cases, userspace isn't interested
        * in this information, so turn it off.
        */
        ret = 1;
        mnl_socket_setsockopt(nl, NETLINK_NO_ENOBUFS, &ret, sizeof(int));

        for (;;) {
                ret = mnl_socket_recvfrom(nl, buf, sizeof_buf);
                if (ret == -1) {
                        perror("mnl_socket_recvfrom");
                        exit(EXIT_FAILURE);
                }

                ret = mnl_cb_run(buf, ret, 0, portid, queue_cb, NULL);
                if (ret < 0){
                        perror("mnl_cb_run");
                        exit(EXIT_FAILURE);
                }
        }

        mnl_socket_close(nl);

        return 0;
}