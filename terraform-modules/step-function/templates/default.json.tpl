{
    "StartAt": "ListAccounts",
    "States": {
      "ListAccounts": {
        "Type": "Map",
        "Iterator": {
           "StartAt": "ScanAccounts",
           "States": {
             "ScanAccounts": {
               "Type": "Task",
               "Resource": "${lambda_arn}",
               "End": true
             }
           }
        },
        "End": true
      }
    }
  }
