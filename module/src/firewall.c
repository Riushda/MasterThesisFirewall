#include "protocol/protocol.h"
#include "constraints/time_constraint.h"
#include <linux/proc_fs.h>
#include <linux/sched.h>
#include <linux/trace.h>

#define DRIVER_AUTHOR "Justin & Dariush"
#define DRIVER_DESC "Firewall"

struct sock *nl_sock = NULL;
struct nlmsghdr *nlh;

static struct nf_hook_ops *nfho_in = NULL;
static struct nf_hook_ops *nfho_out = NULL;
static struct nf_hook_ops *nfho_fw = NULL;

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
    bool_t has_broker;
    bool_t code;
    rule_t rule1;
    rule_t rule2;
    uint8_t n_constraint;
    short index;
    memset(&rule1, 0, sizeof(rule_t));
    memset(&rule2, 0, sizeof(rule_t));
    rule2.index = -1;

    int offset = 0;

    memcpy(&code, skb->data + offset, sizeof(bool_t));
    offset += sizeof(bool_t);

    switch (code)
    {
        case PID_INFO:
            printk(KERN_INFO "PID_INFO\n");
            memcpy(&firewall_pid, skb->data + offset, sizeof(int));
            break;
        case ADD:
            printk(KERN_INFO "ADD\n");

            memcpy(&has_broker, skb->data + offset, sizeof(bool_t));
            offset += sizeof(bool_t);

            offset += buffer_to_rule(skb->data + offset, &rule1);
            if(has_broker)
                offset += buffer_to_rule(skb->data + offset, &rule2);

            print_rule(rule1);
            print_rule(rule2);

            n_constraint = *(skb->data+offset);

            if(!n_constraint){

                insert_rule(&rule_struct, rule1);
                if(has_broker)
                    insert_rule(&rule_struct, rule2);

            }
            else{

                insert_rule_and_constraint(&rule_struct, rule1, skb->data + offset);
                if(has_broker)
                    insert_rule_and_constraint(&rule_struct, rule2, skb->data + offset);

                print_data_constraint(rule_struct.data_c);
            }

            break;
        case REMOVE:
            printk(KERN_INFO "REMOVE\n");

            memcpy(&has_broker, skb->data + offset, sizeof(bool_t));
            offset += sizeof(bool_t);

            offset += buffer_to_rule(skb->data + offset, &rule1);
            if(has_broker)
                offset += buffer_to_rule(skb->data + offset, &rule2);

            print_rule(rule1);
            print_rule(rule2);

            remove_rule(&rule_struct, rule1);
            if(has_broker)
                remove_rule(&rule_struct, rule2);

            break;
        case ENABLE :
            printk(KERN_INFO "ENABLE\n");

            memcpy(&has_broker, skb->data + offset, sizeof(bool_t));
            offset += sizeof(bool_t);
          
            memcpy(&index, skb->data + offset, sizeof(short));
            offset += sizeof(short);

            enable_rule(&rule_struct, index);
            if(has_broker)
                enable_rule(&rule_struct, index + 1);

            break;
        case DISABLE :
            printk(KERN_INFO "DISABLE\n");

            memcpy(&has_broker, skb->data + offset, sizeof(bool_t));
            offset += sizeof(bool_t);
          
            memcpy(&index, skb->data + offset, sizeof(short));
            offset += sizeof(short);

            disable_rule(&rule_struct, index);
            if(has_broker)
                disable_rule(&rule_struct, index + 1);
            
            break;
        default:
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

    parsed_len = parse_packet(data, port, &packet, buffer+sizeof(rule_t));

    if(parsed_len>0){ // if publish message 
        
        print_abstract_packet(&packet);

        // match the rule
        int rule_index = match_rule(&rule_struct, &packet, 1);
        if (rule_index < 0) 
        {   
            printk(KERN_INFO "firewall: forbidden packet !\n");
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

    // decode payload tests

    data_t *data = NULL;

    //char payload[50] = "?field1=value1&field2=value2&field3=value3}";
    //char payload[35] = "{field1: value1, field2: value2}";
    char payload[35] = "{field1 : 50, 200, field2 : 300}";
    format_t *pattern = NULL;
    //create_format(&pattern, 1, "=", "&", "}");
    create_format(&pattern, 1, ":", ",", "}");
    print_format(pattern);
    int err  = decode_payload(pattern, payload, strlen(payload), &data);
    printk("err : %d\n", err);
    //print_data_t(data, STRING_TYPE);
    print_data_t(data, INT_TYPE);

    destroy_format(pattern);
    //destroy_data_t(data, STRING_TYPE);
    destroy_data_t(data, INT_TYPE);

    // time tests

    uint16_t hour;
    uint16_t minute;
    set_current_time(&hour, &minute);
    printk(KERN_INFO "time : %d:%d\n", hour, minute);

    // packet matching tests

    rule_t rule;
    rule_struct_t rule_struct_2;
    memset(&rule_struct_2, 0, sizeof(rule_struct_t));
    memset(&rule, 0, sizeof(rule_t));

    // rule

    parse_ip("192.168.1.104/24", &rule.src, &rule.src_bm);
    parse_ip("192.168.1.230/24", &rule.dst, &rule.dst_bm);
    rule.src = htonl(rule.src);
    rule.dst = htonl(rule.dst);
    parse_port("*", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 1;
    rule.action = 1;
    print_rule(rule);

    char buffer[1024];
    memset(buffer, 0, 1024);
    char *buf = buffer;

    data_constraint_t *data_c = NULL;
    data_t *data_1 = NULL;

    char value[7];
    uint8_t str_len = 6;
    memcpy(value, &str_len, 1);
    memcpy(value+1, "friend", 6);

    add_data_t(&data_1, STRING_TYPE, 0, NULL, value);

    add_data_constraint(&data_c, STRING_TYPE, 5, "hello", data_1, 1);
    data_constraint_to_buffer(data_c, &buf);

    init_rules(&rule_struct_2);

    insert_rule_and_constraint(&rule_struct_2, rule, buf);

    // packet

    abstract_packet_t packet;
    memset(&packet, 0, sizeof(abstract_packet_t));

    parse_ip("192.168.1.204/32", &packet.src, &packet.src_bm);
    parse_ip("192.168.1.130/32", &packet.dst, &packet.dst_bm);
    parse_port("22", &packet.sport, NULL);
    parse_port("22", &packet.dport, NULL);

    content_t *content = NULL;
    data_t *data_2 = NULL;

    char value2[7];
    uint8_t str_len2 = 6;
    memcpy(value2, &str_len2, 1);
    memcpy(value2+1, "friend", 6);

    add_data_t(&data_2, STRING_TYPE, 5, "hello", value2);

    create_content(&content, STRING_TYPE, 4, "test", data_2);

    create_abstract_packet(&packet, packet.src, packet.dst, packet.sport, packet.dport, packet.src_bm, packet.dst_bm, content);

    print_abstract_packet(&packet);

    // match

    printk("RULE MATCHED : %d\n", match_rule(&rule_struct_2, &packet, 1));
    disable_rule(&rule_struct_2, rule.index);
    printk("RULE MATCHED : %d\n", match_rule(&rule_struct_2, &packet, 1));
    enable_rule(&rule_struct_2, rule.index);
    printk("RULE MATCHED : %d\n", match_rule(&rule_struct_2, &packet, 1));

    print_data_constraint(rule_struct_2.data_c);
    remove_rule(&rule_struct_2, rule);
    printk("AFTER REMOVE : \n");
    print_data_constraint(rule_struct_2.data_c);

    destroy_rules(&rule_struct_2);
    destroy_abstract_packet(&packet);
    destroy_all_data_constraint(data_c);
    
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

    // Ingoing netfilter hook 

    nfho_in = (struct nf_hook_ops *)kcalloc(1, sizeof(struct nf_hook_ops), GFP_KERNEL);

    nfho_in->hook = (nf_hookfn *)hfunc;     // hook function 
    nfho_in->hooknum = NF_INET_PRE_ROUTING; // received packets 
    nfho_in->pf = PF_INET;                  // IPv4 
    nfho_in->priority = NF_IP_PRI_FIRST;    // max hook priority 

    nf_register_net_hook(&init_net, nfho_in);

    // Outgoing netfilter hook

    /*nfho_out = (struct nf_hook_ops *)kcalloc(1, sizeof(struct nf_hook_ops), GFP_KERNEL);

    nfho_out->hook = (nf_hookfn *)hfunc;     // hook function 
    nfho_out->hooknum = NF_INET_POST_ROUTING;// outgoing packets 
    nfho_out->pf = PF_INET;                  // IPv4 
    nfho_out->priority = NF_IP_PRI_FIRST;    // max hook priority 

    nf_register_net_hook(&init_net, nfho_out);*/

    // Forwarding netfilter hook

    /*nfho_fw = (struct nf_hook_ops *)kcalloc(1, sizeof(struct nf_hook_ops), GFP_KERNEL);

    nfho_fw->hook = (nf_hookfn *)hfunc;     // hook function 
    nfho_fw->hooknum = NF_INET_FORWARD;     // forwarded packets 
    nfho_fw->pf = PF_INET;                  // IPv4 
    nfho_fw->priority = NF_IP_PRI_FIRST;    // max hook priority 

    nf_register_net_hook(&init_net, nfho_fw);*/

    return 0;
}

static void __exit cleanup(void)
{
    printk(KERN_INFO "firewall: exit module\n");

    netlink_kernel_release(nl_sock);

    nf_unregister_net_hook(&init_net, nfho_in);
    kfree(nfho_in);

    /*nf_unregister_net_hook(&init_net, nfho_out);
    kfree(nfho_out);*/

    /*nf_unregister_net_hook(&init_net, nfho_fw);
    kfree(nfho_fw);*/

    printk(KERN_INFO "Before destroy_rules\n");

    destroy_rules(&rule_struct);
}

module_init(init);
module_exit(cleanup);

MODULE_LICENSE("GPL");
MODULE_AUTHOR(DRIVER_AUTHOR);
MODULE_DESCRIPTION(DRIVER_DESC);