# Twitter Friend of Friend
**List of Followed Accounts on Twitter Retrieval Tool**

I created this script to help visualize which Twitter accounts (_target accounts_) are being followed by a provided list of accounts (_source accounts_). 

Use cases of the script could include e.g. visualizing the graph of your friends on Twitter. 

Another use case might be getting data about which accounts are influencing accounts known for being affected by and sharing malicious content on Twitter (such as disinformation).

It is possible to visualize the output data with [Gephi](https://gephi.org/) later.

This project was largely inspired by [How to download and visualize your Twitter network](https://towardsdatascience.com/how-to-download-and-visualize-your-twitter-network-f009dbbf107b) by Steve Hedden.

It is however adapted to use the TwitterAPI package instead of Tweepy.

This script uses Twitter API v2.

## Installation

### Install virtual environment (Optional)
```
python3 -m venv virtualenv

source virtualenv/bin/activate
```

### Get prerequisites
```
pip install -r requirements.txt
```

### Provide TwitterAPI authentication
Rename the `.env.sample` file to `.env` and provide needed API authentication values inside that file.

## How to use

To retrieve the list of followed accounts, run
```
python main.py SOURCE_FILE
```
where `SOURCE_FILE` is a file with a line-separated list of twitter user ids which you would like to analyze.

To help visualize the data, the script retrieves Twitter @username for all provided IDs.

This adds to the time needed to run the script, so you might provide usernames after each ID (separated by a comma, without the @) if you know them.

You do not have to provide Twitter @username for all records, mix and match is allowed.

**Source file example**
```
10001
10002,someTwitterUser
10003,anotherTwitterUser
...
```

Twitter v2 limits the retrieval of followed account's list to 15 requests per 15 minutes.
To account for this, the script sleeps for 16 minutes after each 15 requests performed.
Additionally, only 1000 followed accounts can be retrieved at once.

Therefore, expect long execution times for longer lists of Twitter users.

Data retrieved from Twitter API will be stored as `output/result.csv` in the following format.
```csv
source,target
someTwitterUser,SomeTwitterNewsOutlet
someTwitterUser,OtherTwitterUserThisUserIsFollowing
...
```

Additionaly, a version of the sourcefile with missing usernames added to it will be saved as `output/source_accounts.csv`

## Optional flags

- Use `--usernames-only` flag to only retrieve usernames for your follower list.

## Visualizing data with Gephi

I am only a beginner with Gephi, however I will share some of the steps I learned to be useful for visualizing the results in Gephi.

First, import the result csv file as Edge table, with edge type set as `Directed`.

Second, switch to the Data Laboratory tab, and under `Copy data to another column` select the column `Id` and ask Gephi to copy its contents to column `Label`. This will allow us to display Twitter usernames in the graph.

![Screen Shot 2023-02-28 at 17 35 46](https://user-images.githubusercontent.com/10202752/221928398-bb23b4ea-50f9-4212-974e-709c05fc9b94.png)

Switch back to the Overview tab. If you have too many data points, you might want to filter out accounts with a small number of connections. I use the `Topology/K-core` filter. 

![Screen Shot 2023-02-28 at 17 37 43](https://user-images.githubusercontent.com/10202752/221928454-d2064d03-f96b-4c1f-b9c3-59c0e703aab9.png)

Next we will need to generate Out-Degree to separate our initial user lists from the users who weren't in the original list and we retrieved them with this script. Switch the Filters tab over to the Statistics tab and next to `Degree` press the Run button.

![Screen Shot 2023-02-28 at 17 55 39](https://user-images.githubusercontent.com/10202752/221928492-c1c75dc9-cf18-4742-9dbe-a133e951c7cc.png)

Now we can use the value of Out-Degree to visually separate data under the Appearance tab. I selected a green color for nodes with Out-Degree equal to 0 (the accounts which we got from Twitter API)

![Screen Shot 2023-02-28 at 18 20 05](https://user-images.githubusercontent.com/10202752/221929045-8101fa60-1a2a-4b08-8d64-9564136f3adf.png)

We can also play with other values such as make the size of each node reflect it's In-Degree value (acocunts followed by more people will have larger circles).

Finally, run the Force Atlas 2 layout algorithm to make the data more readable. 

Depending on your data, the result could look something like this. (Actual Twitter usernames have been obfuscated into hashes)

Gephi helps us view data in an interactive way. We can for example highlight a target account and see all the source accounts which are following it.

![Screen Shot 2023-02-28 at 18 01 27](https://user-images.githubusercontent.com/10202752/221928626-59974d4d-7f77-4ca3-b45e-1e2f54d99ce9.png)

## Visualizing data without Gephi

If you wish to visualize the results without the help of Gephi (e.g. with python libraries such as `matplotlib`), you may refer to the Steve Hadden [article](https://towardsdatascience.com/how-to-download-and-visualize-your-twitter-network-f009dbbf107b) linked above.
