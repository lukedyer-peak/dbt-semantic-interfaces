from typing import List, Tuple

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

from dbt_semantic_interfaces.parsing.schema_validator import SchemaValidator

TRANSFORM_OBJECT_NAME_PATTERN = "(?!.*__).*^[a-z][a-z0-9_]*[a-z0-9]$"


# Enums
metric_types_enum_values = ["SIMPLE", "RATIO", "CUMULATIVE", "DERIVED"]
metric_types_enum_values += [x.lower() for x in metric_types_enum_values]

entity_type_enum_values = ["PRIMARY", "UNIQUE", "FOREIGN", "NATURAL"]
entity_type_enum_values += [x.lower() for x in entity_type_enum_values]

aggregation_type_values = [
    "SUM",
    "MIN",
    "MAX",
    "AVERAGE",
    "COUNT_DISTINCT",
    "SUM_BOOLEAN",
    "COUNT",
    "PERCENTILE",
    "MEDIAN",
]
aggregation_type_values += [x.lower() for x in aggregation_type_values]

window_aggregation_type_values = ["MIN", "MAX"]
window_aggregation_type_values += [x.lower() for x in window_aggregation_type_values]

time_granularity_values = ["DAY", "WEEK", "MONTH", "QUARTER", "YEAR"]
time_granularity_values += [x.lower() for x in time_granularity_values]

dimension_type_values = ["CATEGORICAL", "TIME"]
dimension_type_values += [x.lower() for x in dimension_type_values]

time_dimension_type_values = ["TIME", "time"]

metric_input_measure_schema = {
    "$id": "metric_input_measure_schema",
    "oneOf": [
        {"type": "string"},
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "filter": {"type": "string"},
                "alias": {"type": "string"},
                "join_to_timespine": {"type": "boolean"},
                "fill_nulls_with": {"type": "integer"},
            },
            "additionalProperties": False,
        },
    ],
}

metric_input_schema = {
    "$id": "metric_input_schema",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "filter": {"type": "string"},
        "alias": {"type": "string"},
        "offset_window": {"type": "string"},
        "offset_to_grain": {"type": "string"},
    },
    "additionalProperties": False,
}

metric_type_params_schema = {
    "$id": "metric_type_params",
    "type": "object",
    "properties": {
        "numerator": {"$ref": "metric_input_measure_schema"},
        "denominator": {"$ref": "metric_input_measure_schema"},
        "measure": {"$ref": "metric_input_measure_schema"},
        "expr": {"type": ["string", "boolean"]},
        "window": {"type": "string"},
        "grain_to_date": {"type": "string"},
        "metrics": {
            "type": "array",
            "items": {"$ref": "metric_input_schema"},
        },
    },
    "additionalProperties": False,
}

entity_schema = {
    "$id": "entity_schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": TRANSFORM_OBJECT_NAME_PATTERN,
        },
        "type": {"enum": entity_type_enum_values},
        "role": {"type": "string"},
        "expr": {"type": ["string", "boolean"]},
        "entity": {"type": "string"},
        "label": {"type": "string"},
    },
    "additionalProperties": False,
    "required": ["name", "type"],
}

validity_params_schema = {
    "$id": "validity_params_schema",
    "type": "object",
    "properties": {
        "is_start": {"type": "boolean"},
        "is_end": {"type": "boolean"},
    },
    "additionalProperties": False,
}

dimension_type_params_schema = {
    "$id": "dimension_type_params_schema",
    "type": "object",
    "properties": {
        "time_granularity": {"enum": time_granularity_values},
        "validity_params": {"$ref": "validity_params_schema"},
    },
    "additionalProperties": False,
    "required": ["time_granularity"],
}

non_additive_dimension_schema = {
    "$id": "non_additive_dimension_schema",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "window_choice": {"enum": window_aggregation_type_values},
        "window_groupings": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "additionalProperties": False,
    "required": ["name"],
}

aggregation_type_params_schema = {
    "$id": "aggregation_type_params_schema",
    "type": "object",
    "properties": {
        "percentile": {"type": "number"},
        "use_discrete_percentile": {"type": "boolean"},
        "use_approximate_percentile": {"type": "boolean"},
    },
    "additionalProperties": False,
}

measure_schema = {
    "$id": "measure_schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": TRANSFORM_OBJECT_NAME_PATTERN,
        },
        "agg": {"enum": aggregation_type_values},
        "agg_time_dimension": {
            "type": "string",
            "pattern": TRANSFORM_OBJECT_NAME_PATTERN,
        },
        "expr": {"type": ["string", "integer", "boolean"]},
        "agg_params": {"$ref": "aggregation_type_params_schema"},
        "create_metric": {"type": "boolean"},
        "create_metric_display_name": {"type": "string"},
        "non_additive_dimension": {
            "$ref": "non_additive_dimension_schema",
        },
        "description": {"type": "string"},
        "label": {"type": "string"},
    },
    "additionalProperties": False,
    "required": ["name", "agg"],
}

