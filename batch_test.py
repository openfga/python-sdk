import time
from openfga_sdk.client.models import ClientCheckRequest
from openfga_sdk.models.batch_check_request import BatchCheckRequest
from openfga_sdk.models.batch_check_item import BatchCheckItem
from openfga_sdk.models import TupleKey
from openfga_sdk.sync import OpenFgaClient
from openfga_sdk import ClientConfiguration
from datetime import timedelta

configuration = ClientConfiguration(
    api_url="http://localhost:8080",
    store_id="01J8QBXT1ZT41H73TB6DW6XQNK",
)

client = OpenFgaClient(configuration)

old_check_request = ClientCheckRequest(
     user="user:justin",
     relation="can_read",
     object="doc:public-roadmap"
)

def time_old_way(num_checks):
    start = time.time()
    client.batch_check([old_check_request for _ in range(num_checks)])
    delta = timedelta(seconds=time.time() - start)
    return delta

ttu_tuple = TupleKey(
     user="user:justin",
     relation="can_read",
     object="doc:public-roadmap"
)
justin_can_read_item = BatchCheckItem(tuple_key=ttu_tuple)

def time_new_way(num_checks):
    start = time.time()
    client.justin_batch_check(
        BatchCheckRequest(checks=[justin_can_read_item for _ in range(num_checks)])
    )

    delta = timedelta(seconds=time.time() - start)
    return delta


def run_both_tests(checks_to_send, number_of_request_loops):
    old_deltas = []
    for _ in range(number_of_request_loops):
        ms = time_old_way(checks_to_send).total_seconds() * 1000
        print(f"old batch took {ms}ms")
        old_deltas.append(ms)
        time.sleep(.2)

    avg_old_delta = sum(old_deltas) / len(old_deltas)
    print(f"old delta average ms: {avg_old_delta}\n")

    new_deltas = []
    for _ in range(number_of_request_loops):
        ms = time_new_way(checks_to_send).total_seconds() * 1000
        print(f"new batch took: {ms}ms")
        new_deltas.append(ms)
        time.sleep(.2)

    avg_new_delta = sum(new_deltas) / len(new_deltas)
    print(f"new delta average ms: {avg_new_delta}")

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
    justin_check_request = BatchCheckRequest(checks=[one_check_item])

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