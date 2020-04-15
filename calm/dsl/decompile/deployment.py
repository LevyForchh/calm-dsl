from calm.dsl.decompile.render import render_template
from calm.dsl.builtins import DeploymentType
from calm.dsl.decompile.ref import render_ref_template
from calm.dsl.decompile.ref_dependency import update_deployment_name
from calm.dsl.tools import get_logging_handle

LOG = get_logging_handle(__name__)


def render_deployment_template(cls):

    LOG.debug("Rendering {} deployment template".format(cls.__name__))
    if not isinstance(cls, DeploymentType):
        raise TypeError("{} is not of type {}".format(cls, DeploymentType))

    # Entity context
    entity_context = "Deployment_" + cls.__name__

    user_attrs = cls.get_user_attrs()
    user_attrs["name"] = cls.__name__
    user_attrs["description"] = cls.__doc__ or "{} Deployment description".format(
        cls.__name__
    )

    gui_display_name = cls.get_name()

    # updating ui and dsl name mapping
    update_deployment_name(gui_display_name, cls.__name__)

    depends_on_list = []
    for entity in user_attrs.get("dependencies", []):
        depends_on_list.append(render_ref_template(entity))

    if cls.substrate:
        user_attrs["substrate"] = render_ref_template(cls.substrate)

    package_list = []
    for entity in user_attrs.get("packages", []):
        package_list.append(render_ref_template(entity))

    user_attrs["packages"] = ", ".join(package_list)
    user_attrs["dependencies"] = ",".join(depends_on_list)

    text = render_template("deployment.py.jinja2", obj=user_attrs)
    return text.strip()
