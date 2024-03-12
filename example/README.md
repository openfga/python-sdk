## Examples of using the OpenFGA Python SDK

A set of examples on how to call the OpenFGA Python SDK

### Examples

Example 1:
A bare-bones example. It creates a store, and runs a set of calls against it including creating a model, writing tuples and checking for access.

### Running the Examples

Prerequisites:

- `docker`
- `make`
- `python` 3.11+

#### Run using a published SDK

Steps:

1. Clone/Copy the example folder
2. If you have an OpenFGA server running, you can use it, otherwise run `make run-openfga` to spin up an instance (you'll need to switch to a different terminal after - don't forget to close it when done)
3. Run `make run` to run the example

#### Run using a local unpublished SDK build

Steps:

1. Build the SDK
2. Change to the example directory
3. Install the local SDK `pip install -e $LOCAL_DIR`
   - For example, if your local SDK is located at `$HOME/projects/python-sdk`, run `pip install -e $HOME/projects/python-sdk`
   - For advanced users: The above just updates `requirements.txt` and the source of openfga-sdk. If you know how to manually edit this, feel free to do that as well.
4. If you have an OpenFGA server running, you can use it, otherwise run `make run-openfga` to spin up an instance (you'll need to switch to a different terminal after - don't forget to close it when done)
5. Run `make run` to run the example
