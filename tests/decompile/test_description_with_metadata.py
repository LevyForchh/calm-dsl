from calm.dsl.builtins import (
    ref,
    basic_cred,
    CalmVariable,
    CalmTask,
    action,
)
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import read_provider_spec, read_local_file

CRED_USERNAME = read_local_file(".tests/username")
CRED_PASSWORD = read_local_file(".tests/password")
DNS_SERVER = read_local_file(".tests/dns_server")


class MySQLService(Service):
    """Sample mysql service
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: my sql service
    """

    ENV = CalmVariable.Simple("DEV")


class MySQLPackage(Package):
    """Example package with variables, install tasks and link to service
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: my sql package
    """

    foo = CalmVariable.Simple("bar")
    services = [ref(MySQLService)]

    @action
    def __install__():
        CalmTask.Exec.ssh(name="Task1", script="echo @@{foo}@@")


class AHVVMforMySQL(Substrate):
    """AHV VM config given by reading a spec file
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: ahv vm for sql
    """

    provider_spec = read_provider_spec("specs/ahv_provider_spec.yaml")


class MySQLDeployment(Deployment):
    """Sample deployment pulling in service and substrate references
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: my sql deployment
    """

    packages = [ref(MySQLPackage)]
    substrate = ref(AHVVMforMySQL)


class PHPService(Service):
    """Sample PHP service with a custom action
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: php service
    """

    # Dependency to indicate PHP service is dependent on SQL service being up
    dependencies = [ref(MySQLService)]

    @action
    def test_action():

        blah = CalmVariable.Simple("2")  # noqa
        CalmTask.Exec.ssh(name="Task2", script='echo "Hello"')
        CalmTask.Exec.ssh(name="Task3", script='echo "Hello again"')


class PHPPackage(Package):
    """Example PHP package with custom install task
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: php package
    """

    foo = CalmVariable.Simple("baz")
    services = [ref(PHPService)]

    @action
    def __install__():
        CalmTask.Exec.ssh(name="Task4", script="echo @@{foo}@@")


class AHVVMforPHP(Substrate):
    """AHV VM config given by reading a spec file
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: ahv vm for php substrate
    """

    provider_spec = read_provider_spec("specs/ahv_provider_spec.yaml")


class PHPDeployment(Deployment):
    """Sample deployment pulling in service and substrate references
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: php deployment
    """

    packages = [ref(PHPPackage)]
    substrate = ref(AHVVMforPHP)


class DefaultProfile(Profile):
    """Sample application profile with variables
    
    ### Calm DSL Metadata/Hints (Do not edit/change)
    calm_dsl_metadata:
      display_name: default profile
    """

    nameserver = CalmVariable.Simple(DNS_SERVER, label="Local DNS resolver")
    foo1 = CalmVariable.Simple("bar1", runtime=True)
    foo2 = CalmVariable.Simple("bar2", runtime=True)

    deployments = [MySQLDeployment, PHPDeployment]

    @action
    def test_profile_action():
        """Sample description for a profile action
    
        ### Calm DSL Metadata/Hints (Do not edit/change)
        calm_dsl_metadata:
            display_name: sample profile action
        """
        CalmTask.Exec.ssh(name="Task5", script='echo "Hello"', target=ref(MySQLService))
        PHPService.test_action(name="Task6")


class NextDslBlueprint(Blueprint):
    """Calm DSL .NEXT demo"""

    credentials = [
        basic_cred(CRED_USERNAME, CRED_PASSWORD, default=True),
    ]
    services = [MySQLService, PHPService]
    packages = [MySQLPackage, PHPPackage]
    substrates = [AHVVMforMySQL, AHVVMforPHP]
    profiles = [DefaultProfile]
