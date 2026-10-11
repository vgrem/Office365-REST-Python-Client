from enum import Enum


class SecurityNetworkProtocol(Enum):
    unknown = "-1"
    ip = "0"
    icmp = "1"
    igmp = "2"
    ggp = "3"
    ipv4 = "4"
    tcp = "6"
    pup = "12"
    udp = "17"
    idp = "22"
    ipv6 = "41"
    ipv6RoutingHeader = "43"
    ipv6FragmentHeader = "44"
    ipSecEncapsulatingSecurityPayload = "50"
    ipSecAuthenticationHeader = "51"
    icmpV6 = "58"
    ipv6NoNextHeader = "59"
    ipv6DestinationOptions = "60"
    nd = "77"
    raw = "255"
    ipx = "1000"
    spx = "1256"
    spxII = "1257"
    unknownFutureValue = "32767"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SecurityNetworkProtocol"
