#include "rule.h"
#include <linux/proc_fs.h>
#include <linux/sched.h>

#define DRIVER_AUTHOR "Justin & Dariush"
#define DRIVER_DESC "Firewall"

struct sock *nl_sock = NULL;
struct nlmsghdr *nlh;

static struct nf_hook_ops *nfho = NULL;

rule_struct_t rule_struct;
int firewall_pid = 0;

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
    bool_t action;
    rule_t rule;
    memset(&rule, 0, sizeof(rule_t));

    nlh = (struct nlmsghdr *)skb->data;
    msg = (char *)NLMSG_DATA(nlh);

    memcpy(&action, msg, sizeof(bool_t));
    memcpy(&rule, msg+1, sizeof(rule_t));
    rule.src = (int) ntohl((uint32_t) rule.src);
    rule.dst = (int) ntohl((uint32_t) rule.dst);

    //print_rule(rule);

    switch (action)
        {
        case ADD:
            insert_rule(&rule_struct, rule);
            break;
        case REMOVE:
            remove_rule(&rule_struct, rule);
            break;
        default:
            msg = msg;
            //printk(KERN_INFO "action not know\n");
        }
}

static unsigned int hfunc(void *priv, struct sk_buff *skb, const struct nf_hook_state *state)
{
    rule_t rule;
    
    struct tcphdr *tcph;

    char *data;
    uint8_t application_header;

    int offset; 
    uint8_t msg_len;
    uint16_t topic_len;
    uint8_t payload_len;

    uint8_t topic_len_short;
    int buffer_len;

    if (!skb)
        return NF_ACCEPT;

    // create the rule

    memset(&rule, 0, sizeof(rule_t));

    parse_to_rule(skb, &rule);
    //print_rule(rule);

    // match the rule

    if (match_rule(&rule_struct, rule)) // actually !match_rule but if drop too much it crashes
    {
        printk(KERN_INFO "firewall: no match!\n");
        return NF_DROP;
    }

    /*

    MQTT layer 
    Remark : msg_len is the length of the remaining fields (not counting itself)
    ________________________________________________________________________________________
    |        |         |           |                   |                                    |
    | header | msg_len | topic_len |      topic        |              payload               |                                   
    | 1 byte | 1 byte  |  2 bytes  | topic_len byte(s) |  (msg_len - 2 - topic_len) byte(s) |                                                            
    |________|_________|___________|___________________|____________________________________|

    */

    tcph = tcp_hdr(skb);

    data = (char *)((unsigned char *)tcph + (tcph->doff * 4));

    application_header = *(data);

    if(application_header==MQTT_PROTOCOL){
        msg_len = *(data+1);

        memcpy(&topic_len, data+2, 2);
        topic_len = ntohs(topic_len);

        offset = 4;

        char topic[topic_len+1];
        memset(topic, 0, topic_len+1);
        memcpy(topic, data+offset, topic_len);

        offset += topic_len;

        payload_len = msg_len - 2 - topic_len; 
        char payload[payload_len+1];
        memset(payload, 0, payload_len+1);
        memcpy(payload, data+offset, payload_len);

        printk(KERN_INFO "topic : %s\n", topic);
        printk(KERN_INFO "payload : %s\n", payload);

        // concatenate informations

        topic_len_short = (uint8_t) topic_len;
        
        buffer_len = 12 + 1 + topic_len + 1 + payload_len;
        unsigned char buffer[buffer_len];
        memset(buffer, 0, buffer_len);

        offset = rule_to_buffer(&rule, buffer); // will always be 12 : 2 int ips (8 bytes) + 2 short ports (4 bytes)

        memcpy(buffer + offset, &topic_len_short, 1);
        offset += 1;
        memcpy(buffer + offset, topic, topic_len);
        offset += topic_len;
        memcpy(buffer + offset, &payload_len, 1);
        offset += 1;
        memcpy(buffer + offset, payload, payload_len);

        // send buffer to userspace

        //netlink_send_msg(buffer, buffer_len);
    }

    return NF_ACCEPT;
}

static int __init init(void)
{
    rule_t rule;
    
    // search for firewall process

    struct task_struct *task;

    for_each_process(task) {

       // compare your process name with each of the task struct process name 

        if ( (strcmp( task->comm,"client.out") == 0 ) ) {

              // if matched that is your user process PID      
              firewall_pid = task->pid;
              printk(KERN_INFO "firewall pid : %d\n", firewall_pid);
        }
    }

    if(!firewall_pid){
        printk(KERN_INFO "firewall process not found !");
        //return -1; // will throw operation not permitted
    }

    /* rule_struct list initialization */

    memset(&rule_struct, 0, sizeof(rule_struct_t));

    init_rules(&rule_struct);

    // insert dummy rule

    memset(&rule, 0, sizeof(rule_t));

    parse_ip("127.0.0.1/24", &rule.src, &rule.src_bm);
    parse_ip("127.0.0.1/24", &rule.dst, &rule.dst_bm);
    parse_port("22", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 2;
    rule.action = 1;

    insert_rule(&rule_struct, rule);

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