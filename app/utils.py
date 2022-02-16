"""Utility functions."""
from pathlib import Path
import datetime
from openapi_core import create_spec
from openapi_core.contrib.flask import FlaskOpenAPIRequest
from openapi_core.validation.request.validators import RequestValidator
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename
import pandas as pd
import numpy as np
from kytos.core import log
from kytos.core.events import KytosEvent

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def get_timestamp():
    """Function to obtain the current time_stamp in a specific format"""
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def emit_event(controller, name, **kwargs):
    """Send an event when something happens with an EVC."""
    event_name = f"kytos/mef_eline.{name}"
    event = KytosEvent(name=event_name, content=kwargs)
    controller.buffers.app.put(event)


def compare_endpoint_trace(endpoint, vlan, trace):
    """Compare and endpoint with a trace step."""
    return (
        endpoint.switch.dpid == trace["dpid"]
        and endpoint.port_number == trace["port"]
        and vlan == trace["vlan"]
    )


def diff_pd(current_params, initial_params):
    """Identify differences between two pandas DataFrames"""
    log.info("############### diff_pd ###############")
    log.info("##### current_df #####")
    log.info(current_params)
    log.info("##### initial_df #####")
    log.info(initial_params)
    current_dict = [v for (k, v) in current_params.items()]
    current_df = pd.json_normalize(current_dict)
    initial_dict = [v for (k, v) in initial_params.items()]
    initial_df = pd.json_normalize(initial_dict)

    assert (current_df.columns == initial_df.columns).all(), \
        "DataFrame column names are different"
    if any(current_df.dtypes != initial_df.dtypes):
        # Data Types are different, trying to convert
        initial_df = initial_df.astype(current_df.dtypes)
    if current_df.equals(initial_df):
        return {"message:": "No changes"}
    # need to account for np.nan != np.nan returning True
    diff_mask = (current_df != initial_df) & \
        ~(current_df.isnull() & initial_df.isnull())
    ne_stacked = diff_mask.stack()
    changed = ne_stacked[ne_stacked]
    log.info("#################### changed ####################")
    log.info(changed)
    changed.index.names = ['id', 'col']
    difference_locations = np.where(diff_mask)
    changed_from = current_df.values[difference_locations]
    log.info("#################### changed from  ####################")
    log.info(changed_from)
    changed_to = initial_df.values[difference_locations]
    log.info("#################### changed to  ####################")
    log.info(changed_to)
    log.info("############### end of diff_pd ###############")
    # pd_result = pd.DataFrame({'from': changed_from, 'to': changed_to},
    #                       index=changed.index)
    return {'index': changed.index, 'from': changed_from, 'to': changed_to}


def load_spec():
    """Validate openapi spec."""
    napp_dir = Path(__file__).parent
    yml_file = napp_dir / "validator.yml"
    spec_dict, _ = read_from_filename(yml_file)

    validate_spec(spec_dict)

    return create_spec(spec_dict)


def validate_request(spec, data_request):
    """Decorator to validate a REST endpoint input.

    Uses the schema defined in the openapi.yml file
    to validate.
    """
    validator = RequestValidator(spec)
    openapi_request = FlaskOpenAPIRequest(data_request)
    result = validator.validate(openapi_request)
    if result.errors:
        errors = result.errors[0]
        if hasattr(errors, "schema_errors"):
            schema_errors = errors.schema_errors[0]
            error_response = {
                "error_message": schema_errors.message,
                "error_validator": schema_errors.validator,
                "error_validator_value": schema_errors.validator_value,
                "error_path": list(schema_errors.path),
                "error_schema": schema_errors.schema,
                "error_schema_path": list(schema_errors.schema_path),
                }
        else:
            error_response = {"errors": errors}
        return {"data": error_response, "code": 400}
    return {"data": data_request.json, "code": 200}
