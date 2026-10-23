"""Web branding: rebase the source's paths, copy only what the target can resolve."""

from office365.migration.sharepoint.branding import (
    apply_web_branding,
    verify_web_branding,
)

SOURCE_MASTER = "/sites/team_in/_catalogs/masterpage/seattle.master"
TARGET_MASTER = "/sites/team_out/_catalogs/masterpage/seattle.master"


class _Request:
    def __init__(self) -> None:
        self.reads = 0

    def get(self) -> "_Request":
        return self

    def execute_query(self) -> "_Request":
        self.reads += 1
        return self


class _Web:
    """A web whose projected read returns whatever properties the fake holds."""

    def __init__(self, path="/sites/team_out", *, files=(), folders=(), **properties) -> None:
        self._props = {"ServerRelativeUrl": path, "Url": f"https://contoso.sharepoint.com{path}"}
        self._props.update(properties)
        self.files = set(files)
        self.folders = set(folders)
        self.written = {}
        self.updates = 0
        self.selected = None

    @property
    def properties(self):
        return self._props

    def get_property(self, name):
        return self._props.get(name)

    def select(self, names):
        self.selected = list(names)
        return self

    def get(self):
        return self

    def set_property(self, name, value):
        self.written[name] = value
        self._props[name] = value
        return self

    def update(self):
        return self

    def execute_query(self):
        self.updates += 1
        return self

    def get_file_by_server_relative_url(self, url):
        if url not in self.files:
            raise FileNotFoundError(url)
        return _Request()

    def get_folder_by_server_relative_path(self, url):
        if url not in self.folders:
            raise FileNotFoundError(url)
        return _Request()


def test_apply_rebases_the_source_paths_onto_the_target():
    source = _Web(
        "/sites/team_in",
        MasterUrl=SOURCE_MASTER,
        CustomMasterUrl=SOURCE_MASTER,
        SiteLogoUrl="/sites/team_in/SiteAssets/logo.png",
        AlternateCssUrl="https://contoso.sharepoint.com/sites/team_in/SiteAssets/brand.css",
    )
    target = _Web(files={TARGET_MASTER, "/sites/team_out/SiteAssets/logo.png", "/sites/team_out/SiteAssets/brand.css"})

    report = apply_web_branding(source, target)

    assert report.changed
    assert report.skipped == {}
    assert report.applied == {
        "AlternateCssUrl": "https://contoso.sharepoint.com/sites/team_out/SiteAssets/brand.css",
        "MasterUrl": TARGET_MASTER,
        "CustomMasterUrl": TARGET_MASTER,
        "SiteLogoUrl": "/sites/team_out/SiteAssets/logo.png",
    }
    assert target.written["MasterUrl"] == TARGET_MASTER
    assert report.summary() == (
        "branding: copied AlternateCssUrl, CustomMasterUrl, MasterUrl, SiteLogoUrl onto "
        "https://contoso.sharepoint.com/sites/team_out"
    )


def test_apply_is_idempotent():
    source = _Web("/sites/team_in", MasterUrl=SOURCE_MASTER, SiteLogoUrl="/sites/team_in/SiteAssets/logo.png")
    target = _Web(
        MasterUrl=TARGET_MASTER,
        SiteLogoUrl="/sites/team_out/SiteAssets/logo.png",
        files={TARGET_MASTER, "/sites/team_out/SiteAssets/logo.png"},
    )

    report = apply_web_branding(source, target)

    assert report.applied == {}
    assert report.summary() == ""
    assert target.updates == 1  # the capture GET, no MERGE
    assert target.written == {}


def test_verify_reports_a_divergent_property():
    source = _Web("/sites/team_in", MasterUrl=SOURCE_MASTER, AlternateCssUrl="/sites/team_in/Style%20Library/a.css")
    target = _Web(MasterUrl="/sites/team_out/_catalogs/masterpage/other.master")

    notes = verify_web_branding(source, target)

    assert notes == [
        "branding: https://contoso.sharepoint.com/sites/team_out AlternateCssUrl is None, "
        "source has '/sites/team_out/Style%20Library/a.css'",
        "branding: https://contoso.sharepoint.com/sites/team_out MasterUrl is "
        "'/sites/team_out/_catalogs/masterpage/other.master', "
        "source has '/sites/team_out/_catalogs/masterpage/seattle.master'",
    ]
