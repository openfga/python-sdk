import time
from openfga_sdk.client.models import ClientCheckRequest
from openfga_sdk.models.batch_check_request import BatchCheckRequest
from openfga_sdk.models.batch_check_item import BatchCheckItem
from openfga_sdk.models import TupleKey
from openfga_sdk.sync import OpenFgaClient
from openfga_sdk import ClientConfiguration
from openfga_sdk.credentials import Credentials, CredentialConfiguration
from datetime import timedelta


# our test store in shared-fga-test
TEST_AUTH_MODEL_ID = "01J99P5J93G224G6V605P53FK4"

class BatchTester:
    def __init__(self):
        self.client = None
        self.old_check_request = ClientCheckRequest(
            user="user:justin",
            relation="can_read",
            object="doc:public-roadmap"
        )

        ttu_tuple = TupleKey(
            user="user:justin",
            relation="can_read",
            object="doc:public-roadmap"
        )
        self.new_batch_check_item = BatchCheckItem(tuple_key=ttu_tuple)

    # config for Ewan / Justin test store
    def init_client(self):
        credentials = Credentials(
            method='client_credentials',
            configuration=CredentialConfiguration(
                api_issuer= "sandcastle-dev.us.auth0.com",
                # api_audience= "https://api.staging.fga.dev/",
                api_audience="https://api.shared-fga-test-6.dev.fga.dev/",
                client_id= "xLjsFehFRG8pGr8EJodic8Zh5CJMuvI9",
                client_secret= "UGRPPyqJfrb6r5-M7UGGyvAmVvkZXVypwsKsut0JRAS1QIffZsqz7Wbb4GHzbr_G",
            )
        )

        configuration = ClientConfiguration(
            # api_url = "https://api.stage.fga.dev",
            api_url="https://api.shared-fga-test-6.dev.fga.dev",
            store_id = "01J99EC70YNERR04HX0PBQDJJG",
            authorization_model_id = TEST_AUTH_MODEL_ID, # Ewan / Justin test store
            credentials = credentials,
        )

        self.client = OpenFgaClient(configuration)


    def time_old_way(self, num_checks):
        start = time.time()
        self.client.batch_check([self.old_check_request for _ in range(num_checks)])
        delta = timedelta(seconds=time.time() - start)
        return delta


    def time_new_way(self, num_checks):
        start = time.time()
        self.client.justin_batch_check(
            BatchCheckRequest(
                checks=[self.new_batch_check_item for _ in range(num_checks)],
                authorization_model_id=TEST_AUTH_MODEL_ID,
            )
        )

        delta = timedelta(seconds=time.time() - start)
        return delta


    def run_both_tests(self, checks_to_send, number_of_request_loops=10):
        """
        will run old batch check `number_of_request_loops` times
        and print the average duration each batch took
        then do same for new batch check

        e.g. `run_both_tests(50,10)` will run a batch of 50 checks and repeat that 10 times
        for the old batch check, then 10 times for the new batch check
        """
        self.init_client()
        old_deltas = []
        for _ in range(number_of_request_loops):
            ms = self.time_old_way(checks_to_send).total_seconds() * 1000
            print(f"old batch took {ms}ms")
            old_deltas.append(ms)
            time.sleep(.2) # not strictly necessary, mostly so I can see what's happening

        avg_old_delta = sum(old_deltas) / len(old_deltas)
        print(f"old delta average ms: {avg_old_delta}\n")

        new_deltas = []
        for _ in range(number_of_request_loops):
            ms = self.time_new_way(checks_to_send).total_seconds() * 1000
            print(f"new batch took: {ms}ms")
            new_deltas.append(ms)
            time.sleep(.2)

        avg_new_delta = sum(new_deltas) / len(new_deltas)
        print(f"new delta average ms: {avg_new_delta}")


# Don't worry about anything below here ----------------------------------
def the_old_way():
    existing_check_request = ClientCheckRequest(
        user="user:charles",
        relation="member",
        object="group:fabrikam"
    )

    justin_check_request = ClientCheckRequest(
        user="user:justin",
        relation="can_read",
        object="doc:public-roadmap"
    )

    client.check(existing_check_request)
    # {'allowed': True, 'resolution': ''}

    client.batch_check([existing_check_request])

    # 100 checks in a batch
    results = client.batch_check([existing_check_request for _ in range(50)])
    # interesting so in a local test, using the old batch, even then there's no cache hit on the original batch request
    # if I follow it up manually with another one a second later, the cache hits hard

def the_new_way():
    simple_tuple = TupleKey(
        user="user:charles",
        relation="member",
        object="group:fabrikam"
    )

    charles_can_see = TupleKey(
        user="user:charles",
        relation="viewer",
        object="doc:public-roadmap"
    )
    one_check_item = BatchCheckItem(tuple_key=simple_tuple)

    # justin_check_request = BatchCheckRequest(checks=[one_check_item for _ in range(10)])
    # 01J99P5J93G224G6V605P53FK4 is ewan's test instance model
    justin_check_request = BatchCheckRequest(checks=[one_check_item], authorization_model_id="01J99P5J93G224G6V605P53FK4")

    # currently failing:
    # results = client.justin_batch_check([existing_check_request for _ in range(50)])

def nested_folders():
    """ added these tuples:
    fga tuple write folder:folder-1 parent folder:product-2021
    fga tuple write folder:folder-2 parent folder:folder-1
    fga tuple write folder:folder-3 parent folder:folder-2
    fga tuple write user:justin viewer folder:folder-3
    fga query check user:justin can_read doc:public-roadmap

    user:justin has viewer access to 3 folders above the one that matters
    for access
    """
    ttu_tuple = TupleKey(
        user="user:justin",
        relation="can_read",
        object="doc:public-roadmap"
    )
    ttu_item = BatchCheckItem(tuple_key=ttu_tuple)
    client.justin_batch_check(BatchCheckRequest(checks=[ttu_item for _ in range(10)]))
    """
    this results in a ton of queries
    at 10 checks its ~43 queries and a single cache hit
    
    on attempt 2 it was only 26 queries :thinking:
    with 0 cache hits in any query
    
    
    running 1000 simultaneous checks ran 1370 queries total
    
    100 made 212 queries
    43 total cache hits in checks
    """

"""
With the Sync client:
I tried with a batch of 50 completely identical requests, the old way, and 41 hit cache
seems like everything AFTER the first batch
next time it was 49, then 43, 46, 47
hovers between 80-95%
"""

"""
[
    {'_allowed': True,
    '_request': <openfga_sdk.client.models.check_request.ClientCheckRequest at 0x103bf2300>,
    '_response': {'allowed': True, 'resolution': ''},
    '_error': None}
]
"""

"""
check user is member of a group
is user charles a member of group fabrikam - should cache his membership

is folder product 2021 a parent of doc:public-roadmap - should cache the parent relationship

is user:charles a viewer of doc:public-roadmap

fga query check user:charles member group:fabrikam
fga query check folder:product-2021 parent doc:public-roadmap
fga query check user:charles viewer doc:public-roadmap

fga query check group:fabrikam#member viewer doc:2021-roadmap
fga query check user:charles viewer doc:public-roadmap
"""



def local_client():
    """
    local config, justin's laptop
    """
    configuration = ClientConfiguration(
        api_url="http://localhost:8080",
        store_id="01J8QBXT1ZT41H73TB6DW6XQNK",
        authorization_model_id="01J8QBXT27F1WJ4RK89M7FK1M8"
    )
    OpenFgaClient(configuration)
