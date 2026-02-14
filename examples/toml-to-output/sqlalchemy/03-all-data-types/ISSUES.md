# Issues Found in SQLAlchemy Data Type Conversion

## Summary

The conversion from TOML to SQLAlchemy completed successfully, but the generated code has several data type mapping issues that prevent it from being used correctly.

## Issues Identified

### 1. Reserved Attribute Name (Critical)
- **Column**: `metadata`
- **Issue**: `metadata` is a reserved attribute in SQLAlchemy's declarative base
- **Impact**: The model cannot be instantiated - raises `InvalidRequestError`
- **Suggested Fix**: Rename to `metadata_` or `meta_data` in the conversion tool

### 2. Incorrect Integer Type Mappings
- **Column**: `big_number` (TOML type: `bigint`)
  - **Current**: `Column(Integer, ...)`
  - **Expected**: `Column(BigInteger, ...)`
  - **Impact**: May cause data overflow for large numbers

- **Column**: `small_number` (TOML type: `smallint`)
  - **Current**: `Column(Integer, ...)`
  - **Expected**: `Column(SmallInteger, ...)`
  - **Impact**: Inefficient storage, doesn't match schema intent

- **Column**: `tiny_number` (TOML type: `tinyint`)
  - **Current**: `Column(Integer, ...)`
  - **Expected**: `Column(SmallInteger, ...)` or custom type
  - **Impact**: Inefficient storage

### 3. Incorrect DateTime Type Mappings
- **Column**: `created_at` (TOML type: `datetime`)
  - **Current**: `Column(Date, ...)`
  - **Expected**: `Column(DateTime, ...)`
  - **Impact**: Loses time information, only stores date

- **Column**: `updated_at` (TOML type: `timestamp`)
  - **Current**: `Column(Time, ...)`
  - **Expected**: `Column(DateTime, ...)` or `Column(TIMESTAMP, ...)`
  - **Impact**: Loses date information, only stores time

### 4. Missing Imports
- `BigInteger` is not imported from `sqlalchemy`
- `SmallInteger` is not imported from `sqlalchemy`

## Verification Command

```bash
uv run python verify_sqlalchemy_types.py
```

## Next Steps

These issues indicate bugs in the `er-convert` tool's SQLAlchemy output generator. The tool needs to be fixed to:

1. Handle reserved SQLAlchemy attribute names (metadata, query, etc.)
2. Correctly map integer size types (bigint → BigInteger, smallint → SmallInteger)
3. Correctly map datetime types (datetime → DateTime, timestamp → DateTime/TIMESTAMP)
4. Import all necessary SQLAlchemy types

## Task Status

Task 4.3 has been executed and the conversion command ran successfully, but the output has correctness issues that need to be addressed in the conversion tool itself.
