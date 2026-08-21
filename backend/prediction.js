// --------------------------------------------------
// PREDICTION MODULE
// --------------------------------------------------

// This module is responsible for handling the prediction
// process.
//
// At the moment, the actual machine-learning model has not
// been integrated. Therefore, this function temporarily
// returns the validated input data.
//
// Later, the ML model can be called from this module.
//
// Risk classification and alert generation are NOT handled
// here because they belong to other components of the project.


// --------------------------------------------------
// PREDICTION FUNCTION
// --------------------------------------------------

// Receives validated input data from server.js.
//
// Parameter:
// data -> object containing the input features required
//         by the prediction model
function predict(data) {

    // Temporary placeholder for the future ML model.
    //
    // Returning the input allows us to verify that the
    // data is successfully reaching the prediction module.
    const prediction = {
        input: data
    };

    return prediction;
}


// --------------------------------------------------
// EXPORT FUNCTION
// --------------------------------------------------

// Export the prediction function so that it can be
// imported and used by server.js.
module.exports = predict;