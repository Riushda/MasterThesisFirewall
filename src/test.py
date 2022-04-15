from nft.nftables_api import NftablesAPI

nf_api = NftablesAPI()
nf_api.init_ruleset()
nf_api.add_rule("192.168.1.1", 22, "192.168.1.2", 22, 0, False)
nf_api.add_rule("fe80::5054:ff:fe50:fd0e", 22, "fe80::5054:ff:fe50:fd0e", 22, 0, True)
