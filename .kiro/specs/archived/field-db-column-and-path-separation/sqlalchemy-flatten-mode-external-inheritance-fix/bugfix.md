# Bugfix Requirements Document

## Introduction

When using `--inheritance-mode flatten` to convert Django models to SQLAlchemy, the generated SQLAlchemy models incorrectly inherit Django model classes (like `KinkoTechModelBase`, `CreateModifyMixinModel`, `LocationMixin`). This causes runtime errors because SQLAlchemy models cannot inherit from Django models. The flatten mode should expand all fields from external classes into the entity and only inherit from the SQLAlchemy declarative base.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN `--inheritance-mode flatten` is used AND the entity has external Django model classes in `extends` THEN the system imports the external Django model classes

1.2 WHEN `--inheritance-mode flatten` is used AND the entity has external Django model classes in `extends` THEN the system adds the external Django model classes to the inheritance list (e.g., `class POI(KinkoTechModelBase, CreateModifyMixinModel, LocationMixin)`)

1.3 WHEN `--inheritance-mode flatten` is used AND the entity has external Django model classes in `extends` THEN the system does not expand fields from the external classes into the entity definition

1.4 WHEN the generated SQLAlchemy model inherits from Django model classes THEN the system produces a runtime error because SQLAlchemy models cannot inherit from Django models

### Expected Behavior (Correct)

2.1 WHEN generating SQLAlchemy output AND the entity has external Django model classes in `extends` THEN the system SHALL NOT import the external Django model classes (regardless of inheritance mode)

2.2 WHEN generating SQLAlchemy output AND the entity has external Django model classes in `extends` THEN the system SHALL only inherit from the SQLAlchemy declarative base (e.g., `class POI(Base)`) (regardless of inheritance mode)

2.3 WHEN generating SQLAlchemy output AND the entity has external Django model classes in `extends` THEN the system SHALL expand all fields from the external classes into the entity definition (regardless of inheritance mode)

2.4 WHEN generating SQLAlchemy output AND the entity has external Django model classes in `extends` THEN the system SHALL generate valid SQLAlchemy models that can be instantiated without runtime errors

2.5 WHEN generating SQLAlchemy output AND the entity has external Django model classes in `extends` THEN the system SHALL treat external classes the same way in both reference and flatten modes (always expand fields, never inherit)

### Unchanged Behavior (Regression Prevention)

3.1 WHEN `--inheritance-mode reference` is used AND the entity has internal templates (defined in TOML) in `extends` THEN the system SHALL CONTINUE TO generate mixin files and use Python inheritance for internal templates

3.2 WHEN `--inheritance-mode flatten` is used AND the entity has internal templates (defined in TOML) in `extends` THEN the system SHALL CONTINUE TO expand fields from internal templates into the entity

3.3 WHEN the entity has no classes in `extends` THEN the system SHALL CONTINUE TO generate models as before

3.4 WHEN converting Django models to Django output format THEN the system SHALL CONTINUE TO handle inheritance as before (external classes can be inherited in Django output)
