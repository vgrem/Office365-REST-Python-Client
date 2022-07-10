from office365.runtime.client_value import ClientValue


class PostReference(ClientValue):
    """The SocialPostReference class specifies a reference to a post in another thread.  The referenced post can be a
    post with a tag, a post that is liked, a post that mentions a user, or a post that is a reply. Threads that contain
    a SocialPostReference in the PostReference property (see section 3.1.5.42.1.1.6) are threads with root posts that
    are generated on the server and not created by a client."""
