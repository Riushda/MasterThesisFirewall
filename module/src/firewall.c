#include "protocol/protocol.h"
#include "constraints/time_constraint.h"
#include <linux/proc_fs.h>
#include <linux/sched.h>

#define DRIVER_AUTHOR "Justin & Dariush"
#define DRIVER_DESC "Firewall"

struct sock *nl_sock = NULL;
struct nlmsghdr *nlh;

static struct nf_hook_ops *nfho = NULL;

rule_struct_t rule_struct;
int firewall_pid = 0;

/* 
    TODO : - install gdb for debug in kernel
           - detect encryption in firewall.c (keep track of connections?)
           - add context in rule.c
           - test context.c with check_time
 */

static void netlink_send_msg(char *msg, int msg_size)
{
    struct sk_buff *skb_out;
    int res;

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

    //printk(KERN_INFO "firewall: Send %s\n", msg);

    res = nlmsg_unicast(nl_sock, skb_out, firewall_pid);
    if (res < 0)
        printk(KERN_INFO "firewall: error while sending skb to user\n");
}

static void netlink_recv_msg(struct sk_buff *skb)
{
    char *msg;
    bool_t code;
    rule_t rule;
    memset(&rule, 0, sizeof(rule_t));

    nlh = (struct nlmsghdr *)skb->data;
    msg = (char *)NLMSG_DATA(nlh);
    
    //printk(KERN_INFO "skb->data : %s\n", (char *) skb->data);
    //printk(KERN_INFO "msg : %s\n", msg);

    memcpy(&code, msg, sizeof(bool_t));

    switch (code)
        {
        case PID_INFO:
            printk(KERN_INFO "PID_INFO\n");
            memcpy(&firewall_pid, msg+1, sizeof(int));
            break;
        case ADD:
            printk(KERN_INFO "ADD\n");

            memcpy(&rule, msg+1, sizeof(rule_t));

            msg = msg + 1 + sizeof(rule_t);

            rule.src=htonl(rule.src);
            rule.dst=htonl(rule.dst);
            if(!(*msg)){
                print_rule(rule);
                insert_rule(&rule_struct, rule);
            }
            else{
                insert_rule_and_constraint(&rule_struct, rule, msg);
            }

            break;
        case REMOVE:
            printk(KERN_INFO "REMOVE\n");

            memcpy(&rule, msg+1, sizeof(rule_t));
            rule.src=htonl(rule.src);
            rule.dst=htonl(rule.dst);

            remove_rule(&rule_struct, rule);

            break;
        default:
            msg = msg;
            printk(KERN_INFO "action not know\n");
        }
}

/* do not hook packet without layer 3, having only layer 1 and 2 */
static unsigned int hfunc(void *priv, struct sk_buff *skb, const struct nf_hook_state *state)
{
    abstract_packet_t packet;
    
    struct iphdr *iph;
    struct tcphdr *tcph;
    struct udphdr *udph;

    char *data;
    uint16_t port;
    unsigned char buffer[MAX_PACKET_SIZE];
   
    int parsed_len;
    uint8_t mask = 32;

    if (!skb)
        return NF_ACCEPT;

    memset(&packet, 0, sizeof(abstract_packet_t));

    // packet parsing

    iph = ip_hdr(skb);

    if(iph->protocol == IPPROTO_TCP){

        tcph = tcp_hdr(skb);

        data = (char *)((unsigned char *)tcph + (tcph->doff * 4));

        port = ntohs(tcph->dest); 

        create_abstract_packet(&packet, iph->saddr, iph->daddr, tcph->source, tcph->dest, mask, mask, NULL);

    }
    else if(iph->protocol == IPPROTO_UDP){

        // the udp code has not been tested

        udph = udp_hdr(skb);

        //data = (char *)((unsigned char *)iph + sizeof(*iph));
        data = (char *)((unsigned char *)udph + sizeof(*udph));

        port = ntohs(udph->dest);

        create_abstract_packet(&packet, iph->saddr, iph->daddr, udph->source, udph->dest, mask, mask, NULL);

    }
    else{
        printk(KERN_INFO "Unknown ip/transport layer protocol\n");
        return NF_ACCEPT; // other ip/transport layer protocol
    }

    memset(buffer, 0, sizeof(int)*2 + sizeof(short)*2);

    packet_ip_to_buffer(&packet, buffer); 

    parsed_len = parse_packet(&packet, data, port, buffer+sizeof(rule_t));

    if(parsed_len>0){ // if publish message 
        
        print_abstract_packet(&packet);

        // match the rule
        if (!match_rule(&rule_struct, &packet)) 
        {
            printk(KERN_INFO "firewall: forbidden packet!\n");
            return NF_DROP;
        }

        // send buffer to userspace

        //netlink_send_msg(buffer, sizeof(rule_t)+parsed_len);
    }
    else if(!parsed_len){ // tcp/udp packet but not related to known iot protocol
        parsed_len = 0; // for compilation
    }
    else if(parsed_len==-1){ // tcp/udp packet related to known iot protocol but not a publish
        parsed_len = -1; // for compilation
    }

    return NF_ACCEPT;
}

