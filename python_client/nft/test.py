import nftables_api


def main():
    api = nftables_api.NftablesAPI()

    api.init_ruleset()
    handle = api.add_rule(src="192.168.0.1/24", sport=80,
                          dst="192.168.2.55/18", dport=22)

    # api.disable_rule(handle)
    # api.enable_rule(handle)
    # api.list_ruleset()
    api.del_rule(handle)
    # api.flush_ruleset()


if __name__ == "__main__":
    main()
