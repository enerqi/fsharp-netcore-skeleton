"""Netcore Skeleton.

Usage:
    fsharp-netcore-skeleton <project_name> (--console [--watcher] | --classlib) [--force] [--nogit]

Options:
    --console   make an executable type project.
    --classlib  make a library type project.
    --watcher   add a dotnet watcher to run the test and executable on code change. Console applications only.
    --force     try to run this skeleton script even though the project directory already exists. May fail horribly.
    --nogit     do not git init and git add
"""

from docopt import docopt
import os
from os.path import join
import shutil
from subprocess import check_output
import sys
import xml.dom.minidom as minidom

arguments = docopt(__doc__)

# Inputs
project_name = arguments['<project_name>']
is_classlib = arguments['--classlib']
watcher = arguments['--watcher']
run_git = not arguments['--nogit']
test_project_name = project_name + "Test"
pwd = os.getcwd()
project_dir = join(pwd, project_name)
dir_already_existed = os.path.exists(project_dir)
script_dir = os.path.dirname(os.path.realpath(__file__))
src_fsproj = "{}.fsproj".format(project_name)
test_fsproj = "{}.fsproj".format(test_project_name)

if dir_already_existed and not arguments['--force']:
    print("Project directory already exists - remove and try again")
    sys.exit(1)


# OS Utils
def mkdir(directory):
    try:
        os.mkdir(directory)
    except OSError:
        pass


def touch(file_path):
    open(file_path, 'a').close()


def nuke_tree(directory):
    if sys.platform.startswith("win"):
        print(check_output(["rmdir /S /Q", directory], shell=True))
    else:
        shutil.rmtree(directory)


# Project setup
def copy_file_to_project(template_file_name, new_project_relative_path):
    shutil.copyfile(join(script_dir, "resources", template_file_name),
                    join(project_dir, new_project_relative_path))


def touch_project_file(file_name):
    touch(join(project_dir, file_name))


def update_fsproj_target_framework(fsproj_path, new_version="netcoreapp2.0"):
    fsproj_xml = open(fsproj_path).read()
    fsproj_xml = fsproj_xml.replace("netcoreapp1.1", new_version)  # works for now
    open(fsproj_path, "w").write(fsproj_xml)


def run_cmd(cmd):
    output = str(check_output(cmd, shell=True), 'utf-8')
    print(output)
    return output


def add_src_fsproj_package_reference(package_name):
    run_cmd("dotnet add src/{} package {}".format(src_fsproj, package_name))


def add_test_fsproj_package_reference(package_name):
    run_cmd("dotnet add test/{} package {}".format(test_fsproj, package_name))


def add_test_run_msbuild_watch_target():
    # If a classlib then the fake serverTests target just runs the tests and exits the process
    # (Ionide) already has a way to watch the source tree for changes and re-run the tests with Expecto
    # However, if a console application we may want to have a watch process that runs the tests and re-runs
    # the application - if it is a server process for example.

    fsproj_dom = minidom.parse("test/{}".format(test_fsproj))
    project_node = fsproj_dom.firstChild
    assert project_node.nodeName == 'Project'
    target = fsproj_dom.createElement("Target")
    target.setAttribute("Name", "TestAndRun")
    execRunServerTest = fsproj_dom.createElement("Exec")
    execRunServerTest.setAttribute("Command", "dotnet run")
    execRunServerTest.setAttribute("WorkingDirectory", "./")
    target.appendChild(execRunServerTest)
    if watcher:
        execRunServerExecutable = fsproj_dom.createElement("Exec")
        execRunServerExecutable.setAttribute("Command", "dotnet run")
        execRunServerExecutable.setAttribute("WorkingDirectory", "../src/")
        target.appendChild(execRunServerExecutable)
    project_node.appendChild(target)

    new_dom_text = fsproj_dom.toprettyxml()
    open("test/{}".format(test_fsproj), "w").write(new_dom_text)

    if not watcher:
        # Remove RunWatch action
        build_fsx = open("build.fsx").read()
        build_fsx = build_fsx.replace('"RunServerTests" ==> "RunWatch"', "")
        open("build.fsx", "w").write(build_fsx)


