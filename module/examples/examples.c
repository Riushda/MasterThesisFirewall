/*
struct rule *match;
    unsigned char buffer[12];

    match = (struct rule *)kmalloc(sizeof(struct rule), GFP_KERNEL);
    memset(match, 0, sizeof(struct rule));

    match->src = in_aton("192.168.1.15");
    match->dst = in_aton("192.168.1.4");
    match->sport = ntohs(5353);
    match->dport = ntohs(56342);

    rule_to_buffer(match, buffer);
    insert_item(buffer, table, TABLE_SIZE);
    kfree(match);
    */