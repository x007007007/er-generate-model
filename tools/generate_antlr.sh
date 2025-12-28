#!/bin/bash
# Generate ANTLR parser code from grammar file
# Requires Java 11+ and ANTLR 4.13.2

JAR_FILE="tools/antlr-4.13.2-complete.jar"
GRAMMAR_FILE="src/x007007007/er/parser/antlr/MermaidER.g4"
OUTPUT_DIR="src/x007007007/er/parser/antlr/generated"

# Check if Java is available
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed or not in PATH"
    exit 1
fi

# Check Java version (need 11+)
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | sed '/^1\./s///' | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 11 ]; then
    echo "Error: Java 11+ is required. Current version: $JAVA_VERSION"
    echo "Please upgrade Java or use an older ANTLR version (4.9.3 supports Java 8)"
    exit 1
fi

# Check if JAR file exists
if [ ! -f "$JAR_FILE" ]; then
    echo "Error: ANTLR JAR file not found: $JAR_FILE"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate parser code
echo "Generating ANTLR parser code..."
java -jar "$JAR_FILE" -Dlanguage=Python3 -visitor -o "$OUTPUT_DIR" "$GRAMMAR_FILE"

if [ $? -eq 0 ]; then
    echo "Successfully generated ANTLR parser code in $OUTPUT_DIR"
else
    echo "Error: Failed to generate parser code"
    exit 1
fi

