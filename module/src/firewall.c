#include <net/sock.h>
#include <linux/module.h>
#include <linux/netlink.h>
#include <linux/skbuff.h>
#include <linux/kernel.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/inet.h>
#include "rule.h"
#include "htable.h"
#include "utils.h"

#define DRIVER_AUTHOR "Justin"
#define DRIVER_DESC "Firewall"

struct sock *nl_sock = NULL;
struct nlmsghdr *nlh;

static struct nf_hook_ops *nfho = NULL;

struct item *table[TABLE_SIZE];

static void netlink_send_msg(char *msg, int msg_size)
{
    struct sk_buff *skb_out;
    int res;
    int pid;

    pid = nlh->nlmsg_pid;

    // create message
    skb_out = nlmsg_new(msg_size, 0);
    if (!skb_out)
    {
        printk(KERN_ERR "firewall: failed to allocate new skb\n");
        return;
    }

    nlh = nlmsg_put(skb_out, 0, 0, NLMSG_DONE, msg_size, 0);
    NETLINK_CB(skb_out).dst_group = 0;
    strncpy(nlmsg_data(nlh), msg, msg_size);

    printk(KERN_INFO "firewall: Send %s\n", msg);

    res = nlmsg_unicast(nl_sock, skb_out, pid);
    if (res < 0)
        printk(KERN_INFO "firewall: error while sending skb to user\n");
}

static void netlink_recv_msg(struct sk_buff *skb)
{
    nlh = (struct nlmsghdr *)skb->data;
    printk(KERN_INFO "firewall: msg received\n");
}

static unsigned int hfunc(void *priv, struct sk_buff *skb, const struct nf_hook_state *state)
{
    unsigned char buffer[RULE_SIZE];

    if (!skb)
        return NF_ACCEPT;

    parse_to_buffer(skb, buffer);
    if (search_item(buffer, table, TABLE_SIZE) != NULL)
    {
        printk(KERN_INFO "firewall: match!\n");
        return NF_DROP;
    }

    return NF_ACCEPT;
}

static int __init init(void)
{
    struct netlink_kernel_cfg cfg = {
        .input = netlink_recv_msg,
    };

    printk(KERN_INFO "firewall: init module\n");

    nl_sock = netlink_kernel_create(&init_net, NETLINK_FW, &cfg);
    if (!nl_sock)
    {
        printk(KERN_ALERT "firewall: error creating socket.\n");
        return -10;
    }

    nfho = (struct nf_hook_ops *)kcalloc(1, sizeof(struct nf_hook_ops), GFP_KERNEL);

    /* Initialize netfilter hook */
    nfho->hook = (nf_hookfn *)hfunc;     /* hook function */
    nfho->hooknum = NF_INET_PRE_ROUTING; /* received packets */
    nfho->pf = PF_INET;                  /* IPv4 */
    nfho->priority = NF_IP_PRI_FIRST;    /* max hook priority */

    nf_register_net_hook(&init_net, nfho);

    return 0;
}

static void __exit cleanup(void)
{
    printk(KERN_INFO "firewall: exit module\n");

    netlink_kernel_release(nl_sock);

    nf_unregister_net_hook(&init_net, nfho);
    kfree(nfho);

    free_table(table, TABLE_SIZE);
}

module_init(init);
module_exit(cleanup);

MODULE_LICENSE("GPL");
MODULE_AUTHOR(DRIVER_AUTHOR);
MODULE_DESCRIPTION(DRIVER_DESC);