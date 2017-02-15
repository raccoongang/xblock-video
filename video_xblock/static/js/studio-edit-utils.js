/**
 * Auxiliary functions for studio editor modal's JS.
 */

/**
 * Run a callback when DOM is fully loaded
 */
function domReady(callback) {
    if (document.readyState === "interactive" || document.readyState === "complete") {
        callback();
    } else {
        document.addEventListener("DOMContentLoaded", callback);
    }
}

/**
 * Prepare data to be saved to video xblock.
 */
function fillValues(fields) {
    var values = {};
    var notSet = []; // List of field names that should be set to default values
    for (var i in fields) {
        var field = fields[i];
        if (field.isSet()) {
            values[field.name] = field.val();
        } else {
            notSet.push(field.name);
        }
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        if (field.hasEditor()) {
            field.removeEditor();
        }
    }
    return {values: values, defaults: notSet};
}
