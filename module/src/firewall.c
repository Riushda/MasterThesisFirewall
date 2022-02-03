#include "protocol/protocol.h"
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
            rule.src=htonl(rule.src);
            rule.dst=htonl(rule.dst);
            insert_rule(&rule_struct, rule);
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
    rule_t rule;
    
    struct iphdr *iph;
    struct tcphdr *tcph;
    struct udphdr *udph;

    char *data;
    uint16_t port;
    unsigned char buffer[MAX_PACKET_SIZE];
   
    int buffer_len;

    if (!skb)
        return NF_ACCEPT;

    memset(&rule, 0, sizeof(rule_t));

    // packet parsing

    uint8_t mask = 32;

    iph = ip_hdr(skb);
    memcpy(&rule.src, &iph->saddr, sizeof(rule.src));
    memcpy(&rule.src_bm, &mask, 1);
    memcpy(&rule.dst, &iph->daddr, sizeof(rule.dst));
    memcpy(&rule.dst_bm, &mask, 1);

    if(iph->protocol == IPPROTO_TCP){

        tcph = tcp_hdr(skb);
        memcpy(&rule.sport, &tcph->source, sizeof(rule.sport));
        memcpy(&rule.dport, &tcph->dest, sizeof(rule.dport));

        data = (char *)((unsigned char *)tcph + (tcph->doff * 4));

        port = ntohs(tcph->dest); 

    }
    else if(iph->protocol == IPPROTO_UDP){

        // the udp code has not been tested

        udph = udp_hdr(skb);
        memcpy(&rule.sport, &udph->source, sizeof(rule.sport));
        memcpy(&rule.dport, &udph->dest, sizeof(rule.dport));

        //data = (char *)((unsigned char *)iph + sizeof(*iph));
        data = (char *)((unsigned char *)udph + sizeof(*udph));

        port = ntohs(udph->dest);

    }
    else{
        printk(KERN_INFO "Unknown ip/transport layer protocol\n");
        return NF_ACCEPT; // other ip/transport layer protocol
    }

    memset(buffer, 0, buffer_len);

    rule_to_buffer(&rule, buffer); // length will always be 12 : 2 int ips (8 bytes) + 2 short ports (4 bytes)

    buffer_len = parse_packet(data, port, buffer);

    if(buffer_len>0){ // if publish message 

        print_rule(rule);
        
        // match the rule
        if (!match_rule(&rule_struct, rule)) 
        {
            printk(KERN_INFO "firewall: forbidden packet!\n");
            return NF_DROP;
        }

        // send buffer to userspace

        //netlink_send_msg(buffer, buffer_len);
    }
    else if(!buffer_len){ // tcp/udp packet but not related to known iot protocol
        buffer_len = 0; // for compilation
    }
    else if(buffer_len==-2){ // tcp/udp packet related to known iot protocol but not a publish
        buffer_len = -2; // for compilation
    }

    // if buffer_len==0, then not a publish message so accept it

    return NF_ACCEPT;
}

static int __init init(void)
{   
    // get time 

    daily_time_t now;

    memset(&now, 0, sizeof(daily_time_t));

	set_current_time(&now.hour, &now.minute);

    printk(KERN_INFO "time %d:%d\n", now.hour, now.minute);

    // check if time constraint functions work

    time_constraint_t time_c;
    memset(&time_c, 0, sizeof(time_constraint_t));
    create_time_constraint(&time_c, 20, 30, 21, 30);
    print_time_constraint(time_c);

    int result = time_check(&time_c);
    printk(KERN_INFO "time_check : %d\n", result);

    // search for firewall process (TO BE REMOVED)
    
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