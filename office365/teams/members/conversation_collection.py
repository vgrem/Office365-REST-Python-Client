from office365.entity_collection import EntityCollection
from office365.teams.members.conversation import ConversationMember


class ConversationMemberCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(ConversationMemberCollection, self).__init__(context, ConversationMember, resource_path)


