from typing import Union
from pydantic import BaseModel, Field


class ScopeCollection(BaseModel):
    scopes: dict[str, "ScopeDefinition"] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> "ScopeDefinition":
        return self.scopes[key]

    def __setitem__(self, key: str, value: "ScopeDefinition"):
        self.scopes[key] = value

    def get(self, scope: str) -> Union["ScopeDefinition", None]:
        if not "." in scope:
            return self.scopes.get(scope)
        head, rest = scope.split(".", maxsplit=1)
        if not head in self.scopes.keys():
            return None

        return self.scopes[head].collection.get(rest)

    def serialize(self) -> dict:
        return {k: v.serialize() for k, v in self.scopes.items()}


def collection(*scopes: list["ScopeDefinition"]) -> ScopeCollection:
    return ScopeCollection(scopes={s.name: s for s in scopes})


class ScopeDefinition(BaseModel):
    name: str
    friendly_name: str
    description: str
    children: Union[ScopeCollection, None] = None

    @property
    def collection(self) -> ScopeCollection:
        if not self.children:
            self.children = collection()

        return self.children

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "friendly_name": self.friendly_name,
            "description": self.description,
            "children": self.collection.serialize(),
        }


APPLICATION_SCOPES = collection(
    ScopeDefinition(
        name="root",
        friendly_name="Root User",
        description="Bypasses all scoping. Applied only to root user. Root users cannot be deleted.",
    ),
    ScopeDefinition(
        name="app",
        friendly_name="Application User",
        description="Root scope, all users other than root have this scope applied automatically. All logged-in actions require this scope, including logging in itself. Removing it disables an account without deleting it.",
        children=collection(
            ScopeDefinition(
                name="user",
                friendly_name="Normal User",
                description="Places the account into USER mode. Given to each non-root account by default.",
            ),
            ScopeDefinition(
                name="kiosk",
                friendly_name="Kiosk User",
                description="Places the account into KIOSK mode.",
            ),
            ScopeDefinition(
                name="plugins",
                friendly_name="Plugins Access",
                description="Access to all plugins & plugin features.",
            ),
        ),
    ),
    ScopeDefinition(
        name="users",
        friendly_name="User Administration",
        description="User viewing & management root.",
        children=collection(
            ScopeDefinition(
                name="view",
                friendly_name="View Users",
                description="View all user details.",
            ),
            ScopeDefinition(
                name="manage",
                friendly_name="Manage Users",
                description="Manage user settings.",
                children=collection(
                    ScopeDefinition(
                        name="create",
                        friendly_name="User Creation",
                        description="Create new users.",
                    ),
                    ScopeDefinition(
                        name="edit",
                        friendly_name="User Editing",
                        description="Edit existing users & scopes (allows disabling users).",
                    ),
                    ScopeDefinition(
                        name="delete",
                        friendly_name="Delete Users",
                        description="Allows the deletion of existing users.",
                    ),
                ),
            ),
        ),
    ),
    ScopeDefinition(
        name="plugins",
        friendly_name="Plugin Administration",
        description="Plugin viewing & management root.",
        children=collection(
            ScopeDefinition(
                name="view",
                friendly_name="View Plugin Info",
                description="View detailed plugin information & settings",
            ),
            ScopeDefinition(
                name="manage",
                friendly_name="Manage Plugins",
                description="Manage plugin settings.",
                children=collection(
                    ScopeDefinition(
                        name="settings",
                        friendly_name="Plugin Settings",
                        description="Allows modification of plugin configs.",
                    ),
                    ScopeDefinition(
                        name="active",
                        friendly_name="Plugin Toggle",
                        description="Allows setting plugins to active or inactive.",
                    ),
                ),
            ),
        ),
    ),
    ScopeDefinition(
        name="server",
        friendly_name="Server Settings",
        description="Manage internal server settings.",
        children=collection(
            ScopeDefinition(
                name="view",
                friendly_name="View Settings",
                description="Allows viewing settings, but not modification.",
            ),
            ScopeDefinition(
                name="manage",
                friendly_name="Manage Server",
                description="Manage server settings.",
                children=collection(
                    ScopeDefinition(
                        name="zones",
                        friendly_name="Zone Management",
                        description="Allows management of household zones.",
                    ),
                    ScopeDefinition(
                        name="colors",
                        friendly_name="Color Scheme",
                        description="Allows setting the default app color scheme for all users.",
                    ),
                ),
            ),
        ),
    ),
)
