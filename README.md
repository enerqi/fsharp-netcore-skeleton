# FSharp Netcore Skeleton
Utility for creating an F# solution/workspace using dotnet core 2.0 with:
- [Expecto](https://github.com/haf/expecto) tests
- [Paket](https://fsprojects.github.io/Paket/) for dependency management
- [FAKE](https://fake.build/) for builds.

Multi project setup:
- Creates a solution
- Creates a library (classlib) or executable (console).
- If it's a console application then we can enable the FAKE build task `RunWatch` to watch the file system for changes and build/run tests/executable on each source file change - just do `build.cmd RunWatch`.
- Automatically runs the first `paket install` to get the initial dependencies
- Runs `git init` and adds all the files

Simple setup (`--single-project` or `--no-build`):
- No solution
- The single project setup creates a a library (classlib) or executable (console) project, but NO test project.
- The single project setup uses Paket for dependencies and Fake for builds.
- The `--no-build` option is a single project without Fake builds, but still using Paket.

For anything simpler, for example, no project, no fake and perhaps just paket to fetch some depedencies, you
might as well just use `paket` or the `dotnet` cli directly along with `.fsx` interactive file(s).

## Usage
- Requires [python 3](https://www.python.org/).
- Requires [dotnet sdk](https://www.microsoft.com/net/download/)

```bash
# Create solution 'FooProject' in a subfolder of the working directory
python3 fsharp-netcore-skeleton.py FooProject --console --watcher

# Create a solution 'FooProject' in a specific directory
python3 fsharp-netcore-skeleton.py ~/dev/FooProject --console --watcher

# Create a solution 'FooProject' in a specific directory and overwrite files as needed
python3 fsharp-netcore-skeleton.py ~/dev/FooProject --classlib --force

# Create a single project 'FooProject' with no solution and don't initialise git
python3 fsharp-netcore-skeleton.py ~/dev/FooProject --console --single-project --nogit
```

The options are documented through [DocOpt](http://docopt.org).

## Prior to First Generated Build Script Run
The `build.fsx` file should then be tweaked: `project`, `summary` and maybe `dotnetcliVersion` before running `build.cmd`.

`build.cmd` runs the `All` build targets (everything except `RunWatch`) doing a full rebuild. The sample Expecto tests have some initially failing examples that need fixing for the build to be green. Note, if wanting to only watch and re-run tests everytime the source changes (and not run an executable), then the VSCode Ionide plugin can do that.

## Alternatives
[Project Scaffold](https://github.com/fsprojects/ProjectScaffold) is currently a better alternative if using the non-crossplatform .net framework. This skeleton is single project + test project only.

[Forge](http://forge.run/) may do some or all of the work of this skeleton, but it is currently also not dotnet core.

[SAFE-Stack bookstore](https://github.com/SAFE-Stack/SAFE-BookStore) project is a good example of a combined client/server project similar to this skeleton using the Fable F# to JS compiler for the frontend.