def patch_expecto_template():
    # Deal with `dotnet restore` failing with wildcards in version numbers (presumably a bug)
    fsproj_dom = minidom.parse("test/{}".format(test_fsproj))
    project_node = fsproj_dom.firstChild
    refs = project_node.getElementsByTagName("PackageReference")
    for package_ref in (r for r in refs if r.hasAttribute("Include")):
        package_name = package_ref.getAttribute("Include")
        if "Expecto" == package_name:
            package_ref.setAttribute("Version", "5.0.1")
            break

    # Update dotnet watcher version
    cli_refs = project_node.getElementsByTagName("DotNetCliToolReference")
    for cli_ref in (cr for cr in cli_refs if cr.hasAttribute("Include")):
        tool_name = cli_ref.getAttribute("Include")
        if "Microsoft.DotNet.Watcher.Tools" == tool_name:
            cli_ref.setAttribute("Version", "2.0.0")

    new_dom_text = fsproj_dom.toprettyxml()
    open("test/{}".format(test_fsproj), "w").write(new_dom_text)


def make_project():
    mkdir(project_dir)
    os.chdir(project_dir)

    project_template = "classlib" if is_classlib else "console"
    run_cmd('dotnet new {} --language "F#" --output src --name {}'.format(project_template, project_name))
    if "expecto" not in run_cmd("dotnet new -l"):
        run_cmd("dotnet new -i 'Expecto.Template::*'")
    run_cmd("dotnet new expecto --output test --name {}".format(test_project_name))
    run_cmd("dotnet new sln")
    run_cmd("dotnet sln add src/" + src_fsproj)
    run_cmd("dotnet sln add test/" + test_fsproj)

    update_fsproj_target_framework(join("test", test_fsproj))
    run_cmd("dotnet add test/{} reference src/{}".format(test_fsproj, src_fsproj))

    patch_expecto_template()

    mkdir(join(project_dir, ".paket"))
    copy_file_to_project("paket.bootstrapper.exe", ".paket/paket.exe")
    copy_file_to_project("paket.dependencies", "paket.dependencies")
    copy_file_to_project("src-paket-references", "src/paket.references")
    copy_file_to_project("test-paket-references", "test/paket.references")
    copy_file_to_project("NuGet.config", "NuGet.config")

    add_src_fsproj_package_reference("Chessie")
    add_test_fsproj_package_reference("Chessie")
    add_test_fsproj_package_reference("FsCheck")

    copy_file_to_project("build.sh", "build.sh")
    os.chmod("build.sh", 0o775)
    copy_file_to_project("build.cmd", "build.cmd")
    copy_file_to_project("build.fsx", "build.fsx")
    add_test_run_msbuild_watch_target()

    copy_file_to_project("fsharp-gitattributes", ".gitattributes")
    copy_file_to_project("fsharp-gitignore", ".gitignore")
    copy_file_to_project("LICENSE", "LICENSE")
    touch_project_file("README.md")
    open(join(project_dir, "README.md"), "w").write("# " + project_name)

    os.chmod(".paket/paket.exe", 0o775)
    run_cmd(".paket{sep}paket.exe install".format(sep=os.path.sep))
    run_cmd(".paket{sep}paket.exe auto-restore on".format(sep=os.path.sep))

    if run_git:
        run_cmd("git init")
        run_cmd('git add "*"')

    # OPTIONAL
    # - lint in fake (though done by the Ionide 'IDE' plugin) https://github.com/fsprojects/FSharpLint/blob/master/docs/content/FAKE-Task.md
    #   Lint via FAKE only seems to work with .net framework currently
    #   Lint via FAKE through CLI ok but need PATH install of FSharpLint.exe which must be manually built
    # - documentation/releases/nuget packaging/continuous integration
    # - fxcop https://fake.build/todo-fxcop.html - seems WINDOWs only. Gendarme is the mono equivalent.
    # - coverage with dotCover (jetbrains) http://fake.build/apidocs/fake-dotcover.html etc.
    #   All commercial, except OpenCover which is also Windows only.
    # - source code formatting - only project rider or visual studio currently. Future Ionide feature.


try:
    make_project()
finally:
    os.chdir(pwd)
