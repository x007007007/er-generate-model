# SQLAlchemy Flatten Mode External Inheritance Fix Design

## Overview

When using `--inheritance-mode flatten` to convert Django models to SQLAlchemy, the system incorrectly imports and inherits from external Django model classes (like `KinkoTechModelBase`, `CreateModifyMixinModel`). This causes runtime errors because SQLAlchemy models cannot inherit from Django models. The fix involves modifying the Jinja2 templates to distinguish between internal templates (defined in the TOML file) and external classes (from external packages), and only importing/inheriting external classes in reference mode while expanding their fields in flatten mode.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when flatten mode is used with entities that have external classes in their `extends` list
- **Property (P)**: The desired behavior - external classes should not be imported or inherited in flatten mode; only the SQLAlchemy Base should be inherited
- **Preservation**: Existing behavior that must remain unchanged - reference mode should continue to import and inherit external classes; internal template handling should remain unchanged
- **External Class**: A class reference in the `extends` list that is NOT defined in the `model.templates` dictionary (e.g., `kinkotech.common.infrastructure.models.base.KinkoTechModelBase`)
- **Internal Template**: A template defined in the `model.templates` dictionary within the same TOML file
- **Inheritance Mode**: The mode controlling how inheritance is handled - `reference` (inherit from base classes) or `flatten` (expand all fields into the entity)
- **sqlalchemy_single_model.j2**: The Jinja2 template for generating single-file SQLAlchemy models
- **sqlalchemy_model.j2**: The Jinja2 template for generating multi-entity SQLAlchemy models in a single file

## Bug Details

### Fault Condition

The bug manifests when generating SQLAlchemy output AND an entity has external Django model classes in its `extends` list. The template logic incorrectly imports these external classes and adds them to the inheritance list, regardless of the inheritance mode setting. External Django classes cannot be used as base classes for SQLAlchemy models because they are incompatible ORM frameworks.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type TemplateRenderContext
  OUTPUT: boolean
  
  RETURN input.output_framework == 'sqlalchemy'
         AND input.entity.extends IS NOT EMPTY
         AND EXISTS template_name IN input.entity.extends WHERE template_name NOT IN input.model.templates
         AND (externalClassesImported(input) OR externalClassesInherited(input))
