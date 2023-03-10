import os
import sys

from datetime import datetime, timedelta 

# local components
from classes.patient_api_client import PatientApiClient
from classes.options import Options


# method is unused in current project
def get_account_followers(api: PatientApiClient, account_id: int):
    return get_account_relations(api, account_id, "followers")


def get_account_following(api: PatientApiClient, account_id: int):
    return get_account_relations(api, account_id, "following")


def get_account_relations(api: PatientApiClient, account_id: int, request_type: str):
    assert (request_type in ["followers", "following"])
    follower_list = []
    next_page_token = -1
    params = dict()
    params["max_results"] = 1000
    while next_page_token is not None:
        if next_page_token != -1:
            params["pagination_token"] = next_page_token
        response_data = ""
        try:
            response = api.handle_request_json(request_type="following",
                                               request=f'users/:{account_id}/{request_type}',
                                               params=params)
            if response is None:
                return None

            next_page_token = response["meta"].get("next_token")

            for item in response["data"]:
                # we can learn this about the accounts: id, username (twitter @), name (display name)
                # follower_list.append(f"{item['username']} ({item['id']}): {item['name']}")
                # append only the handle
                follower_list.append(item['username'])

        except Exception as e:
            sys.stderr.write(f"    Error getting {request_type} list for {account_id}: {e}, log: {response}\n")
            return follower_list
    return follower_list


def get_username(api: PatientApiClient, user_id):
    print(f"\nGetting username for twitter user id: {user_id}")
    response = api.handle_request_json(request_type="username",
                                       request=f'users/:{user_id}')
    if response.get("errors"):
        print("    Could not retrieve username. Please confirm account with this id still exists.")
        return None
    username: str = response.get("data").get("username")
    print(f"    Retrieved username: {username}")
    return username


def read_source_ids_from_file(sourcefile_path: str):
    if not sourcefile_path:
        print("Please provide a filename to read source id list from!")
        return None

    if not os.path.exists(sourcefile_path):
        print(f"Specified file {sourcefile_path} does not exist.")
        return None

    with open(sourcefile_path, 'r') as f:
        source_ids = f.read().splitlines()

    return source_ids


def write_ids_with_usernames(id_username_pairs: dict):
    with open("output/source_accounts.csv", 'w+') as f:
        for user_id, username in id_username_pairs.items():
            f.write(f"{user_id},{username}\n")


def create_source_dictionary(api: PatientApiClient, source_lines: list):
    source_dict: dict = dict()

    for source_line in source_lines:
        split_line = source_line.split(',')
        if len(split_line) > 1 and split_line[1] and split_line[1].strip():
            source_dict[split_line[0]] = split_line[1]
        elif str.isnumeric(split_line[0]):
            username: str = get_username(api, split_line[0])
            if username and username.strip():
                source_dict[split_line[0]] = username

    return source_dict


def write_results_to_file(api: PatientApiClient, file_handle, user_id: int, username: str):
    print(f'\nNow getting list of followed accounts for user: {username}')
    following_list = get_account_following(api, user_id)
    if following_list:
        print(f'    Retrieved a list of {len(following_list)} followed accounts.')
        for following in following_list:
            file_handle.write(f"{username},{following}\n")
        print(f'    Appended the list of followed accounts to the output file.')


def create_output_folder_if_not_exists():
    if not os.path.exists("output/"):
        os.makedirs("output")


def estimate_running_time(source_lines: list, options: Options):
    source_id_count: int = len(source_lines)
    split_line = [x.split(',') for x in source_lines]
    username_missing_count: int = len([x for x in split_line if not len(split_line) > 1 and not split_line[1]])
    
    api_cycle_count: int = 0
    api_cycle_count += ((username_missing_count - 1) // 300)
    if not options.is_get_usernames_only:
        api_cycle_count += ((source_id_count - 1) // 15)
    
    if api_cycle_count < 1:
        print('\n\nThe procedure should only take several seconds.\n\n')
        return
    
    minute_count: int = api_cycle_count * 16
    completion_time = (datetime.now() + timedelta(minutes=minute_count)).strftime("%H:%M:%S")
    print(f'\n\nThe procedure will take at least {minute_count} minutes')
    print('    (Actual duration might be longer when analyzing accounts who follow many other accounts)')
    print(f'\nEarliest expected completion time: \n    {completion_time}\n\n')

#todo add option to only export twitter user ids, without usernames
def main():
    api: PatientApiClient = PatientApiClient()
    options: Options = Options()

    if not api.is_authenticated:
        sys.stderr.writelines("Could not authenticate TwitterAPI v2 client.\n"
                              "Please check that .env file contains correct authentication data.\n")
        return

    source_lines = read_source_ids_from_file(sourcefile_path=options.sourcefile_path)
    if source_lines is None:
        return

    estimate_running_time(source_lines, options)
    
    if options.is_estimate_only:
        return
    
    create_output_folder_if_not_exists()
    
    # get usernames for missing ids
    source_dict = create_source_dictionary(api, source_lines)

    #write id list with usernames, so that this can be reused later
    #todo: only perform if specified in command line
    write_ids_with_usernames(source_dict)
    
    if options.is_get_usernames_only:
        return
        

    with open("output/result.csv", 'w+') as f:
        f.write("source,target\n")
        for (user_id, username) in source_dict.items():
            write_results_to_file(api, f, user_id, username)


if __name__ == '__main__':
    main()
