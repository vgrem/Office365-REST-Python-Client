from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.onedrive.lists.list import List
from tests import create_unique_name


def clean_up(columns):
    """
    :type columns: list[office365.onedrive.columns.definition.ColumnDefinition]
    """
    [column.delete_object().execute_query() for column in columns]


client = GraphClient(acquire_token_by_username_password)
lib = client.sites.root.lists["Docs"]
column_name = create_unique_name("TextColumn")
text_column = lib.columns.add_text(column_name).execute_query()
print(text_column.display_name)

clean_up([text_column])
