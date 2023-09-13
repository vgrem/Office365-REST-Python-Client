from office365.directory.synchronization.schema import SynchronizationSchema
from office365.directory.synchronization.status import SynchronizationStatus
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class SynchronizationJob(Entity):
    """
    Performs synchronization by periodically running in the background, polling for changes in one directory,
    and pushing them to another directory. The synchronization job is always specific to a particular instance
    of an application in your tenant. As part of the synchronization job setup, you need to give authorization
    to read and write objects in your target directory, and customize the job's synchronization schema.
    """

    @property
    def status(self):
        """Status of the job, which includes when the job was last run, current job state, and errors."""
        return self.properties.get("status", SynchronizationStatus())

    @property
    def schema(self):
        """The synchronization schema configured for the job."""
        return self.properties.get('schema',
                                   SynchronizationSchema(self.context, ResourcePath("schema", self.resource_path)))