END FUNCTION
```

### Examples

- **Example 1**: Entity `Order` extends `["kinkotech.common.infrastructure.models.base.KinkoTechModelBase", "kinkotech.common.infrastructure.models.base.CreateModifyMixinModel"]` with flatten mode
  - **Current (Incorrect)**: Generates `from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel` and `class Order(KinkoTechModelBase, CreateModifyMixinModel):`
  - **Expected (Correct)**: Should generate `class Order(Base):` with all fields from external classes expanded into the entity

- **Example 2**: Entity `Order` extends same external classes with reference mode
  - **Current (Incorrect)**: Generates `from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel` and `class Order(KinkoTechModelBase, CreateModifyMixinModel):`
  - **Expected (Correct)**: Should generate `class Order(Base):` with all fields from external classes expanded into the entity (same as flatten mode for external classes)

- **Example 3**: Entity `PromotionCode` extends three external classes with flatten mode
  - **Current (Incorrect)**: Imports all three Django classes and inherits from them
  - **Expected (Correct)**: Should only inherit from `Base` and expand all fields from the three external classes

- **Example 4**: Entity with both internal and external classes in `extends` with reference mode
  - **Current (Incorrect)**: Imports external classes and adds them to inheritance list
  - **Expected (Correct)**: Should generate mixin for internal template and inherit from it, but expand fields from external classes (not inherit)

- **Edge Case**: Entity with only internal templates in `extends` with reference mode
  - **Expected**: Should continue to work as before (generate mixin files, use Python inheritance)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Reference mode must continue to import and inherit from external classes
- Internal template handling (templates defined in `model.templates`) must remain unchanged
- Entities with no external classes in `extends` must continue to work as before
- Django-to-Django conversion must continue to handle inheritance as before
- Field expansion from internal templates in flatten mode must remain unchanged

**Scope:**
All inputs that do NOT involve flatten mode with external classes should be completely unaffected by this fix. This includes:
- Reference mode with external classes (should continue to import and inherit)
- Flatten mode with only internal templates (should continue to expand fields)
- Entities with no inheritance (should continue to inherit only from Base)
- Any non-SQLAlchemy output formats

## Hypothesized Root Cause

Based on the bug description and template analysis, the root causes are:

1. **Missing Inheritance Mode Check in Import Logic**: The template sections that collect and generate external class imports do not check the `inheritance_mode` variable before adding external classes to the import list. The logic at lines 8-36 in both templates collects external imports without considering whether flatten mode is active.

2. **Missing Inheritance Mode Check in Base Class Logic**: The template sections that build the `base_classes` list (lines 38-58 in `sqlalchemy_single_model.j2` and similar in `sqlalchemy_model.j2`) add external classes to the inheritance list without checking if `inheritance_mode == 'flatten'`.

3. **Incomplete External Class Detection**: The template correctly distinguishes between internal templates (`template_name in model.templates`) and external classes, but this distinction is not used to filter out external classes in flatten mode.

4. **Field Expansion Already Works**: The field expansion logic in flatten mode already works correctly (fields from templates are marked with `_source_template` and expanded into the entity). The bug is purely in the import and inheritance sections.

## Correctness Properties

Property 1: Fault Condition - No External Inheritance in Flatten Mode

_For any_ template render context where `inheritance_mode == 'flatten'` and the entity has external classes in its `extends` list, the generated SQLAlchemy model SHALL NOT import the external classes, SHALL NOT inherit from the external classes, and SHALL only inherit from the SQLAlchemy Base class.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Reference Mode External Inheritance

_For any_ template render context where `inheritance_mode == 'reference'` and the entity has external classes in its `extends` list, the generated SQLAlchemy model SHALL continue to import the external classes and inherit from them exactly as before, preserving the existing reference mode behavior.

**Validates: Requirements 3.1, 3.2**

Property 3: Preservation - Internal Template Handling

_For any_ template render context where the entity has internal templates (defined in `model.templates`) in its `extends` list, the generated SQLAlchemy model SHALL continue to handle these internal templates according to the inheritance mode rules (reference or flatten) exactly as before, preserving the existing internal template behavior.

**Validates: Requirements 3.3**

Property 4: Preservation - No Inheritance Cases

_For any_ template render context where the entity has no classes in its `extends` list, the generated SQLAlchemy model SHALL continue to inherit only from Base exactly as before, preserving the existing no-inheritance behavior.

**Validates: Requirements 3.4**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**Files**: 
- `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_single_model.j2`
- `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_model.j2`

**Specific Changes**:

1. **Modify External Import Collection Logic**: Add inheritance mode check to prevent collecting external imports in flatten mode
   - In the section that collects `external_imports` (lines 8-36), wrap the external class collection logic with a condition: `{%- if inheritance_mode == 'reference' %}`
   - This ensures external classes are only imported when inheritance mode is reference

2. **Modify Base Class List Building Logic**: Add inheritance mode check to prevent adding external classes to base_classes in flatten mode
   - In the section that builds `base_classes` (lines 38-58), add a condition when processing external classes: only add to `base_classes` if `inheritance_mode == 'reference'`
   - This ensures external classes are only inherited when inheritance mode is reference

3. **Ensure Field Expansion Continues**: Verify that field expansion from external classes works correctly in flatten mode
   - The existing field expansion logic should already handle this (fields marked with `_source_template`)
   - No changes needed to field rendering logic

4. **Apply Same Fix to Both Templates**: Both `sqlalchemy_single_model.j2` and `sqlalchemy_model.j2` have identical inheritance logic and need the same fixes

5. **Test with Multiple Scenarios**: Verify the fix works for:
   - Entities with only external classes in `extends`
   - Entities with both internal and external classes in `extends`
   - Entities with multiple external classes from the same module
   - Entities with external classes from different modules

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that parse a TOML file with entities extending external Django classes, render the SQLAlchemy templates with `--inheritance-mode flatten`, and assert that external classes are NOT imported and NOT inherited. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Single External Class Test**: Entity extends one external Django class with flatten mode (will fail on unfixed code - external class will be imported and inherited)
2. **Multiple External Classes Test**: Entity extends multiple external Django classes with flatten mode (will fail on unfixed code - all external classes will be imported and inherited)
3. **Mixed Internal and External Test**: Entity extends both internal templates and external classes with flatten mode (will fail on unfixed code - external classes will be imported and inherited)
4. **Field Expansion Test**: Verify fields from external classes are expanded in flatten mode (may pass on unfixed code if field expansion already works)

**Expected Counterexamples**:
- Generated code contains `from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel`
- Generated code contains `class Order(KinkoTechModelBase, CreateModifyMixinModel):`
- Possible causes: missing inheritance_mode check in import logic, missing inheritance_mode check in base class logic

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed templates produce the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := renderTemplate_fixed(input)
  ASSERT NOT externalClassesImported(result)
  ASSERT NOT externalClassesInherited(result)
  ASSERT onlyInheritsFromBase(result)
  ASSERT fieldsFromExternalClassesExpanded(result)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed templates produce the same result as the original templates.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT renderTemplate_original(input) = renderTemplate_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for reference mode and no-inheritance cases, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Reference Mode Preservation**: Observe that reference mode with external classes imports and inherits correctly on unfixed code, then write test to verify this continues after fix
2. **Internal Template Preservation**: Observe that internal templates are handled correctly in both modes on unfixed code, then write test to verify this continues after fix
3. **No Inheritance Preservation**: Observe that entities with no extends work correctly on unfixed code, then write test to verify this continues after fix
4. **Django Output Preservation**: Observe that Django-to-Django conversion works correctly on unfixed code, then write test to verify this continues after fix

### Unit Tests

- Test flatten mode with single external class (should not import or inherit)
- Test flatten mode with multiple external classes (should not import or inherit any)
- Test flatten mode with mixed internal and external classes (should only handle internal classes)
- Test reference mode with external classes (should import and inherit)
- Test entities with no inheritance (should only inherit from Base)
- Test field expansion from external classes in flatten mode

### Property-Based Tests

- Generate random entity configurations with various combinations of internal templates and external classes
- Verify flatten mode never imports or inherits external classes across many scenarios
- Verify reference mode always imports and inherits external classes across many scenarios
- Verify field expansion works correctly for all inheritance configurations

### Integration Tests

- Test full conversion flow from Django TOML to SQLAlchemy with flatten mode
- Test that generated SQLAlchemy models can be imported without errors
- Test that generated SQLAlchemy models can be instantiated without runtime errors
- Test switching between reference and flatten modes produces correct output
