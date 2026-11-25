param([switch]$Release)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$game = Join-Path $root "..\Mindustry-master\desktop\build\libs\Mindustry.jar"
if(-not (Test-Path $game)){
    throw "missing game jar: $game (build Mindustry desktop first)"
}

$stageName = if($Release){ "stage-release" } else { "stage" }
$stage = Join-Path $root "build\$stageName"
Remove-Item -Recurse -Force $stage -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$sources = Get-ChildItem -Recurse -Filter *.java (Join-Path $root "src") | ForEach-Object { $_.FullName }
& javac -encoding UTF-8 --release 17 -cp $game -d $stage $sources
if($LASTEXITCODE -ne 0){ throw "javac failed" }

$metaMode = if($Release){ "--release" } else { "--dev" }
& python (Join-Path $root "tools\meta.py") $metaMode (Join-Path $stage "mod.hjson")
if($LASTEXITCODE -ne 0){ throw "meta generation failed" }

Copy-Item (Join-Path $root "bundle_cns.properties") $stage

$jarName = if($Release){ "ChineseRedstone.jar" } else { "ChineseRedstone-dev.jar" }
$jar = Join-Path $root "build\$jarName"
Remove-Item $jar -ErrorAction SilentlyContinue

# javapath usually only shims java/javac; locate jar.exe in the real JDK
$jarTool = $null
if($env:JAVA_HOME){
    $candidate = Join-Path $env:JAVA_HOME "bin\jar.exe"
    if(Test-Path $candidate){ $jarTool = $candidate }
}
if(-not $jarTool){
    $line = (& java -XshowSettings:properties -version 2>&1 | Select-String "java.home =").ToString()
    $home = ($line -split "=", 2)[1].Trim()
    $candidate = Join-Path $home "bin\jar.exe"
    if(Test-Path $candidate){ $jarTool = $candidate }
}
if(-not $jarTool){ throw "jar tool not found" }

if($Release){
    # Android loads classes.dex from the jar root, desktop loads .class files
    & python (Join-Path $root "tools\dex.py") $stage
    if($LASTEXITCODE -ne 0){ throw "dex failed" }
}

& $jarTool --create --file $jar -C $stage .
if($LASTEXITCODE -ne 0){ throw "jar failed" }

# The install target lives under a CJK path; Python handles it safely
if($Release){
    & python (Join-Path $root "tools\install.py") "--release"
}else{
    & python (Join-Path $root "tools\install.py") "--dev"
}
if($LASTEXITCODE -ne 0){ throw "install failed" }
