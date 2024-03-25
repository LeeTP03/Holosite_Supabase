Backend for the HoloArc website

Queries data for each Individual Hololive member using the YouTube Data API,
Parses the queried data and then uploads it to a Supabase Database online.

Needs to run to be able to update the data on the website
Unfortunately it is quite inefficient due to the massive amounts of data that needs to be queried
The 10000 quota daily limit given by YouTube's API for a free account is not enough for a frequent enough update (hourly updates are not possible)
