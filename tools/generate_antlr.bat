@echo off
REM Generate ANTLR Python code from grammar files
REM This script generates Python lexer, parser, and visitor code from .g4 grammar files

setlocal enabledelayedexpansion

REM Set Java home to JDK 25
set "JAVA_HOME=C:\Program Files\Java\jdk-25"
set "PATH=%JAVA_HOME%\bin;%PATH%"

REM Check if Java is available
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java is not available. Please install JDK 25 or later.
    exit /b 1
)

REM Find ANTLR JAR file in tools directory
set "TOOLS_DIR=%~dp0"
set "ANTLR_JAR="
for %%f in ("%TOOLS_DIR%antlr-*.jar") do set "ANTLR_JAR=%%f"
if not exist "%ANTLR_JAR%" (
    echo ERROR: ANTLR JAR file not found. Please download antlr-4.13.2-complete.jar
    echo and place it in the tools directory.
    exit /b 1
)

REM Change to project root directory
cd /d "%~dp0.."

REM Set directories (relative to project root)
set "GRAMMAR_DIR=src\x007007007\er\parser\antlr"
set "OUTPUT_DIR=%GRAMMAR_DIR%\generated"
set "PACKAGE=x007007007.er.parser.antlr.generated"

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo Generating ANTLR code for MermaidER.g4...
java -cp "%ANTLR_JAR%" org.antlr.v4.Tool ^
    -Dlanguage=Python3 ^
    -visitor ^
    -o "%OUTPUT_DIR%" ^
    "%GRAMMAR_DIR%\MermaidER.g4"

if errorlevel 1 (
    echo ERROR: Failed to generate code for MermaidER.g4
    exit /b 1
)

echo Generating ANTLR code for PlantUMLER.g4...
java -cp "%ANTLR_JAR%" org.antlr.v4.Tool ^
    -Dlanguage=Python3 ^
    -visitor ^
    -o "%OUTPUT_DIR%" ^
    "%GRAMMAR_DIR%\PlantUMLER.g4"

if errorlevel 1 (
    echo ERROR: Failed to generate code for PlantUMLER.g4
    exit /b 1
)

echo.
echo ANTLR code generation completed successfully!
echo Generated files are in: %OUTPUT_DIR%
echo.
echo Note: You may need to adjust imports in the generated files
echo if the package structure doesn't match your project.
