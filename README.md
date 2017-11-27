
# FSharp Netcore Skeleton

Utility for creating an F# project using dotnet core 2.0 with:
- [Expecto](https://github.com/haf/expecto) tests
- [Paket](https://fsprojects.github.io/Paket/) for dependency management
- [FAKE](https://fake.build/) for builds.

What this does:
- Creates a library (classlib) or executable (console).
- If it's a console application then we can enable the FAKE build task `RunWatch` to watch the file system for changes and build/run tests/executable on each source file change - just do `build.cmd RunWatch`.
- Automatically runs the first `paket install` to get the initial dependencies
- Runs `git init` and adds all the files

The `build.fsx` file should then be tweaked: `project`, `summary` and maybe `dotnetcliVersion` before running `build.cmd`.

`build.cmd` runs the `All` build targets (everything except `RunWatch`). The sample Expecto tests have some initially failing examples that need fixing for the build to be green. Note, if wanting to only watch and re-run tests everytime the source changes (and not run an executable), then the VSCode Ionide plugin can do that.

[Project Scaffold](https://github.com/fsprojects/ProjectScaffold) is currently a better alternative if using the non-crossplatform .net framework. This skeleton is single project + test project only.

[Forge](http://forge.run/) may do some or all of the work of this skeleton, but it is currently also not dotnet core.

[Fable-Suave](https://github.com/fable-compiler/fable-suave-scaffold) is a good example of a combined client/server
project similar to this skeleton.

## Usage

- Requires [python 3](https://www.python.org/).
- Requires [dotnet sdk](https://www.microsoft.com/net/download/)

```bash
cd /path/to/project/parent/
python /path/to/fsharp-netcore-skeleton.py FooProject --console --watcher
```

The options are documented through [DocOpt](http://docopt.org).
