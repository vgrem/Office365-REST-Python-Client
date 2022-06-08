from office365.runtime.client_value import ClientValue


class SocialActorInfo(ClientValue):

    @property
    def entity_type_name(self):
        return "SP.Social.SocialActorInfo"
