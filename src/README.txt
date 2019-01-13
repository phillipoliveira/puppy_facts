To add an Instagram account, enter the following command: (Replace <> with your text)
add-user <instatag> fact-type <fact_type>
Note: only 'puppy_fact', 'cat_fact' and 'horse_fact' are valid fact types.

To only scrape Instagram media that contains a particular hashtag:
add-user <instatag> hashtag <hashtag> fact-type <fact_type>

To see existing user data:
view-users

To manually update a user's Instagram images, enter the following command:
update-user <instatag>

To remove an Instagram account, enter the following command:
remove-user <instatag>

To migrate facts from the src/models/fact folder:
migrate-facts

To add an email address to spam with daily facts:
add-email <email-address>

To remove a user that hates daily facts:
remove-email <email-address>

To add a slack channel to spam with daily facts:
add-slack <slack-channel-id>

To remove channel that hates facts:
remove-slack <slack-channel-id>

To view all emails and slack channels being used:
view-distributors

To print all slack channels available to you:
print-slack-channels

To print all slack groups available to you:
print-slack-groups

To exit the app, enter "exit"