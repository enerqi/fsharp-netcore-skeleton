// --------------------------------------------------------------------------------------
// FAKE build script
// --------------------------------------------------------------------------------------

#r @"packages/build/FAKE/tools/FakeLib.dll"
#I @"packages/build/FSharpLint.Fake/tools"
#r @"packages/build/FSharpLint.Fake/tools/FSharpLint.Fake.dll"

open Fake
open Fake.Git
open Fake.AssemblyInfoFile
open Fake.ReleaseNotesHelper
open FSharpLint.Fake
open System
open System.IO
open Fake.Testing.Expecto


let project = "Netcore sample"

let summary = "Netcore server side example"

let description = summary

let configuration = "Release"

let serverPath = "./src/" |> FullName

let serverTestsPath = "./test" |> FullName

let dotnetcliVersion = "2.0.3"

let mutable dotnetExePath = "dotnet"

let deployDir = "./deploy"

let dockerUser = "enerqi"
let dockerImageName = "netcore"

// --------------------------------------------------------------------------------------
// END TODO: The rest of the file includes standard build steps
// --------------------------------------------------------------------------------------


let run' timeout cmd args dir =
    if execProcess (fun info ->
        info.FileName <- cmd
        if not (String.IsNullOrWhiteSpace dir) then
            info.WorkingDirectory <- dir
        info.Arguments <- args
    ) timeout |> not then
        failwithf "Error while running '%s' with args: %s" cmd args

let run = run' System.TimeSpan.MaxValue

let runDotnet workingDir args =
    let result =
        ExecProcess (fun info ->
            info.FileName <- dotnetExePath
            info.WorkingDirectory <- workingDir
            info.Arguments <- args) TimeSpan.MaxValue
    if result <> 0 then failwithf "dotnet %s failed" args

let platformTool tool winTool =
    let tool = if isUnix then tool else winTool
    tool
    |> ProcessHelper.tryFindFileOnPath
    |> function Some t -> t | _ -> failwithf "%s not found" tool

do if not isWindows then
    // We have to set the FrameworkPathOverride so that dotnet sdk invocations know
    // where to look for full-framework base class libraries
    let mono = platformTool "mono" "mono"
    let frameworkPath = IO.Path.GetDirectoryName(mono) </> ".." </> "lib" </> "mono" </> "4.5"
    setEnvironVar "FrameworkPathOverride" frameworkPath


// --------------------------------------------------------------------------------------
// Clean build results

Target "Clean" (fun _ ->
    !!"src/**/bin"
    ++ "test/**/bin"
    |> CleanDirs

    !! "src/**/obj/*.nuspec"
    ++ "test/**/obj/*.nuspec"
    |> DeleteFiles

    CleanDirs ["bin"; "temp"; "docs/output"; deployDir]
)

Target "InstallDotNetCore" (fun _ ->
    dotnetExePath <- DotNetCli.InstallDotNetSDK dotnetcliVersion
)

// --------------------------------------------------------------------------------------
// Build library & test project

Target "InstallServer" (fun _ ->
    runDotnet serverPath "restore"
)

Target "BuildServer" (fun _ ->
    runDotnet serverPath "build"
)

Target "InstallServerTests" (fun _ ->
    runDotnet serverTestsPath "restore"
)

Target "BuildServerTests" (fun _ ->
    runDotnet serverPath "build"
)

Target "RunServerTests" (fun _ ->
    runDotnet serverTestsPath "run"
)

Target "Lint" (fun _ ->
    !! "src/**/*.fsproj"
        |> Seq.iter (FSharpLint id)
)


// Executables only
Target "RunWatch" (fun _ ->
    let unitTestsWatch = async {
        let result =
            ExecProcess (fun info ->
                info.FileName <- dotnetExePath
                info.WorkingDirectory <- serverTestsPath
                info.Arguments <- "watch msbuild /t:TestAndRun") TimeSpan.MaxValue

        if result <> 0 then failwith "Website shut down." }

    Async.Parallel [| unitTestsWatch |]
    |> Async.RunSynchronously
    |> ignore
)

FinalTarget "KillProcess" (fun _ ->
    killProcess "dotnet"
    killProcess "dotnet.exe"
)

// -------------------------------------------------------------------------------------
Target "Build" DoNothing
Target "All" DoNothing

"Clean"
  ==> "InstallDotNetCore"
  ==> "InstallServer"
  ==> "InstallServerTests"
  ==> "BuildServer"
  ==> "BuildServerTests"
  ==> "RunServerTests"
  ==> "All"

"RunServerTests" ==> "RunWatch"

RunTargetOrDefault "All"