static int __init init(void)
{   

    uint16_t hour;
    uint16_t minute;
    set_current_time(&hour, &minute);
    printk(KERN_INFO "time : %d:%d\n", hour, minute);

    // packet matching tests

    /*rule_t rule;
    rule_struct_t rule_struct_2;
    memset(&rule_struct_2, 0, sizeof(rule_struct_t));
    memset(&rule, 0, sizeof(rule_t));

    parse_ip("192.168.0.104/24", &rule.src, &rule.src_bm);
    parse_ip("192.168.0.230/24", &rule.dst, &rule.dst_bm);
    parse_port("*", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 1;
    rule.action = 1;

    char buffer[1024];
    memset(buffer, 0, 1024);
    char *buf = buffer;

    data_constraint_t *data_c = NULL;
    data_t *data_1 = NULL;
    add_str_data_t(&data_1, 7, "friend");
    add_data_constraint(&data_c, STRING_TYPE, 6, "hello", data_1, 1);
    data_constraint_to_buffer(data_c, &buf);

    init_rules(&rule_struct_2);

    insert_rule_and_constraint(&rule_struct_2, rule, buf);

    abstract_packet_t packet;
    memset(&packet, 0, sizeof(abstract_packet_t));

    parse_ip("192.168.0.104/32", &packet.src, &packet.src_bm);
    parse_ip("192.168.0.230/32", &packet.dst, &packet.dst_bm);
    parse_port("22", &packet.sport, NULL);
    parse_port("22", &packet.dport, NULL);

    payload_t *payload = NULL;
    data_t *data_2 = NULL;

    add_str_data_t(&data_2, 7, "friend");

    create_payload(&payload, STRING_TYPE, 6, "hello", data_2);

    create_abstract_packet(&packet, packet.src, packet.dst, packet.sport, packet.dport, packet.src_bm, packet.dst_bm, payload);

    print_abstract_packet(&packet);

    printk(KERN_INFO "IP MATCHED : %d\n", match_rule(&rule_struct_2, &packet));
    printk(KERN_INFO "CONSTRAINT MATCHED : %d\n", match_constraint(&rule_struct_2, &packet));

    print_data_constraint(rule_struct_2.data_c);
    remove_rule(&rule_struct_2, rule);
    printk(KERN_INFO "AFTER REMOVE (there should be nothing): \n");
    print_data_constraint(rule_struct_2.data_c);

    destroy_rules(&rule_struct_2);
    destroy_abstract_packet(&packet);
    destroy_all_data_constraint(data_c);*/

    // test hexa to byte

    char dst[1024];
    memset(dst, 0, 1024);
    char hexa[24] = "\\x05\\x01\\x00\\x03\\x04\\x05"; // 20 = 4+5*4
    
    char len[1];
    hexa_to_byte(hexa, len, 1);

    hexa_to_byte(hexa+4, dst, (uint8_t) *len);

    int i;
    uint8_t n = (uint8_t) *len;
    for(i=0; i<n; i++)
        printk("dst[%d] : %d\n", i, dst[i]);
    
    /* rule_struct list initialization */

    memset(&rule_struct, 0, sizeof(rule_struct_t));

    init_rules(&rule_struct);

    // hook function initialisation

    struct netlink_kernel_cfg cfg = {
        .input = netlink_recv_msg,
    };

    printk(KERN_INFO "firewall: init module\n");

    nl_sock = netlink_kernel_create(&init_net, NETLINK_USERSOCK, &cfg); // was NETLINK_FW
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

    printk(KERN_INFO "Before destroy_rules\n");

    destroy_rules(&rule_struct);
}

module_init(init);
module_exit(cleanup);

MODULE_LICENSE("GPL");
MODULE_AUTHOR(DRIVER_AUTHOR);
MODULE_DESCRIPTION(DRIVER_DESC);