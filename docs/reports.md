# Reports

Domain protect generates the following reports.  Each report is generated and sent to the SNS topic as a JSON object, which is then picked up by the [notify lambda](../terraform-modules/lambda-slack/code/notify/notify.py) and sent to slack.

## Current Vulnerabilities (Daily)
This daily report sends a message to slack listing the currently known vulnerable domains that require fixes.

![Current vulnerabilities example](images/current.png?raw=true)

## Takeover Resources (Daily)
This daily report lists the resources that are currently being used to prevent domain takeover.  This can be useful for managing costs associated with having the resources running.

![Current resources example](images/resources-notification.png?raw=true)

## Stats (Monthly)
This monthly report runs on the first of each month and lists number of domains takeovers that have been prevented in the last month, last year and all time.

![Stats example](images/stats.png?raw=true)