dimension_schema = {
    "$id": "dimension_schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": TRANSFORM_OBJECT_NAME_PATTERN,
        },
        "description": {"type": "string"},
        "type": {"enum": dimension_type_values},
        "is_partition": {"type": "boolean"},
        "expr": {"type": ["string", "boolean"]},
        "type_params": {"$ref": "dimension_type_params_schema"},
        "label": {"type": "string"},
    },
    # dimension must have type_params if its a time dimension
    "anyOf": [{"not": {"$ref": "#/definitions/is-time-dimension"}}, {"required": ["type_params"]}],
    "definitions": {
        "is-time-dimension": {
            "properties": {"type": {"enum": time_dimension_type_values}},
            "required": ["type"],
        },
    },
    "additionalProperties": False,
    "required": ["name", "type"],
}

# Top level object schemas
metric_schema = {
    "$id": "metric_schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": TRANSFORM_OBJECT_NAME_PATTERN,
        },
        "type": {"enum": metric_types_enum_values},
        "type_params": {"$ref": "metric_type_params"},
        "filter": {"type": "string"},
        "description": {"type": "string"},
        "label": {"type": "string"},
    },
    "additionalProperties": False,
    "required": ["name", "type", "type_params"],
}

node_relation_schema = {
    "$id": "node_relation_schema",
    "type": "object",
    "properties": {
        "alias": {"type": "string"},
        "schema_name": {"type": "string"},
        "database": {"type": "string"},
        "relation_name": {"type": "string"},
    },
    "additionalProperties": False,
    "required": ["alias", "schema_name"],
}


semantic_model_defaults_schema = {
    "$id": "semantic_model_defaults_schema",
    "type": "object",
    "properties": {
        "agg_time_dimension": {"type": "string"},
    },
    "additionalProperties": False,
    "required": [],
}


time_spine_table_configuration_schema = {
    "$id": "time_spine_table_configuration_schema",
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "column_name": {"type": "string"},
        "grain": {"enum": time_granularity_values},
    },
    "additionalProperties": False,
    "required": ["location", "column_name", "grain"],
}


project_configuration_schema = {
    "$id": "project_configuration_schema",
    "type": "object",
    "properties": {
        "time_spine_table_configurations": {
            "type": "array",
            "items": {"$ref": "time_spine_table_configuration_schema"},
        },
    },
    "additionalProperties": False,
    "required": ["time_spine_table_configurations"],
}


saved_query_schema = {
    "$id": "saved_query_schema",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "metrics": {
            "type": "array",
            "items": {"type": "string"},
        },
        "group_bys": {
            "type": "array",
            "items": {"type": "string"},
        },
        "where": {
            "type": "array",
            "items": {"type": "string"},
        },
        "label": {"type": "string"},
    },
    "required": ["name", "metrics"],
    "additionalProperties": False,
}

semantic_model_schema = {
    "$id": "semantic_model_schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": TRANSFORM_OBJECT_NAME_PATTERN,
        },
        "node_relation": {"$ref": "node_relation_schema"},
        "defaults": {"$ref": "semantic_model_defaults_schema"},
        "primary_entity": {
            "type": "string",
        },
        "entities": {"type": "array", "items": {"$ref": "entity_schema"}},
        "measures": {"type": "array", "items": {"$ref": "measure_schema"}},
        "dimensions": {"type": "array", "items": {"$ref": "dimension_schema"}},
        "description": {"type": "string"},
        "label": {"type": "string"},
    },
    "additionalProperties": False,
    "required": ["name"],
}


schema_store = {
    # Top level schemas
    metric_schema["$id"]: metric_schema,
    semantic_model_schema["$id"]: semantic_model_schema,
    project_configuration_schema["$id"]: project_configuration_schema,
    saved_query_schema["$id"]: saved_query_schema,
    # Sub-object schemas
    metric_input_measure_schema["$id"]: metric_input_measure_schema,
    metric_type_params_schema["$id"]: metric_type_params_schema,
    entity_schema["$id"]: entity_schema,
    measure_schema["$id"]: measure_schema,
    dimension_schema["$id"]: dimension_schema,
    validity_params_schema["$id"]: validity_params_schema,
    dimension_type_params_schema["$id"]: dimension_type_params_schema,
    aggregation_type_params_schema["$id"]: aggregation_type_params_schema,
    non_additive_dimension_schema["$id"]: non_additive_dimension_schema,
    metric_input_schema["$id"]: metric_input_schema,
    node_relation_schema["$id"]: node_relation_schema,
    semantic_model_defaults_schema["$id"]: semantic_model_defaults_schema,
    time_spine_table_configuration_schema["$id"]: time_spine_table_configuration_schema,
}

resources: List[Tuple[str, Resource]] = [(str(k), DRAFT7.create_resource(v)) for k, v in schema_store.items()]
registry: Registry = Registry().with_resources(resources)
semantic_model_validator = SchemaValidator(semantic_model_schema, registry=registry)
metric_validator = SchemaValidator(metric_schema, registry=registry)
project_configuration_validator = SchemaValidator(project_configuration_schema, registry=registry)
saved_query_validator = SchemaValidator(saved_query_schema, registry=registry)
