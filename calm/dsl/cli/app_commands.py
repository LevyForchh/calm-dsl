import click

from calm.dsl.api import get_api_client

from .main import main, get, describe, delete, run, watch, download
from .utils import Display, FeatureFlagGroup
from .apps import (
    get_apps,
    describe_app,
    run_actions,
    watch_action,
    watch_app,
    delete_app,
    download_runlog,
)
from calm.dsl.tools import get_logging_handle

LOG = get_logging_handle(__name__)


@get.command("apps")
@click.option("--name", "-n", default=None, help="Search for apps by name")
@click.option(
    "--filter", "filter_by", "-f", default=None, help="Filter apps by this string"
)
@click.option("--limit", "-l", default=20, help="Number of results to return")
@click.option(
    "--offset", "-o", default=0, help="Offset results by the specified amount"
)
@click.option(
    "--quiet", "-q", is_flag=True, default=False, help="Show only application names"
)
@click.option(
    "--all-items", "-a", is_flag=True, help="Get all items, including deleted ones"
)
def _get_apps(name, filter_by, limit, offset, quiet, all_items):
    """Get Apps, optionally filtered by a string"""
    get_apps(name, filter_by, limit, offset, quiet, all_items)


@describe.command("app")
@click.argument("app_name")
@click.option(
    "--out",
    "-o",
    "out",
    type=click.Choice(["text", "json"]),
    default="text",
    help="output format [json|yaml].",
)
def _describe_app(app_name, out):
    """Describe an app"""
    describe_app(app_name, out)


@run.command("action")
@click.argument("action_name")
@click.option(
    "--app",
    "app_name",
    "-a",
    default=None,
    required=True,
    help="Watch action run in an app",
)
@click.option("--watch/--no-watch", "-w", default=False, help="Watch scrolling output")
def _run_actions(app_name, action_name, watch):
    """App lcm actions"""
    render_actions = display_with_screen(app_name, action_name, watch)
    Display.wrapper(render_actions, watch)


def display_with_screen(app_name, action_name, watch):
    def render_actions(screen):
        screen.clear()
        screen.print_at(
            "Running action {} for app {}".format(action_name, app_name), 0, 0
        )
        screen.refresh()
        run_actions(screen, app_name, action_name, watch)
        screen.wait_for_input(10.0)

    return render_actions


@watch.command("action_runlog")
@click.argument("runlog_uuid")
@click.option(
    "--app",
    "app_name",
    "-a",
    default=None,
    required=True,
    help="Watch action run in an app",
)
@click.option(
    "--poll-interval",
    "poll_interval",
    "-p",
    type=int,
    default=10,
    show_default=True,
    help="Give polling interval",
)
def _watch_action_runlog(runlog_uuid, app_name, poll_interval):
    """Watch an app"""

    def display_action(screen):
        watch_action(runlog_uuid, app_name, get_api_client(), screen, poll_interval)
        screen.wait_for_input(10.0)

    Display.wrapper(display_action, watch=True)
    LOG.info("Action run {} completed for app {}".format(runlog_uuid, app_name))


@watch.command("app")
@click.argument("app_name")
@click.option(
    "--poll-interval",
    "poll_interval",
    "-p",
    type=int,
    default=10,
    show_default=True,
    help="Give polling interval",
)
def _watch_app(app_name, poll_interval):
    """Watch an app"""

    def display_action(screen):
        watch_app(app_name, screen)
        screen.wait_for_input(10.0)

    Display.wrapper(display_action, watch=True)
    LOG.info("Action runs completed for app {}".format(app_name))


@download.command("action_runlog")
@click.argument("runlog_uuid")
@click.option(
    "--app", "app_name", "-a", required=True, help="App the action belongs to"
)
@click.option("--file", "file_name", "-f", help="How to name the downloaded file")
def _download_runlog(runlog_uuid, app_name, file_name):
    """Download runlogs, given runlog uuid and app name"""
    download_runlog(runlog_uuid, app_name, file_name)


@delete.command("app")
@click.argument("app_names", nargs=-1)
@click.option("--soft", "-s", is_flag=True, default=False, help="Soft delete app")
def _delete_app(app_names, soft):
    """Deletes an application"""

    delete_app(app_names, soft)


@main.group(cls=FeatureFlagGroup)
def start():
    """Start entities"""
    pass


@main.group(cls=FeatureFlagGroup)
def stop():
    """Stop entities"""
    pass


@main.group(cls=FeatureFlagGroup)
def restart():
    """Restart entities"""
    pass


@start.command("app")
@click.argument("app_name")
@click.option("--watch/--no-watch", "-w", default=False, help="Watch scrolling output")
def start_app(app_name, watch):
    """Starts an application"""

    render_actions = display_with_screen(app_name, "start", watch)
    Display.wrapper(render_actions, watch)


@stop.command("app")
@click.argument("app_name")
@click.option("--watch/--no-watch", "-w", default=False, help="Watch scrolling output")
def stop_app(app_name, watch):
    """Stops an application"""

    render_actions = display_with_screen(app_name, "stop", watch)
    Display.wrapper(render_actions, watch)


@restart.command("app")
@click.argument("app_name")
@click.option("--watch/--no-watch", "-w", default=False, help="Watch scrolling output")
def restart_app(app_name, watch):
    """Restarts an application"""

    render_actions = display_with_screen(app_name, "restart", watch)
    Display.wrapper(render_actions, watch)
